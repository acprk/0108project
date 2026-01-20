"""
人脸识别核心算法模块
支持人脸检测、人脸编码和人脸比对功能
"""
import numpy as np
from typing import List, Tuple, Optional
import face_recognition
from pathlib import Path
import io
import os
from PIL import Image, ImageDraw, ImageFont
from supabase import create_client, Client
from config import settings


class FaceDetector:
    """人脸检测器类"""

    def __init__(self, model_type: str = "hog"):
        """
        初始化人脸检测器

        Args:
            model_type: 检测模型类型，'hog' 速度快但精度略低，'cnn' 精度高但需要GPU
        """
        self.model_type = model_type
        self.known_face_encodings = []
        self.known_face_names = []

    def load_known_faces(self, faces_dir: str):
        """
        从指定目录加载已知人脸数据
        
        Args:
            faces_dir: 包含人脸图片的目录路径，文件名即为人名
        """
        # 优先尝试从 Supabase 加载
        if settings.STORAGE_TYPE == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                print(f"正在从 Supabase Bucket '{settings.SUPABASE_BUCKET}' 加载人脸...")
                supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                files = supabase.storage.from_(settings.SUPABASE_BUCKET).list()
                
                count = 0
                for file in files:
                    if file['name'].lower().endswith(('.jpg', '.jpeg', '.png')):
                        print(f"加载: {file['name']}")
                        data = supabase.storage.from_(settings.SUPABASE_BUCKET).download(file['name'])
                        image_file = io.BytesIO(data)
                        image = face_recognition.load_image_file(image_file)
                        encodings = face_recognition.face_encodings(image)

                        if encodings:
                            name = Path(file['name']).stem
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_names.append(name)
                            count += 1
                print(f"从 Supabase 加载了 {count} 个人脸")
                return
            except Exception as e:
                print(f"从 Supabase 加载失败: {e}")
                # 失败后尝试本地加载

        faces_path = Path(faces_dir)
        if not faces_path.exists():
            faces_path.mkdir(parents=True)
            return

        for image_path in faces_path.glob("*.jpg"):
            # 加载图片
            image = face_recognition.load_image_file(str(image_path))
            # 获取人脸编码
            encodings = face_recognition.face_encodings(image)

            if encodings:
                # 使用文件名（去除扩展名）作为人名
                name = image_path.stem
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(name)

    def detect_faces(self, image: np.ndarray) -> Tuple[List, List]:
        """
        检测图片中的所有人脸

        Args:
            image: 输入图片（numpy array RGB格式）

        Returns:
            face_locations: 人脸位置列表 [(top, right, bottom, left), ...]
            face_names: 识别出的人名列表
        """
        # face_recognition 使用 RGB，如果你传入的是 BGR (OpenCV格式)，需要转换
        # 但我们现在改用 PIL 读取，默认就是 RGB，所以这里不需要转换了
        # 只要确保传入的 image 是 RGB 格式的 numpy array
        
        # 检测人脸位置
        face_locations = face_recognition.face_locations(image, model=self.model_type)

        # 获取人脸编码
        face_encodings = face_recognition.face_encodings(image, face_locations)

        # 识别人脸
        face_names = []
        for face_encoding in face_encodings:
            name = "Unknown"

            if self.known_face_encodings:
                # 比对人脸
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.5  # 容差值，越小越严格（从0.6优化为0.5）
                )

                # 计算人脸距离
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]

            face_names.append(name)

        return face_locations, face_names

    def draw_faces(self, image_array: np.ndarray, face_locations: List, face_names: List) -> Image.Image:
        """
        在图片上绘制人脸框和名字

        Args:
            image_array: 输入图片 (numpy array)
            face_locations: 人脸位置列表
            face_names: 人名列表

        Returns:
            绘制后的图片 (PIL Image 对象)
        """
        # 将 numpy array 转换为 PIL Image
        pil_image = Image.fromarray(image_array)
        draw = ImageDraw.Draw(pil_image)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # 绘制矩形框
            color = (0, 255, 0) if name != "Unknown" else (255, 0, 0) # Green or Red
            
            # PIL 的 rectangle 需要 [x0, y0, x1, y1]
            draw.rectangle([left, top, right, bottom], outline=color, width=3)

            # 绘制标签背景
            text_width = len(name) * 10 # 估算宽度
            text_height = 20
            draw.rectangle([left, bottom - text_height - 10, right, bottom], fill=color, outline=color)

            # 绘制文字
            # 默认字体可能不支持中文，这里为了简单使用默认字体
            # 如果需要中文支持，需要加载字体文件
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255))

        return pil_image

    def add_known_face(self, image: np.ndarray, name: str, save_path: Optional[str] = None) -> bool:
        """
        添加新的已知人脸

        Args:
            image: 人脸图片 (RGB numpy array)
            name: 人名
            save_path: 保存路径（可选）

        Returns:
            是否成功添加
        """
        encodings = face_recognition.face_encodings(image)

        if encodings:
            self.known_face_encodings.append(encodings[0])
            self.known_face_names.append(name)

            # 保存到 Supabase
            if settings.STORAGE_TYPE == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_KEY:
                try:
                    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                    
                    # 将 numpy array 转回图片字节
                    pil_image = Image.fromarray(image)
                    img_byte_arr = io.BytesIO()
                    pil_image.save(img_byte_arr, format='JPEG')
                    file_bytes = img_byte_arr.getvalue()
                    
                    file_name = f"{name}.jpg"
                    # upsert=True 覆盖同名文件
                    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
                        file_name, 
                        file_bytes, 
                        file_options={"content-type": "image/jpeg", "upsert": "true"}
                    )
                    return True
                except Exception as e:
                    print(f"上传到 Supabase 失败: {e}")
                    return False

            # 保存图片到本地
            if save_path:
                pil_image = Image.fromarray(image)
                pil_image.save(save_path)

            return True
        return False


# 全局人脸检测器实例（在应用启动时初始化）
face_detector = None

def get_face_detector() -> FaceDetector:
    """获取全局人脸检测器实例"""
    global face_detector
    if face_detector is None:
        face_detector = FaceDetector(model_type="hog")
        # 加载已知人脸（从 models 目录）
        face_detector.load_known_faces("models/known_faces")
    return face_detector
