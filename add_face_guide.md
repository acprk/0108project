# 添加人脸照片 - 操作指南

## 通过 Web 界面添加（最简单）

### 步骤 1: 打开浏览器
在浏览器地址栏输入：
```
http://localhost:8000
```

**重要：必须使用 localhost，不要用 IP 地址！**

### 步骤 2: 进入人脸管理页面
点击页面顶部的 **"人脸管理"** 标签页

### 步骤 3: 填写信息
1. **在"输入姓名"框中输入你的名字**
   - 例如：张三、李四、王五
   - 使用中文或英文都可以

2. **点击"选择人脸图片"按钮**
   - 浏览并选择你的照片
   - 就是你刚才给我看的那张蓝色背景的证件照

3. **点击"添加人脸"按钮**
   - 等待几秒
   - 看到"成功添加人脸"的提示

### 步骤 4: 验证是否成功
在同一页面的"已知人脸列表"区域，应该能看到你的名字

---

## 如果你已经有照片文件

### 方法 A: 使用命令行添加

1. **找到你的照片文件路径**
   ```bash
   # 假设你的照片在 ~/Downloads/my_photo.jpg
   ```

2. **运行以下命令**
   ```bash
   cd /home/luck/xzy/0108project

   # 将照片复制到人脸目录（替换"你的名字"为实际名字）
   cp ~/path/to/your/photo.jpg models/known_faces/你的名字.jpg

   # 示例：
   cp ~/Downloads/my_photo.jpg models/known_faces/张三.jpg
   ```

3. **重启服务**
   ```bash
   pkill -f "python main.py"
   venv/bin/python main.py &
   ```

### 方法 B: 通过 Python 脚本添加

创建一个临时脚本：

```python
#!/usr/bin/env python3
import cv2
import sys
from face_detector import get_face_detector

# 使用方法：
# venv/bin/python add_face.py /path/to/photo.jpg "姓名"

if len(sys.argv) != 3:
    print("用法: python add_face.py <照片路径> <姓名>")
    print("示例: python add_face.py ~/photo.jpg 张三")
    sys.exit(1)

photo_path = sys.argv[1]
name = sys.argv[2]

# 读取图片
image = cv2.imread(photo_path)
if image is None:
    print(f"错误: 无法读取图片 {photo_path}")
    sys.exit(1)

# 添加人脸
detector = get_face_detector()
save_path = f"models/known_faces/{name}.jpg"
success = detector.add_known_face(image, name, save_path)

if success:
    print(f"✓ 成功添加人脸: {name}")
    print(f"✓ 保存位置: {save_path}")
else:
    print(f"✗ 添加失败: 图片中未检测到人脸")
```

---

## 测试识别功能

添加成功后：

1. **刷新浏览器页面** (按 F5)

2. **点击"实时识别"标签页**

3. **点击"启动摄像头"**

4. **将你的脸对准摄像头**
   - 应该会显示你的名字（绿色框）
   - 如果显示"Unknown"，可能需要调整角度或光线

---

## 验证人脸是否添加成功

运行以下命令：

```bash
# 查看已添加的人脸
ls -lh models/known_faces/*.jpg

# 检查 API
curl http://localhost:8000/api/known_faces

# 测试特定照片是否能被识别
cd /home/luck/xzy/0108project
venv/bin/python -c "
import face_recognition
image = face_recognition.load_image_file('models/known_faces/你的名字.jpg')
faces = face_recognition.face_encodings(image)
print(f'检测到 {len(faces)} 张人脸')
if len(faces) > 0:
    print('✓ 照片可以被识别！')
else:
    print('✗ 照片无法识别，请更换照片')
"
```

---

## 需要帮助？

如果遇到问题，请告诉我：
1. 你使用的是哪种方法（Web 界面 / 命令行）
2. 出现了什么错误提示
3. 照片文件的路径

我会帮你解决！
