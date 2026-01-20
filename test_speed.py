#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸识别速度测试脚本
测试单张图片的识别速度
"""

import time
import sys
import cv2
from pathlib import Path
from face_detector import FaceDetector

def format_time(seconds):
    """格式化时间"""
    if seconds < 1:
        return f"{seconds * 1000:.2f} 毫秒"
    else:
        return f"{seconds:.3f} 秒"

def test_single_image(image_path, detector):
    """测试单张图片的识别速度"""
    print(f"\n{'='*70}")
    print(f"测试图片: {image_path}")
    print(f"{'='*70}")

    # 加载图片
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ 无法加载图片: {image_path}")
        return 0

    # 测试识别速度
    start_time = time.time()
    face_locations, face_names = detector.detect_faces(image)
    end_time = time.time()

    elapsed_time = end_time - start_time

    # 显示结果
    print(f"\n⏱️  总耗时: {format_time(elapsed_time)}")
    print(f"✅ 识别完成")
    print(f"📊 检测到人脸数: {len(face_locations)}")

    for i, (location, name) in enumerate(zip(face_locations, face_names), 1):
        top, right, bottom, left = location
        print(f"\n人脸 {i}:")
        print(f"  - 姓名: {name}")
        print(f"  - 位置: Top={top}, Left={left}, Right={right}, Bottom={bottom}")

    return elapsed_time

def test_multiple_images(image_paths, detector):
    """测试多张图片的平均速度"""
    print(f"\n{'='*70}")
    print(f"批量测试: {len(image_paths)} 张图片")
    print(f"{'='*70}")

    times = []
    success_count = 0

    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] 测试: {Path(image_path).name}")

        # 加载图片
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"  ❌ 无法加载图片")
            continue

        start_time = time.time()
        face_locations, face_names = detector.detect_faces(image)
        end_time = time.time()

        elapsed_time = end_time - start_time
        times.append(elapsed_time)

        success_count += 1
        print(f"  ✅ 成功 - 耗时: {format_time(elapsed_time)} - 人脸数: {len(face_locations)}")

    # 统计结果
    print(f"\n{'='*70}")
    print(f"📊 批量测试统计")
    print(f"{'='*70}")
    print(f"总测试数: {len(times)}")
    print(f"成功数: {success_count}")
    print(f"失败数: {len(times) - success_count}")
    print(f"成功率: {success_count / len(times) * 100:.1f}%")
    print(f"\n⏱️  速度统计:")
    print(f"  - 最快: {format_time(min(times))}")
    print(f"  - 最慢: {format_time(max(times))}")
    print(f"  - 平均: {format_time(sum(times) / len(times))}")
    print(f"  - 总计: {format_time(sum(times))}")

    return times

def main():
    print("="*70)
    print("人脸识别速度测试")
    print("="*70)

    # 初始化检测器
    print("\n🔄 正在加载人脸识别模型...")
    load_start = time.time()
    detector = FaceDetector()

    # 加载已知人脸
    faces_dir = "models/known_faces"
    if Path(faces_dir).exists():
        print(f"🔄 正在从 {faces_dir} 加载人脸数据...")
        detector.load_known_faces(faces_dir)
    else:
        print(f"⚠️  人脸目录不存在: {faces_dir}")

    load_end = time.time()
    load_time = load_end - load_start

    print(f"✅ 模型加载完成")
    print(f"⏱️  加载耗时: {format_time(load_time)}")
    print(f"📊 已知人脸数: {len(detector.known_face_names)}")

    # 测试单张图片
    test_image = "自定义证件照_20240902.jpg"
    if Path(test_image).exists():
        test_single_image(test_image, detector)
    else:
        print(f"\n⚠️  测试图片不存在: {test_image}")

    # 测试已知人脸目录
    known_faces_dir = Path("models/known_faces")
    if known_faces_dir.exists():
        test_images = list(known_faces_dir.glob("*.jpg"))[:10]  # 测试前10张
        if test_images:
            print(f"\n\n{'='*70}")
            print(f"测试数据库中的图片（前10张）")
            print(f"{'='*70}")
            test_multiple_images([str(img) for img in test_images], detector)

    # 测试测试集
    test_set_known = Path("test_set/known_faces")
    if test_set_known.exists():
        test_images = list(test_set_known.glob("*.jpg"))[:5]  # 测试5张已知人脸
        if test_images:
            print(f"\n\n{'='*70}")
            print(f"测试已知人脸测试集（前5张）")
            print(f"{'='*70}")
            test_multiple_images([str(img) for img in test_images], detector)

    print(f"\n{'='*70}")
    print("测试完成！")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
