"""
FastAPI 后端服务
提供人脸识别 Web API
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from pathlib import Path
from typing import Optional
import logging
import os

from face_detector import get_face_detector
from config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="人脸识别系统",
    description="基于 Python + OpenCV + face_recognition 的在线人脸识别系统",
    version="1.0.0"
)

# 配置 CORS（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 确保必要的目录存在 (仅在本地存储模式下或非只读环境)
if settings.STORAGE_TYPE == "local":
    try:
        Path("models/known_faces").mkdir(parents=True, exist_ok=True)
        Path("uploads").mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"无法创建本地目录 (可能在只读环境中): {e}")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化人脸检测器"""
    logger.info("正在初始化人脸检测器...")
    detector = get_face_detector()
    logger.info(f"已加载 {len(detector.known_face_names)} 个已知人脸")
    logger.info("人脸识别系统启动成功！")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    html_path = Path("templates/index.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    else:
        return """
        <html>
            <head><title>人脸识别系统</title></head>
            <body>
                <h1>人脸识别系统</h1>
                <p>模板文件未找到，请检查 templates/index.html</p>
            </body>
        </html>
        """


@app.post("/api/detect")
async def detect_faces(file: UploadFile = File(...)):
    """
    检测上传图片中的人脸

    Args:
        file: 上传的图片文件

    Returns:
        JSON 响应，包含检测结果
    """
    try:
        # 读取上传的图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")

        # 获取人脸检测器
        detector = get_face_detector()

        # 检测人脸
        face_locations, face_names = detector.detect_faces(image)

        # 绘制人脸框
        result_image = detector.draw_faces(image, face_locations, face_names)

        # 将结果图片编码为 base64
        _, buffer = cv2.imencode('.jpg', result_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # 返回结果
        return JSONResponse({
            "success": True,
            "face_count": len(face_locations),
            "faces": [
                {
                    "name": name,
                    "location": {
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "left": left
                    }
                }
                for (top, right, bottom, left), name in zip(face_locations, face_names)
            ],
            "result_image": f"data:image/jpeg;base64,{img_base64}"
        })

    except Exception as e:
        logger.error(f"检测人脸时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/api/detect_stream")
async def detect_faces_stream(image_data: str = Form(...)):
    """
    检测视频流中的人脸（接收 base64 编码的图片）

    Args:
        image_data: base64 编码的图片数据

    Returns:
        JSON 响应，包含检测结果
    """
    try:
        # 解码 base64 图片
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片数据")

        # 获取人脸检测器
        detector = get_face_detector()

        # 检测人脸
        face_locations, face_names = detector.detect_faces(image)

        # 返回结果（不返回图片，减少数据传输量）
        return JSONResponse({
            "success": True,
            "face_count": len(face_locations),
            "faces": [
                {
                    "name": name,
                    "location": {
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "left": left
                    }
                }
                for (top, right, bottom, left), name in zip(face_locations, face_names)
            ]
        })

    except Exception as e:
        logger.error(f"检测视频流时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/api/add_face")
async def add_known_face(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    添加新的已知人脸

    Args:
        name: 人名
        file: 人脸图片

    Returns:
        JSON 响应
    """
    try:
        # 读取上传的图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="无法读取图片")

        # 获取人脸检测器
        detector = get_face_detector()

        # 保存路径
        save_path = None
        if settings.STORAGE_TYPE == "local":
            save_path = f"models/known_faces/{name}.jpg"

        # 添加人脸
        success = detector.add_known_face(image, name, save_path)

        if success:
            return JSONResponse({
                "success": True,
                "message": f"成功添加人脸: {name}",
                "total_known_faces": len(detector.known_face_names)
            })
        else:
            raise HTTPException(status_code=400, detail="图片中未检测到人脸")

    except Exception as e:
        logger.error(f"添加人脸时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/api/known_faces")
async def get_known_faces():
    """
    获取所有已知人脸列表

    Returns:
        JSON 响应，包含已知人脸名称列表
    """
    try:
        detector = get_face_detector()
        return JSONResponse({
            "success": True,
            "known_faces": detector.known_face_names,
            "total": len(detector.known_face_names)
        })
    except Exception as e:
        logger.error(f"获取已知人脸列表时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    detector = get_face_detector()
    return {
        "status": "healthy",
        "known_faces_count": len(detector.known_face_names)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
