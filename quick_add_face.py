#!/usr/bin/env python3
"""
快速添加人脸的脚本
用法: python quick_add_face.py <照片路径> <姓名>
"""
import sys
import cv2
from face_detector import get_face_detector

def main():
    if len(sys.argv) != 3:
        print("=" * 50)
        print("快速添加人脸")
        print("=" * 50)
        print()
        print("用法:")
        print(f"  python {sys.argv[0]} <照片路径> <姓名>")
        print()
        print("示例:")
        print(f"  python {sys.argv[0]} ~/photo.jpg 张三")
        print(f"  python {sys.argv[0]} /path/to/image.png 李四")
        print()
        return 1

    photo_path = sys.argv[1]
    name = sys.argv[2]

    print("=" * 50)
    print("添加人脸到识别系统")
    print("=" * 50)
    print()
    print(f"照片路径: {photo_path}")
    print(f"姓名: {name}")
    print()

    # 读取图片
    print("正在读取图片...")
    image = cv2.imread(photo_path)
    if image is None:
        print(f"✗ 错误: 无法读取图片 {photo_path}")
        print("  请检查文件路径是否正确")
        return 1

    print(f"✓ 图片读取成功 ({image.shape[1]}x{image.shape[0]})")

    # 初始化检测器
    print()
    print("正在初始化人脸检测器...")
    detector = get_face_detector()

    # 添加人脸
    print()
    print("正在检测和添加人脸...")
    save_path = f"models/known_faces/{name}.jpg"
    success = detector.add_known_face(image, name, save_path)

    print()
    if success:
        print("=" * 50)
        print("✓ 成功添加人脸！")
        print("=" * 50)
        print()
        print(f"姓名: {name}")
        print(f"保存位置: {save_path}")
        print()
        print("下一步:")
        print("1. 重启服务以加载新人脸:")
        print("   pkill -f 'python main.py'")
        print("   venv/bin/python main.py &")
        print()
        print("2. 测试识别:")
        print("   访问 http://localhost:8000")
        print("   点击'图片上传'标签页")
        print("   上传你的照片测试识别")
        print()
        return 0
    else:
        print("=" * 50)
        print("✗ 添加失败！")
        print("=" * 50)
        print()
        print("原因: 图片中未检测到人脸")
        print()
        print("请确保照片满足以下要求:")
        print("  ✓ 真实人脸照片（不是卡通、动漫）")
        print("  ✓ 正面照片")
        print("  ✓ 清晰度高")
        print("  ✓ 光线充足")
        print("  ✓ 无遮挡")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
