#!/usr/bin/env python3
"""
创建测试集：100张图片用于验证识别准确性
包含:
- 50张已知人脸的不同照片（测试识别准确率）
- 50张陌生人脸（测试拒绝识别能力）
"""
import os
import time
import random
import urllib.request
from PIL import Image
import io
import shutil

def download_ai_face(save_path):
    """下载AI生成的人脸"""
    url = "https://thispersondoesnotexist.com/"
    try:
        req = urllib.request.Request(
            url + f"?{random.randint(1, 999999)}",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            img_data = response.read()
        image = Image.open(io.BytesIO(img_data))
        image = image.resize((400, 400), Image.LANCZOS)
        image.save(save_path, 'JPEG', quality=90)
        return True
    except:
        return False

def main():
    print("=" * 60)
    print("创建测试集 - 100张图片")
    print("=" * 60)
    print()

    # 创建测试集目录
    test_dir = 'test_set'
    known_dir = os.path.join(test_dir, 'known_faces')      # 已知人脸测试
    unknown_dir = os.path.join(test_dir, 'unknown_faces')  # 陌生人脸测试

    os.makedirs(known_dir, exist_ok=True)
    os.makedirs(unknown_dir, exist_ok=True)

    # 清空现有文件
    for d in [known_dir, unknown_dir]:
        for f in os.listdir(d):
            if f.endswith('.jpg'):
                os.remove(os.path.join(d, f))

    print("测试集组成:")
    print("  1. 已知人脸测试: 50张（复制自训练集，测试识别准确率）")
    print("  2. 陌生人脸测试: 50张（新下载的AI人脸，测试拒绝识别）")
    print()

    # 第一部分: 从已知人脸中随机选择50张作为测试
    print("=" * 60)
    print("第1部分: 准备已知人脸测试集（50张）")
    print("=" * 60)
    print()

    known_faces_dir = 'models/known_faces'
    known_faces = [f for f in os.listdir(known_faces_dir) if f.endswith('.jpg')]

    if len(known_faces) < 50:
        print(f"警告: 已知人脸只有 {len(known_faces)} 个，少于50个")
        print(f"将使用全部 {len(known_faces)} 个作为测试")
        test_known_faces = known_faces
    else:
        # 随机选择50个
        test_known_faces = random.sample(known_faces, 50)

    print(f"从 {len(known_faces)} 个已知人脸中选择 {len(test_known_faces)} 个")
    print()

    for i, face_file in enumerate(test_known_faces, 1):
        src = os.path.join(known_faces_dir, face_file)
        dst = os.path.join(known_dir, face_file)
        shutil.copy2(src, dst)
        print(f"[{i}/{len(test_known_faces)}] {face_file}")

    print()
    print(f"✓ 已知人脸测试集准备完成: {len(test_known_faces)} 张")
    print()

    # 第二部分: 下载50张陌生人脸
    print("=" * 60)
    print("第2部分: 下载陌生人脸测试集（50张）")
    print("=" * 60)
    print()
    print("这些人脸不在训练集中，用于测试系统是否能正确识别为 Unknown")
    print()

    success = 0
    failed = 0
    start_time = time.time()

    for i in range(50):
        filename = f"unknown_{i+1:03d}.jpg"
        filepath = os.path.join(unknown_dir, filename)

        print(f"[{i+1}/50] 下载: {filename}...", end=' ', flush=True)

        if download_ai_face(filepath):
            success += 1
            print("✓")
        else:
            failed += 1
            print("✗")

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / (i + 1)
            remaining = avg_time * (50 - i - 1)
            print(f"  进度: {i+1}/50 | 成功: {success} | "
                  f"失败: {failed} | 预计剩余: {remaining/60:.1f}分钟")

        time.sleep(0.5)

    print()
    print(f"✓ 陌生人脸测试集下载完成: {success} 张")
    print()

    # 总结
    print("=" * 60)
    print("测试集创建完成！")
    print("=" * 60)
    print()
    print(f"测试集位置: {test_dir}/")
    print(f"  - 已知人脸: {known_dir}/ ({len(test_known_faces)} 张)")
    print(f"  - 陌生人脸: {unknown_dir}/ ({success} 张)")
    print(f"  - 总计: {len(test_known_faces) + success} 张")
    print()
    print("下一步:")
    print("  运行测试脚本验证识别准确性:")
    print("  venv/bin/python test_accuracy.py")
    print()

if __name__ == "__main__":
    main()
