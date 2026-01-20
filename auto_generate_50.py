#!/usr/bin/env python3
"""自动生成50个AI人脸（用于快速演示）"""
import os
import time
import random
import urllib.request
from PIL import Image
import io

SURNAMES = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']

GIVEN_NAMES = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
               '勇', '艳', '杰', '涛', '明', '超', '霞', '平', '刚', '华']

def generate_random_name():
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)

def download_ai_face(save_path):
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

print("自动生成50个AI人脸")
print("=" * 50)

output_dir = 'models/known_faces'
os.makedirs(output_dir, exist_ok=True)

names_set = {'小徐'}  # 保留已有的
success = 0
failed = 0

for i in range(50):
    while True:
        name = generate_random_name()
        if name not in names_set:
            names_set.add(name)
            break

    filepath = os.path.join(output_dir, f"{name}.jpg")
    print(f"[{i+1}/50] {name}...", end=' ', flush=True)

    if download_ai_face(filepath):
        success += 1
        print("✓")
    else:
        failed += 1
        print("✗")

    if (i + 1) % 10 == 0:
        print(f"  进度: {i+1}/50, 成功: {success}, 失败: {failed}")

    time.sleep(0.5)

print()
print("=" * 50)
print(f"完成！成功: {success}, 失败: {failed}")
print("总人脸数（含小徐）:", success + 1)
