#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试识别速度与人脸数量的关系
验证：速度是否随人脸数量线性增长
"""

import time
import cv2
import sys
from pathlib import Path
from face_detector import FaceDetector

def format_time(seconds):
    """格式化时间"""
    if seconds < 1:
        return f"{seconds * 1000:.2f} 毫秒"
    else:
        return f"{seconds:.3f} 秒"

def test_with_n_faces(n_faces, test_image_path, all_faces_dir):
    """测试指定数量人脸的识别速度"""
    print(f"\n{'='*70}")
    print(f"测试人脸数量: {n_faces}")
    print(f"{'='*70}")

    # 创建新的检测器
    detector = FaceDetector()

    # 加载指定数量的人脸
    all_faces = list(Path(all_faces_dir).glob("*.jpg"))
    selected_faces = all_faces[:n_faces]

    print(f"🔄 正在加载 {len(selected_faces)} 张人脸...")
    load_start = time.time()

    for face_path in selected_faces:
        image = cv2.imread(str(face_path))
        if image is not None:
            try:
                import face_recognition
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_image)
                if encodings:
                    detector.known_face_encodings.append(encodings[0])
                    detector.known_face_names.append(face_path.stem)
            except Exception as e:
                pass

    load_end = time.time()
    load_time = load_end - load_start

    actual_loaded = len(detector.known_face_names)
    print(f"✅ 实际加载: {actual_loaded} 张人脸")
    print(f"⏱️  加载耗时: {format_time(load_time)}")

    # 测试识别速度（多次测试取平均）
    test_image = cv2.imread(test_image_path)
    if test_image is None:
        print(f"❌ 无法加载测试图片")
        return None

    print(f"\n🔄 进行 5 次识别测试...")
    times = []

    for i in range(5):
        start_time = time.time()
        face_locations, face_names = detector.detect_faces(test_image)
        end_time = time.time()

        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        print(f"  第 {i+1} 次: {format_time(elapsed_time)}")

    avg_time = sum(times) / len(times)
    print(f"\n📊 平均识别时间: {format_time(avg_time)}")

    return {
        'face_count': actual_loaded,
        'avg_time': avg_time,
        'times': times,
        'load_time': load_time
    }

def main():
    print("="*70)
    print("识别速度 vs 人脸数量关系测试")
    print("="*70)

    # 测试图片
    test_image = "自定义证件照_20240902.jpg"
    if not Path(test_image).exists():
        print(f"❌ 测试图片不存在: {test_image}")
        return

    # 人脸目录
    faces_dir = "models/known_faces"
    if not Path(faces_dir).exists():
        print(f"❌ 人脸目录不存在: {faces_dir}")
        return

    # 统计总人脸数
    total_faces = len(list(Path(faces_dir).glob("*.jpg")))
    print(f"\n📊 人脸数据库总数: {total_faces}")

    # 测试不同数量的人脸
    test_counts = [10, 50, 100, 200, 500, 1000]

    # 只测试存在的数量
    test_counts = [n for n in test_counts if n <= total_faces]

    # 如果数据库很大，也测试全部
    if total_faces not in test_counts and total_faces > 100:
        test_counts.append(total_faces)

    test_counts.sort()

    print(f"\n将测试以下人脸数量: {test_counts}")

    # 进行测试
    results = []
    for n in test_counts:
        result = test_with_n_faces(n, test_image, faces_dir)
        if result:
            results.append(result)

        # 避免内存泄漏，稍微等待
        time.sleep(0.5)

    # 输出汇总报告
    print(f"\n\n{'='*70}")
    print("📊 测试结果汇总")
    print(f"{'='*70}")

    print(f"\n{'人脸数量':<12} {'平均识别时间':<15} {'速度比':<10}")
    print("-" * 70)

    if results:
        baseline = results[0]['avg_time']
        for result in results:
            face_count = result['face_count']
            avg_time = result['avg_time']
            ratio = avg_time / baseline

            print(f"{face_count:<12} {format_time(avg_time):<15} {ratio:.2f}x")

    # 分析线性关系
    if len(results) >= 2:
        print(f"\n{'='*70}")
        print("📈 线性关系分析")
        print(f"{'='*70}")

        # 计算每个人脸的平均耗时
        times_per_face = []
        for result in results:
            if result['face_count'] > 0:
                time_per_face = result['avg_time'] / result['face_count'] * 1000  # 转换为毫秒
                times_per_face.append(time_per_face)
                print(f"人脸数: {result['face_count']:>4} | "
                      f"总时间: {format_time(result['avg_time'])} | "
                      f"每个人脸耗时: {time_per_face:.4f} 毫秒")

        if times_per_face:
            avg_per_face = sum(times_per_face) / len(times_per_face)
            print(f"\n💡 结论: 平均每增加1个人脸，识别时间增加约 {avg_per_face:.4f} 毫秒")

    # 给出优化建议
    if results:
        max_result = results[-1]
        print(f"\n{'='*70}")
        print("💡 优化建议")
        print(f"{'='*70}")

        current_time = max_result['avg_time'] * 1000  # 转换为毫秒
        current_count = max_result['face_count']

        print(f"\n当前配置:")
        print(f"  - 人脸数量: {current_count}")
        print(f"  - 识别速度: {format_time(max_result['avg_time'])}")

        # 计算不同人脸数量下的预期速度
        if current_count > 100:
            print(f"\n如果减少人脸数量:")

            for target in [500, 100, 50, 10]:
                if target < current_count:
                    estimated_time = (current_time / current_count) * target
                    speedup = current_time / estimated_time
                    print(f"  - 减少到 {target:>4} 个人脸: "
                          f"约 {estimated_time:>6.2f} 毫秒 "
                          f"(速度提升 {speedup:.1f}x)")

    print(f"\n{'='*70}")
    print("测试完成！")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
