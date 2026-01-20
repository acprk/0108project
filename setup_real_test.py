"""
创建更实用的测试环境
由于 face_recognition 需要真实人脸特征，简单的几何图形无法被识别
本脚本提供一个实用的测试方案
"""
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import random

print("=" * 60)
print("人脸识别系统 - 实用测试方案")
print("=" * 60)

print("\n重要说明：")
print("-" * 60)
print("face_recognition 库使用深度学习模型，需要真实的人脸图像。")
print("简单的几何图形无法被识别为人脸。")
print()
print("为了测试系统，我们有以下几个方案：")
print()

print("【方案一】仅使用真实人脸进行测试（推荐）")
print("  - 通过 Web 界面手动添加几个朋友/同事的照片")
print("  - 添加你自己的照片")
print("  - 测试系统能否正确识别")
print()

print("【方案二】使用公开人脸数据集（需要下载）")
print("  - LFW (Labeled Faces in the Wild) 数据集")
print("  - CelebA 数据集")
print("  - 需要约 100MB-1GB 下载量")
print()

print("【方案三】创建演示场景")
print("  - 我会创建一个演示脚本")
print("  - 模拟识别场景（使用占位符）")
print("  - 仅用于界面展示，不是真实识别")
print()

print("=" * 60)
print("推荐操作流程")
print("=" * 60)

print("\n步骤 1: 添加你的真实照片")
print("-" * 60)
print("方法 A: 通过 Web 界面（推荐）")
print("  1. 访问 http://localhost:8000")
print("  2. 点击 '人脸管理' 标签页")
print("  3. 输入你的姓名")
print("  4. 上传你的清晰正面照片")
print("  5. 点击 '添加人脸'")
print()

print("方法 B: 直接复制文件")
print("  1. 准备你的照片（JPEG格式，正面，清晰）")
print(f"  2. 复制到: {os.path.abspath('models/known_faces')}")
print("  3. 重命名为: 你的名字.jpg")
print("     例如: 张三.jpg")
print()

print("步骤 2: 添加更多测试人脸（可选）")
print("-" * 60)
print("  - 可以添加朋友、同事的照片进行测试")
print("  - 或使用网上找的名人照片（仅用于测试）")
print("  - 建议添加 3-5 张即可测试系统")
print()

print("步骤 3: 测试识别功能")
print("-" * 60)
print("  1. 访问 http://localhost:8000")
print("  2. 点击 '实时识别' 标签页")
print("  3. 点击 '启动摄像头'")
print("  4. 将你的脸对准摄像头")
print("  5. 观察系统是否能识别出你的名字")
print()

print("=" * 60)
print("照片要求")
print("=" * 60)
print("✓ 正面照片（不要侧脸）")
print("✓ 光线充足（避免逆光、阴影）")
print("✓ 表情自然（可以微笑）")
print("✓ 清晰度高（不模糊）")
print("✓ 无遮挡（不戴口罩、墨镜）")
print("✓ 格式: JPEG 或 PNG")
print("✓ 大小: 建议 200x200 像素以上")
print()

print("=" * 60)
print("常见问题")
print("=" * 60)
print()

print("Q: 为什么之前生成的 1000 张图片无法识别？")
print("A: 那些是简单的几何图形，不包含真实人脸的特征。")
print("   face_recognition 使用深度学习，需要真实眼睛、鼻子、嘴巴等特征。")
print()

print("Q: 可以使用卡通头像或动漫图片吗？")
print("A: 不可以。必须是真实人脸照片。")
print()

print("Q: 需要多少张照片才能测试？")
print("A: 至少 1 张（你自己的）。建议 3-5 张以测试多人识别。")
print()

print("Q: 照片太大或太小怎么办？")
print("A: 系统会自动处理大小，但建议使用 200x200 到 1920x1080 之间的尺寸。")
print()

print("=" * 60)
print("示例：创建测试照片")
print("=" * 60)
print()
print("如果你没有照片，可以：")
print("1. 使用手机自拍一张")
print("2. 传输到电脑")
print("3. 通过 Web 界面上传")
print()
print("或者使用网络摄像头直接拍照（需要外部工具）：")
print("  Linux: cheese, guvcview")
print("  macOS: Photo Booth")
print("  Windows: 相机应用")
print()

print("=" * 60)
print("清理之前生成的测试数据")
print("=" * 60)

response = input("\n是否清理之前生成的 1000 张无效图片？(y/n): ").lower()

if response == 'y':
    output_dir = 'models/known_faces'
    count = 0
    for filename in os.listdir(output_dir):
        if filename.endswith('.jpg') and not filename.startswith('真实_'):
            filepath = os.path.join(output_dir, filename)
            os.remove(filepath)
            count += 1

    print(f"\n✓ 已删除 {count} 张无效图片")
    print(f"✓ 目录已清理: {output_dir}")
    print("\n现在你可以添加真实的人脸照片了！")
else:
    print("\n保留现有文件。")

print("\n" + "=" * 60)
print("下一步：添加你的真实人脸照片并开始测试！")
print("=" * 60)
print()
