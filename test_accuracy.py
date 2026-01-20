#!/usr/bin/env python3
"""
测试识别准确性
使用测试集验证系统的识别能力
"""
import os
import cv2
from face_detector import get_face_detector
from pathlib import Path
import json
from datetime import datetime

def test_accuracy():
    print("=" * 70)
    print("人脸识别准确性测试")
    print("=" * 70)
    print()

    # 初始化检测器
    print("正在加载人脸检测器...")
    detector = get_face_detector()
    print(f"✓ 已加载 {len(detector.known_face_names)} 个已知人脸")
    print()

    # 测试集路径
    test_dir = 'test_set'
    known_dir = os.path.join(test_dir, 'known_faces')
    unknown_dir = os.path.join(test_dir, 'unknown_faces')

    if not os.path.exists(test_dir):
        print("错误: 测试集不存在")
        print("请先运行: venv/bin/python create_test_set.py")
        return

    # 统计结果
    results = {
        'known_faces': {
            'total': 0,
            'correct': 0,
            'wrong': 0,
            'not_detected': 0,
            'details': []
        },
        'unknown_faces': {
            'total': 0,
            'correct_reject': 0,
            'false_positive': 0,
            'not_detected': 0,
            'details': []
        }
    }

    # 测试已知人脸
    print("=" * 70)
    print("测试1: 已知人脸识别测试")
    print("=" * 70)
    print()
    print("目标: 识别出正确的名字")
    print()

    known_faces = [f for f in os.listdir(known_dir) if f.endswith('.jpg')]
    results['known_faces']['total'] = len(known_faces)

    for i, face_file in enumerate(known_faces, 1):
        expected_name = face_file[:-4]  # 去掉.jpg
        filepath = os.path.join(known_dir, face_file)

        # 读取并识别
        image = cv2.imread(filepath)
        face_locations, face_names = detector.detect_faces(image)

        print(f"[{i}/{len(known_faces)}] {face_file:30s}", end=' ')

        if len(face_locations) == 0:
            print("✗ 未检测到人脸")
            results['known_faces']['not_detected'] += 1
            results['known_faces']['details'].append({
                'file': face_file,
                'expected': expected_name,
                'result': 'NOT_DETECTED'
            })
        elif face_names[0] == expected_name:
            print(f"✓ 正确: {face_names[0]}")
            results['known_faces']['correct'] += 1
            results['known_faces']['details'].append({
                'file': face_file,
                'expected': expected_name,
                'result': face_names[0],
                'status': 'CORRECT'
            })
        else:
            print(f"✗ 错误: 识别为 {face_names[0]}，应为 {expected_name}")
            results['known_faces']['wrong'] += 1
            results['known_faces']['details'].append({
                'file': face_file,
                'expected': expected_name,
                'result': face_names[0],
                'status': 'WRONG'
            })

    print()
    print(f"已知人脸测试结果:")
    print(f"  总数: {results['known_faces']['total']}")
    print(f"  正确: {results['known_faces']['correct']} "
          f"({results['known_faces']['correct']/results['known_faces']['total']*100:.1f}%)")
    print(f"  错误: {results['known_faces']['wrong']}")
    print(f"  未检测: {results['known_faces']['not_detected']}")
    print()

    # 测试陌生人脸
    print("=" * 70)
    print("测试2: 陌生人脸拒绝测试")
    print("=" * 70)
    print()
    print("目标: 识别为 Unknown（拒绝识别）")
    print()

    unknown_faces = [f for f in os.listdir(unknown_dir) if f.endswith('.jpg')]
    results['unknown_faces']['total'] = len(unknown_faces)

    for i, face_file in enumerate(unknown_faces, 1):
        filepath = os.path.join(unknown_dir, face_file)

        # 读取并识别
        image = cv2.imread(filepath)
        face_locations, face_names = detector.detect_faces(image)

        print(f"[{i}/{len(unknown_faces)}] {face_file:30s}", end=' ')

        if len(face_locations) == 0:
            print("✗ 未检测到人脸")
            results['unknown_faces']['not_detected'] += 1
            results['unknown_faces']['details'].append({
                'file': face_file,
                'result': 'NOT_DETECTED'
            })
        elif face_names[0] == 'Unknown':
            print(f"✓ 正确拒绝（Unknown）")
            results['unknown_faces']['correct_reject'] += 1
            results['unknown_faces']['details'].append({
                'file': face_file,
                'result': 'Unknown',
                'status': 'CORRECT_REJECT'
            })
        else:
            print(f"✗ 误识别为: {face_names[0]}")
            results['unknown_faces']['false_positive'] += 1
            results['unknown_faces']['details'].append({
                'file': face_file,
                'result': face_names[0],
                'status': 'FALSE_POSITIVE'
            })

    print()
    print(f"陌生人脸测试结果:")
    print(f"  总数: {results['unknown_faces']['total']}")
    print(f"  正确拒绝: {results['unknown_faces']['correct_reject']} "
          f"({results['unknown_faces']['correct_reject']/results['unknown_faces']['total']*100:.1f}%)")
    print(f"  误识别: {results['unknown_faces']['false_positive']}")
    print(f"  未检测: {results['unknown_faces']['not_detected']}")
    print()

    # 总体统计
    print("=" * 70)
    print("总体统计")
    print("=" * 70)
    print()

    total_tests = results['known_faces']['total'] + results['unknown_faces']['total']
    total_correct = (results['known_faces']['correct'] +
                     results['unknown_faces']['correct_reject'])
    total_errors = (results['known_faces']['wrong'] +
                    results['unknown_faces']['false_positive'])
    total_not_detected = (results['known_faces']['not_detected'] +
                          results['unknown_faces']['not_detected'])

    accuracy = total_correct / total_tests * 100 if total_tests > 0 else 0

    print(f"总测试数: {total_tests}")
    print(f"正确数: {total_correct}")
    print(f"错误数: {total_errors}")
    print(f"未检测: {total_not_detected}")
    print()
    print(f"✨ 总体准确率: {accuracy:.2f}%")
    print()

    # 评级
    if accuracy >= 95:
        rating = "优秀 ⭐⭐⭐⭐⭐"
    elif accuracy >= 90:
        rating = "良好 ⭐⭐⭐⭐"
    elif accuracy >= 80:
        rating = "中等 ⭐⭐⭐"
    elif accuracy >= 70:
        rating = "及格 ⭐⭐"
    else:
        rating = "需要改进 ⭐"

    print(f"评级: {rating}")
    print()

    # 保存结果
    results['summary'] = {
        'total_tests': total_tests,
        'total_correct': total_correct,
        'total_errors': total_errors,
        'total_not_detected': total_not_detected,
        'accuracy': accuracy,
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    }

    result_file = 'test_results.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"详细结果已保存到: {result_file}")
    print()

    # 建议
    print("=" * 70)
    print("优化建议")
    print("=" * 70)
    print()

    if results['known_faces']['wrong'] > 0:
        print("⚠️  已知人脸识别错误:")
        print("   - 可能原因: 照片质量、光线、角度差异")
        print("   - 建议: 为每个人添加多张不同角度的照片")
        print()

    if results['unknown_faces']['false_positive'] > 0:
        print("⚠️  陌生人脸误识别:")
        print("   - 可能原因: 相似度阈值过低")
        print("   - 建议: 调整 face_detector.py 中的 tolerance 参数")
        print("   - 当前: 0.6，可以改为 0.5（更严格）")
        print()

    if total_not_detected > 0:
        print("⚠️  部分人脸未检测到:")
        print("   - 可能原因: 照片质量差、分辨率低、遮挡")
        print("   - 建议: 使用高质量的正面照片")
        print()

    print("=" * 70)

if __name__ == "__main__":
    test_accuracy()
