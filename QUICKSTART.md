# 快速启动指南

## 方式一：使用启动脚本（推荐）

```bash
cd 0108project
./run.sh
```

启动脚本会自动：
- 检查 Python 环境
- 创建并激活虚拟环境
- 安装所有依赖
- 启动服务

## 方式二：手动启动

### 1. 安装依赖

```bash
cd 0108project

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:8000

## 第一次使用

1. **添加已知人脸**
   - 点击"人脸管理"标签
   - 输入姓名并上传清晰的人脸照片
   - 点击"添加人脸"

2. **开始识别**
   - 点击"实时识别"标签
   - 点击"启动摄像头"
   - 允许浏览器访问摄像头
   - 系统会自动识别画面中的人脸

## 常用命令

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（支持热重载）
uvicorn main:app --reload

# 启动生产服务器
uvicorn main:app --host 0.0.0.0 --port 8000

# 停止服务
按 Ctrl+C
```

## 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 获取已知人脸列表
curl http://localhost:8000/api/known_faces

# 上传图片检测（需要有图片文件）
curl -X POST -F "file=@test.jpg" http://localhost:8000/api/detect
```

## 故障排除

### dlib 安装失败

```bash
# Ubuntu/Debian
sudo apt-get install cmake build-essential

# 然后重新安装
pip install dlib
```

### 端口已被占用

```bash
# 更改端口（编辑 main.py 最后一行）
uvicorn.run(app, host="0.0.0.0", port=8080)  # 改为 8080
```

### 摄像头无法访问

- 确保使用 Chrome/Firefox 等现代浏览器
- 检查浏览器摄像头权限
- 如果是远程访问，必须使用 HTTPS

## 下一步

详细文档请查看 [README.md](README.md)
