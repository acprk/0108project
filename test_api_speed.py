#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API识别速度测试脚本
测试通过HTTP API的识别速度
"""

import time
import requests
from pathlib import Path

def format_time(seconds):
    """格式化时间"""
    if seconds < 1:
        return f"{seconds * 1000:.2f} 毫秒"
    else:
        return f"{seconds:.3f} 秒"

def test_api_speed(image_path, api_url):
    """测试API识别速度"""
    print(f"\n{'='*70}")
    print(f"测试图片: {image_path}")
    print(f"API地址: {api_url}")
    print(f"{'='*70}")

    # 读取图片文件
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f, 'image/jpeg')}

        # 记录开始时间
        start_time = time.time()

        # 发送请求
        response = requests.post(api_url, files=files)

        # 记录结束时间
        end_time = time.time()

    elapsed_time = end_time - start_time

    # 解析响应
    if response.status_code == 200:
        data = response.json()

        print(f"\n⏱️  总耗时: {format_time(elapsed_time)}")
        print(f"✅ 识别成功")
        print(f"📊 检测到人脸数: {data.get('face_count', 0)}")

        if 'faces' in data:
            for i, face in enumerate(data['faces'], 1):
                print(f"\n人脸 {i}:")
                print(f"  - 姓名: {face.get('name', 'Unknown')}")
                print(f"  - 位置: Top={face['location']['top']}, Left={face['location']['left']}")

        return elapsed_time, True
    else:
        print(f"\n⏱️  总耗时: {format_time(elapsed_time)}")
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"响应: {response.text}")
        return elapsed_time, False

def test_multiple(image_paths, api_url, count=5):
    """测试多次请求的平均速度"""
    print(f"\n{'='*70}")
    print(f"批量测试: {count} 次请求")
    print(f"{'='*70}")

    times = []
    success_count = 0

    for i in range(count):
        # 轮流使用不同的图片
        image_path = image_paths[i % len(image_paths)]

        print(f"\n[{i+1}/{count}] 测试: {Path(image_path).name}")

        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}

            start_time = time.time()
            try:
                response = requests.post(api_url, files=files, timeout=30)
                end_time = time.time()

                elapsed_time = end_time - start_time
                times.append(elapsed_time)

                if response.status_code == 200:
                    data = response.json()
                    success_count += 1
                    face_count = data.get('face_count', 0)
                    print(f"  ✅ 成功 - 耗时: {format_time(elapsed_time)} - 人脸数: {face_count}")
                else:
                    print(f"  ❌ 失败 - 耗时: {format_time(elapsed_time)} - HTTP {response.status_code}")

            except Exception as e:
                end_time = time.time()
                elapsed_time = end_time - start_time
                times.append(elapsed_time)
                print(f"  ❌ 错误 - 耗时: {format_time(elapsed_time)} - {str(e)}")

    # 统计结果
    if times:
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
    print("人脸识别 API 速度测试")
    print("="*70)

    # API地址
    api_url = "http://localhost:8001/api/detect"

    # 检查服务是否运行
    print("\n🔄 检查服务状态...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务正常运行")
            print(f"📊 已加载人脸数: {data.get('known_faces_count', 0)}")
        else:
            print(f"⚠️  服务响应异常: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return

    # 测试单张图片
    test_image = "自定义证件照_20240902.jpg"
    if Path(test_image).exists():
        test_api_speed(test_image, api_url)
    else:
        print(f"\n⚠️  测试图片不存在: {test_image}")

    # 查找测试图片
    test_images = []

    # 添加主测试图片
    if Path(test_image).exists():
        test_images.append(test_image)

    # 添加测试集中的图片
    test_set_known = Path("test_set/known_faces")
    if test_set_known.exists():
        test_images.extend([str(p) for p in list(test_set_known.glob("*.jpg"))[:5]])

    # 如果有测试图片，进行批量测试
    if len(test_images) > 0:
        print(f"\n\n找到 {len(test_images)} 张测试图片")
        print("进行批量测试（10次）...")
        test_multiple(test_images, api_url, count=10)

    print(f"\n{'='*70}")
    print("测试完成！")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
