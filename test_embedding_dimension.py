#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试人脸特征向量的维度
"""

import cv2
import face_recognition
import numpy as np
from pathlib import Path

def main():
    print("="*70)
    print("人脸特征向量（Embedding）维度测试")
    print("="*70)

    # 加载测试图片
    test_image = "自定义证件照_20240902.jpg"

    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return

    print(f"\n📷 加载测试图片: {test_image}")

    # 使用 face_recognition 加载图片
    image = face_recognition.load_image_file(test_image)
    print(f"✅ 图片加载成功")
    print(f"   - 图片尺寸: {image.shape}")
    print(f"   - 图片大小: {image.shape[0]} × {image.shape[1]} 像素")
    print(f"   - 颜色通道: {image.shape[2]}")

    # 检测人脸
    print(f"\n🔍 检测人脸...")
    face_locations = face_recognition.face_locations(image)
    print(f"✅ 检测到 {len(face_locations)} 张人脸")

    if len(face_locations) == 0:
        print("❌ 未检测到人脸")
        return

    # 提取人脸特征向量
    print(f"\n🧮 提取人脸特征向量（Embedding）...")
    face_encodings = face_recognition.face_encodings(image, face_locations)

    if len(face_encodings) == 0:
        print("❌ 无法提取特征向量")
        return

    # 分析第一个人脸的特征向量
    encoding = face_encodings[0]

    print(f"✅ 特征向量提取成功！")
    print(f"\n{'='*70}")
    print(f"📊 特征向量详细信息")
    print(f"{'='*70}")

    print(f"\n🎯 **核心参数**:")
    print(f"   - 向量维度: {len(encoding)} 维")
    print(f"   - 数据类型: {encoding.dtype}")
    print(f"   - 内存占用: {encoding.nbytes} 字节")

    print(f"\n📈 **向量统计信息**:")
    print(f"   - 最小值: {np.min(encoding):.6f}")
    print(f"   - 最大值: {np.max(encoding):.6f}")
    print(f"   - 平均值: {np.mean(encoding):.6f}")
    print(f"   - 标准差: {np.std(encoding):.6f}")
    print(f"   - 向量范数(L2): {np.linalg.norm(encoding):.6f}")

    print(f"\n🔢 **前10个特征值**:")
    for i, val in enumerate(encoding[:10]):
        print(f"   [{i:2d}] {val:+.6f}")
    print(f"   ...")

    print(f"\n🔢 **后10个特征值**:")
    for i, val in enumerate(encoding[-10:], start=len(encoding)-10):
        print(f"   [{i:2d}] {val:+.6f}")

    # 测试多张人脸
    print(f"\n{'='*70}")
    print(f"📊 数据库中的人脸向量维度")
    print(f"{'='*70}")

    faces_dir = Path("models/known_faces")
    if faces_dir.exists():
        face_files = list(faces_dir.glob("*.jpg"))[:5]  # 测试前5张

        print(f"\n测试 {len(face_files)} 张人脸数据库图片...")

        all_same_dimension = True
        dimensions = []

        for face_file in face_files:
            image = face_recognition.load_image_file(str(face_file))
            encodings = face_recognition.face_encodings(image)

            if encodings:
                dim = len(encodings[0])
                dimensions.append(dim)
                print(f"✅ {face_file.stem[:20]:<20} - {dim} 维")

                if dim != 128:
                    all_same_dimension = False
            else:
                print(f"❌ {face_file.stem[:20]:<20} - 无法提取特征")

        if dimensions:
            print(f"\n{'='*70}")
            print(f"📊 统计结果")
            print(f"{'='*70}")
            print(f"所有人脸向量维度: {set(dimensions)}")

            if all_same_dimension and len(set(dimensions)) == 1:
                print(f"✅ 所有人脸向量维度一致: {dimensions[0]} 维")

    # 技术原理说明
    print(f"\n{'='*70}")
    print(f"💡 技术原理说明")
    print(f"{'='*70}")

    print(f"""
📚 **使用的深度学习模型**:
   - 模型名称: dlib ResNet-34
   - 模型作者: Davis King (dlib 库作者)
   - 训练数据: 约 300 万张人脸图片
   - 模型精度: 在 LFW 数据集上达到 99.38% 准确率

🎯 **特征向量维度**: 128 维
   - 每个人脸被压缩成 128 个浮点数
   - 每个浮点数占用 8 字节 (float64)
   - 总计: 128 × 8 = 1024 字节 = 1 KB

🔬 **为什么是 128 维？**
   - 权衡了识别精度和计算效率
   - 太少（如 64 维）: 精度下降
   - 太多（如 512 维）: 计算慢，存储大
   - 128 维是经过大量实验验证的最优选择

🧮 **识别原理**:
   1. 将人脸图片输入 ResNet-34 网络
   2. 网络输出 128 维特征向量
   3. 计算待识别人脸与数据库中所有人脸的欧氏距离
      距离公式: d = √(Σ(a[i] - b[i])²)
   4. 找出距离最小的人脸
   5. 如果距离 < 阈值(0.5)，则识别成功

⚡ **计算复杂度**:
   - 提取特征: O(1) - 固定的神经网络计算
   - 比对 N 个人脸: O(N × 128) - 需要计算 N 次距离
   - 每增加 1 个人脸: 需要额外计算 128 次浮点数运算

💾 **存储需求**:
   - 1 个人脸: 1 KB
   - 1000 个人脸: 1 MB
   - 1,000,000 个人脸: 1 GB
""")

    print(f"{'='*70}")
    print(f"测试完成！")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
