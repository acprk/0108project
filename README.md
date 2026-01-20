# AI 人脸识别系统

基于 Python + OpenCV + face_recognition 的在线人脸识别 Web 应用。

## 功能特性

- **实时识别**：通过摄像头实时检测和识别人脸
- **图片上传**：上传图片进行人脸识别
- **人脸管理**：添加和管理已知人脸数据库
- **现代化界面**：响应式设计，支持移动端访问

## 项目结构

```
0108project/
├── main.py                 # FastAPI 后端服务
├── face_detector.py        # 人脸识别核心算法
├── requirements.txt        # Python 依赖
├── README.md              # 项目说明
├── templates/             # HTML 模板
│   └── index.html
├── static/                # 静态资源
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── models/                # 模型和数据
│   └── known_faces/       # 已知人脸图片（姓名.jpg）
└── uploads/               # 临时上传文件
```

## 安装步骤

### 1. 系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip
sudo apt-get install -y cmake build-essential
sudo apt-get install -y libopencv-dev
```

**macOS:**
```bash
brew install cmake
brew install opencv
```

**Windows:**
- 安装 Visual Studio Build Tools
- 下载并安装 CMake

### 2. 创建虚拟环境

```bash
cd 0108project
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**注意**：如果 `dlib` 安装失败，可以尝试：

```bash
# 方法 1：使用预编译版本
pip install dlib --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 方法 2：使用 conda（推荐）
conda install -c conda-forge dlib
```

## 快速开始

### 1. 启动服务

```bash
python main.py
```

或使用 uvicorn：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问应用

打开浏览器访问：`http://localhost:8000`

### 3. 添加已知人脸

**方法一：通过 Web 界面**
1. 点击"人脸管理"标签页
2. 输入姓名并上传人脸照片
3. 点击"添加人脸"

**方法二：手动添加**
1. 将人脸照片命名为 `姓名.jpg`（如 `张三.jpg`）
2. 放入 `models/known_faces/` 目录
3. 重启服务

## 使用说明

### 实时识别

1. 点击"实时识别"标签页
2. 点击"启动摄像头"按钮
3. 允许浏览器访问摄像头
4. 系统会自动检测并识别画面中的人脸

### 图片上传

1. 点击"图片上传"标签页
2. 点击上传区域或拖拽图片
3. 等待识别结果

### 人脸管理

1. 点击"人脸管理"标签页
2. 添加新人脸或查看已有人脸列表

## API 接口

### 健康检查
```
GET /health
```

### 检测图片中的人脸
```
POST /api/detect
Content-Type: multipart/form-data

file: 图片文件
```

### 检测视频流中的人脸
```
POST /api/detect_stream
Content-Type: application/x-www-form-urlencoded

image_data: base64 编码的图片
```

### 添加已知人脸
```
POST /api/add_face
Content-Type: multipart/form-data

name: 姓名
file: 人脸图片
```

### 获取已知人脸列表
```
GET /api/known_faces
```

## 技术栈

- **后端**: FastAPI, Python 3.8+
- **人脸识别**: face_recognition, OpenCV, dlib
- **前端**: HTML5, CSS3, JavaScript (原生)
- **视频**: WebRTC (getUserMedia API)

## 性能优化建议

1. **使用 GPU 加速**（可选）：
   - 安装 CUDA 和 cuDNN
   - 安装 GPU 版本的 dlib
   - 修改 `face_detector.py` 中的 `model_type` 为 `"cnn"`

2. **调整检测频率**：
   - 修改 `static/js/app.js` 中的 `detectionInterval` 值
   - 默认 500ms，可根据性能调整

3. **降低视频分辨率**：
   - 修改 `getUserMedia` 的分辨率设置

## 常见问题

### Q: dlib 安装失败怎么办？

A:
1. 确保已安装 CMake 和 C++ 编译器
2. 使用 conda：`conda install -c conda-forge dlib`
3. 或使用预编译版本

### Q: 摄像头无法访问？

A:
1. 确保浏览器有摄像头权限
2. 使用 HTTPS 或 localhost（HTTP 可能被阻止）
3. 检查系统隐私设置

### Q: 识别准确率低？

A:
1. 使用清晰、正面的人脸照片
2. 确保光照充足
3. 调整 `face_detector.py` 中的 `tolerance` 参数（0.6 → 0.5 更严格）

### Q: 服务启动报错？

A:
1. 检查依赖是否完整安装：`pip list`
2. 检查端口 8000 是否被占用
3. 查看详细错误日志

## 安全建议

⚠️ **注意：这是一个演示项目，不建议直接用于生产环境**

生产环境需要考虑：
1. 添加用户认证和授权
2. 使用 HTTPS 加密传输
3. 对上传文件进行安全检查
4. 限制请求频率（防止滥用）
5. 数据库存储人脸特征（而非文件）
6. 遵守隐私法规（GDPR, CCPA 等）

## 开发计划

- [ ] 添加人脸特征数据库存储
- [ ] 支持批量导入人脸
- [ ] 添加识别历史记录
- [ ] 支持多人同时识别
- [ ] 移动端 APP
- [ ] Docker 部署

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请在 GitHub 提交 Issue。
