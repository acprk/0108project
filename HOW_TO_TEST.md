# 如何测试人脸识别系统

## 重要说明 ⚠️

之前生成的 1000 张几何图形**无法被识别**，因为：
- face_recognition 使用深度学习模型
- 需要**真实的人脸特征**（眼睛、鼻子、嘴巴的自然位置关系）
- 简单的几何图形不包含这些特征

**已清理无效数据**，现在需要添加真实人脸照片。

---

## 快速开始测试（3 步骤）

### 步骤 1: 准备你的照片

**拍摄要求：**
- ✅ 真实人脸（不是卡通、动漫）
- ✅ 正面照片
- ✅ 光线充足
- ✅ 表情自然
- ✅ 无遮挡（不戴口罩、墨镜）
- ✅ 清晰度高

**获取照片的方式：**

**方式 A: 使用手机自拍**
```
1. 打开手机相机
2. 正面自拍一张
3. 传输到电脑
```

**方式 B: 使用电脑摄像头**
- Linux: 安装 cheese (`sudo apt-get install cheese`)，然后运行 `cheese`
- macOS: 打开 Photo Booth
- Windows: 打开"相机"应用

**方式 C: 使用现有照片**
- 从你的相册中选择一张符合要求的照片

---

### 步骤 2: 添加照片到系统

#### 方法一：通过 Web 界面（推荐 ⭐）

1. **打开浏览器，访问：**
   ```
   http://localhost:8000
   ```

2. **点击"人脸管理"标签页**

3. **输入你的姓名**
   - 例如：张三

4. **点击"选择人脸图片"，上传照片**

5. **点击"添加人脸"按钮**

6. **等待提示"成功添加人脸"**

#### 方法二：直接复制文件

1. **将照片重命名为：`你的名字.jpg`**
   ```bash
   # 示例
   mv my_photo.jpg 张三.jpg
   ```

2. **复制到人脸目录：**
   ```bash
   cp 张三.jpg /home/luck/xzy/0108project/models/known_faces/
   ```

3. **重启服务**
   ```bash
   pkill -f "python main.py"
   cd /home/luck/xzy/0108project
   venv/bin/python main.py
   ```

---

### 步骤 3: 测试识别功能

1. **访问系统**
   ```
   http://localhost:8000
   ```

2. **点击"实时识别"标签页**

3. **⚠️ 重要：如果你看到红色提示**
   ```
   "当前使用 IP 地址访问，浏览器会阻止摄像头！"
   ```
   **请务必使用** `http://localhost:8000` **而不是** `http://192.168.x.x:8000`

4. **点击"启动摄像头"按钮**
   - 首次使用会弹出权限请求
   - 点击"允许"

5. **将你的脸对准摄像头**
   - 系统会自动检测并识别
   - 如果识别成功，会显示你的名字（绿色框）
   - 如果未识别，会显示"Unknown"（红色框）

---

## 添加更多测试人脸（可选）

为了测试多人识别功能，你可以：

### 选项 A: 添加朋友/同事的照片
```
1. 收集几张朋友的照片
2. 通过 Web 界面添加
3. 输入正确的姓名
```

### 选项 B: 使用名人照片（仅测试用）
```
1. 从网上下载几张名人的清晰正面照
2. 重命名为名人姓名
3. 添加到系统
4. 测试时用名人照片对准摄像头
```

**示例名人照片来源（仅供测试）：**
- 百度图片搜索："名人 正面照"
- 注意版权，仅用于个人测试

---

## 验证系统状态

### 检查已加载的人脸数量

```bash
# 方法一：通过 API
curl http://localhost:8000/api/known_faces

# 方法二：查看目录
ls -l models/known_faces/*.jpg | wc -l
```

### 查看服务日志

```bash
# 查看启动日志
cat /tmp/claude/-home-luck-xzy/tasks/b9c0ec7.output

# 应该看到类似：
# INFO:__main__:已加载 1 个已知人脸
```

---

## 故障排除

### 问题 1: 照片添加后没有被识别

**可能原因：**
- 服务未重启（使用 Web 界面添加可自动生效）
- 照片质量不佳
- 照片中没有检测到人脸

**解决方法：**
```bash
# 手动测试照片是否可识别
cd /home/luck/xzy/0108project
venv/bin/python -c "
import face_recognition
image = face_recognition.load_image_file('models/known_faces/你的名字.jpg')
encodings = face_recognition.face_encodings(image)
print(f'检测到人脸数量: {len(encodings)}')
"
```

如果输出 `0`，说明照片不符合要求，需要更换。

### 问题 2: 摄像头无法访问

**参考：** [摄像头故障排除指南](CAMERA_TROUBLESHOOTING.md)

**快速解决：**
- 使用 `http://localhost:8000` 访问
- 允许浏览器摄像头权限
- 使用 Chrome/Firefox/Edge 浏览器

### 问题 3: 识别率低或识别错误

**优化建议：**

1. **提高照片质量**
   - 使用高清照片
   - 确保光线充足
   - 正面拍摄

2. **调整识别阈值**
   编辑 `face_detector.py:92`：
   ```python
   # 从 0.6 调整为更严格的 0.5
   tolerance=0.5  # 越小越严格
   ```

3. **添加多张同一人的照片**
   - 不同角度
   - 不同表情
   - 不同光线条件

---

## 性能测试

### 测试识别速度

1. 添加 1-2 张人脸：识别速度很快（< 200ms）
2. 添加 10-20 张人脸：速度略慢（< 500ms）
3. 添加 100+ 张人脸：可能需要 1-2 秒

**注意：** 添加大量人脸会影响识别速度，生产环境建议使用数据库索引优化。

### 测试识别准确率

准备测试集：
```
models/known_faces/          # 训练集
  ├── 张三.jpg
  ├── 李四.jpg
  └── 王五.jpg

test_images/                # 测试集
  ├── 张三_test1.jpg
  ├── 张三_test2.jpg
  ├── 陌生人.jpg
  └── ...
```

通过"图片上传"功能测试每张图片的识别结果。

---

## 进阶使用

### 批量添加人脸

如果你有多张照片需要批量添加：

```bash
cd /home/luck/xzy/0108project

# 创建临时目录
mkdir -p temp_faces

# 将所有照片放入 temp_faces/ 并按 "姓名.jpg" 命名
# 然后运行：

for file in temp_faces/*.jpg; do
    name=$(basename "$file" .jpg)
    venv/bin/python -c "
from face_detector import get_face_detector
import cv2

detector = get_face_detector()
image = cv2.imread('$file')
success = detector.add_known_face(image, '$name', 'models/known_faces/$name.jpg')
print(f'添加 $name: {'成功' if success else '失败'}')
"
done
```

### 导出人脸数据库

备份你的人脸数据：
```bash
tar -czf face_database_backup.tar.gz models/known_faces/
```

恢复：
```bash
tar -xzf face_database_backup.tar.gz
```

---

## 测试完成检查清单

- [  ] 已添加至少 1 张真实人脸照片
- [  ] 服务显示"已加载 N 个已知人脸"（N > 0）
- [  ] 能够访问 http://localhost:8000
- [  ] 浏览器允许摄像头权限
- [  ] 摄像头能够正常打开
- [  ] 系统能识别出添加的人脸（显示正确姓名）
- [  ] 对于未添加的人脸显示"Unknown"

---

## 需要帮助？

如果遇到问题，请查看：
- [README.md](README.md) - 完整项目文档
- [CAMERA_TROUBLESHOOTING.md](CAMERA_TROUBLESHOOTING.md) - 摄像头问题
- [QUICKSTART.md](QUICKSTART.md) - 快速入门

或者运行诊断脚本：
```bash
venv/bin/python -c "
print('=== 系统诊断 ===')
import os
face_count = len([f for f in os.listdir('models/known_faces') if f.endswith('.jpg')])
print(f'人脸数量: {face_count}')

import face_recognition
print(f'face_recognition 版本: {face_recognition.__version__}')

import cv2
print(f'OpenCV 版本: {cv2.__version__}')

print('\\n如果人脸数量为 0，请添加真实人脸照片！')
"
```

---

**祝测试顺利！** 🎉
