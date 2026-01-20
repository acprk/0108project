"""
生成测试数据：1000个虚假人脸和姓名
使用PIL生成带有随机特征的人脸占位符
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 常见姓氏（100个）
SURNAMES = [
    '王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
    '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高',
    '梁', '郑', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
    '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡',
    '余', '杜', '叶', '程', '苏', '魏', '吕', '丁', '任', '沈',
    '姚', '卢', '姜', '崔', '钟', '谭', '陆', '汪', '范', '金',
    '石', '廖', '贾', '夏', '韦', '付', '方', '白', '邹', '孟',
    '熊', '秦', '邱', '江', '尹', '薛', '闫', '段', '雷', '侯',
    '龙', '史', '陶', '黎', '贺', '顾', '毛', '郝', '龚', '邵',
    '万', '钱', '严', '覃', '武', '戴', '莫', '孔', '向', '汤'
]

# 常见名字（单字和双字）
GIVEN_NAMES_SINGLE = [
    '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
    '洋', '勇', '艳', '杰', '涛', '明', '超', '秀兰', '霞', '平',
    '刚', '桂英', '华', '文', '月英', '玉兰', '春梅', '桂兰', '建华', '丹',
    '萍', '红', '玉', '燕', '鹏', '辉', '波', '斌', '颖', '浩',
    '宇', '婷', '欣', '凯', '琳', '婧', '瑶', '薇', '娟', '倩'
]

GIVEN_NAMES_DOUBLE = [
    '建国', '建军', '志强', '秀英', '桂英', '淑珍', '玉梅', '玉兰', '春梅', '秀兰',
    '国强', '国栋', '志明', '志刚', '建华', '建军', '建平', '建伟', '建新', '建设',
    '晓明', '晓红', '晓丽', '晓燕', '晓东', '晓峰', '晓辉', '晓华', '晓芳', '晓宇',
    '思源', '思远', '思琪', '思涵', '思婷', '雨婷', '雨欣', '雨萱', '雨涵', '雨晴',
    '子轩', '子豪', '子涵', '子墨', '子阳', '嘉欣', '嘉怡', '嘉琪', '嘉豪', '嘉宇'
]


def generate_random_name():
    """生成随机中文姓名"""
    surname = random.choice(SURNAMES)
    if random.random() < 0.5:
        given_name = random.choice(GIVEN_NAMES_SINGLE)
    else:
        given_name = random.choice(GIVEN_NAMES_DOUBLE)
    return surname + given_name


def generate_fake_face(name, output_path, size=(200, 200)):
    """
    生成带有随机特征的虚假人脸图片
    使用简单的几何形状模拟人脸特征
    """
    # 创建图片
    img = Image.new('RGB', size, color=(random.randint(200, 240),
                                        random.randint(180, 220),
                                        random.randint(150, 200)))
    draw = ImageDraw.Draw(img)

    # 随机肤色
    skin_color = (
        random.randint(180, 255),
        random.randint(140, 200),
        random.randint(100, 160)
    )

    # 绘制脸型（椭圆）
    face_margin = 20
    draw.ellipse([face_margin, face_margin, size[0]-face_margin, size[1]-face_margin],
                 fill=skin_color, outline=(100, 70, 50), width=2)

    # 绘制眼睛
    eye_y = size[1] // 3
    left_eye_x = size[0] // 3
    right_eye_x = size[0] * 2 // 3
    eye_size = 15

    # 左眼
    draw.ellipse([left_eye_x - eye_size//2, eye_y - eye_size//2,
                  left_eye_x + eye_size//2, eye_y + eye_size//2],
                 fill='white', outline='black', width=2)
    draw.ellipse([left_eye_x - 5, eye_y - 5, left_eye_x + 5, eye_y + 5],
                 fill=(50, 30, 20))

    # 右眼
    draw.ellipse([right_eye_x - eye_size//2, eye_y - eye_size//2,
                  right_eye_x + eye_size//2, eye_y + eye_size//2],
                 fill='white', outline='black', width=2)
    draw.ellipse([right_eye_x - 5, eye_y - 5, right_eye_x + 5, eye_y + 5],
                 fill=(50, 30, 20))

    # 绘制鼻子
    nose_x = size[0] // 2
    nose_y = size[1] // 2
    draw.line([nose_x, nose_y - 20, nose_x, nose_y + 10], fill=(100, 70, 50), width=3)

    # 绘制嘴巴
    mouth_y = size[1] * 2 // 3
    mouth_width = 40
    draw.arc([nose_x - mouth_width, mouth_y - 15,
              nose_x + mouth_width, mouth_y + 15],
             start=0, end=180, fill=(150, 80, 80), width=3)

    # 添加一些随机噪点（模拟皮肤纹理）
    pixels = img.load()
    for _ in range(500):
        x = random.randint(face_margin, size[0] - face_margin)
        y = random.randint(face_margin, size[1] - face_margin)
        # 检查是否在椭圆内
        if ((x - size[0]//2)**2 / (size[0]//2 - face_margin)**2 +
            (y - size[1]//2)**2 / (size[1]//2 - face_margin)**2) < 1:
            noise = random.randint(-10, 10)
            r = max(0, min(255, pixels[x, y][0] + noise))
            g = max(0, min(255, pixels[x, y][1] + noise))
            b = max(0, min(255, pixels[x, y][2] + noise))
            pixels[x, y] = (r, g, b)

    # 保存图片
    img.save(output_path, 'JPEG', quality=85)


def main():
    """主函数：生成1000个测试人脸"""
    print("=" * 50)
    print("生成测试数据")
    print("=" * 50)

    # 创建输出目录
    output_dir = 'models/known_faces'
    os.makedirs(output_dir, exist_ok=True)

    # 清空现有文件（可选）
    print(f"\n清理目录: {output_dir}")
    for filename in os.listdir(output_dir):
        if filename.endswith('.jpg') and not filename.startswith('真实_'):
            filepath = os.path.join(output_dir, filename)
            os.remove(filepath)
            print(f"  删除: {filename}")

    # 生成1000个虚假人脸
    print(f"\n开始生成 1000 个虚假人脸...")
    names_set = set()
    count = 0

    while count < 1000:
        name = generate_random_name()

        # 确保名字不重复
        if name in names_set:
            continue

        names_set.add(name)
        filename = f"{name}.jpg"
        filepath = os.path.join(output_dir, filename)

        # 生成人脸图片
        generate_fake_face(name, filepath)
        count += 1

        # 显示进度
        if count % 100 == 0:
            print(f"  已生成: {count}/1000")

    print(f"\n✓ 成功生成 {count} 个虚假人脸")
    print(f"✓ 保存位置: {output_dir}")

    print("\n" + "=" * 50)
    print("下一步：添加你的真实人脸")
    print("=" * 50)
    print("\n请按照以下步骤添加你的真实人脸：")
    print("\n方法一：通过 Web 界面添加")
    print("  1. 访问 http://localhost:8000")
    print("  2. 点击 '人脸管理' 标签页")
    print("  3. 输入你的姓名（例如：张三）")
    print("  4. 上传你的清晰正面照片")
    print("  5. 点击 '添加人脸' 按钮")

    print("\n方法二：直接复制照片到目录")
    print("  1. 准备一张你的清晰正面照片")
    print("  2. 重命名为 '真实_你的名字.jpg'（例如：真实_张三.jpg）")
    print(f"  3. 复制到: {output_dir}")

    print("\n提示：")
    print("  - 照片要求：正面、光线充足、清晰")
    print("  - 避免戴口罩、墨镜等遮挡物")
    print("  - 建议使用 JPEG 格式")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
