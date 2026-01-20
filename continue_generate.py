#!/usr/bin/env python3
"""继续生成人脸到1000个"""
import os
import time
import random
import urllib.request
from PIL import Image
import io

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

GIVEN_NAMES = [
    '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
    '洋', '勇', '艳', '杰', '涛', '明', '超', '秀兰', '霞', '平',
    '刚', '桂英', '华', '文', '月英', '玉兰', '春梅', '桂兰', '建华', '丹',
    '萍', '红', '玉', '燕', '鹏', '辉', '波', '斌', '颖', '浩',
    '宇', '婷', '欣', '凯', '琳', '婧', '瑶', '薇', '娟', '倩',
    '建国', '建军', '志强', '国强', '志明', '建平', '建伟', '建新',
    '晓明', '晓红', '晓丽', '晓燕', '晓东', '晓峰', '晓辉', '晓华',
    '思源', '思远', '思琪', '雨婷', '雨欣', '子轩', '子豪', '嘉欣'
]

def generate_random_name():
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)

def download_ai_face(save_path):
    url = "https://thispersondoesnotexist.com/"
    for attempt in range(3):
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
            if attempt < 2:
                time.sleep(2)
            continue
    return False

print("=" * 60)
print("继续生成人脸到1000个")
print("=" * 60)
print()

output_dir = 'models/known_faces'
os.makedirs(output_dir, exist_ok=True)

# 获取已有的名字
existing_names = set()
for f in os.listdir(output_dir):
    if f.endswith('.jpg'):
        name = f[:-4]  # 去掉.jpg
        existing_names.add(name)

current_count = len(existing_names)
print(f"当前已有: {current_count} 个人脸")
print(f"目标: 1000 个人脸")
print(f"还需生成: {1000 - current_count} 个")
print()

if current_count >= 1000:
    print("已经达到1000个，无需继续生成")
    exit(0)

target_count = 1000 - current_count
print(f"开始生成 {target_count} 个人脸...")
print()

success = 0
failed = 0
start_time = time.time()

for i in range(target_count):
    # 生成唯一名字
    attempts = 0
    while attempts < 100:
        name = generate_random_name()
        if name not in existing_names:
            existing_names.add(name)
            break
        attempts += 1

    if attempts >= 100:
        print(f"警告: 无法生成唯一名字，跳过")
        continue

    filepath = os.path.join(output_dir, f"{name}.jpg")
    print(f"[{current_count + i + 1}/1000] {name}...", end=' ', flush=True)

    if download_ai_face(filepath):
        success += 1
        print("✓")
    else:
        failed += 1
        print("✗")

    # 每10个显示进度
    if (i + 1) % 10 == 0:
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1)
        remaining = avg_time * (target_count - i - 1)
        print(f"  进度: {current_count + i + 1}/1000 | "
              f"成功: {success} | 失败: {failed} | "
              f"预计剩余: {remaining/60:.1f}分钟")

    # 每50个保存一次检查点
    if (i + 1) % 50 == 0:
        print(f"\n✓ 检查点: 已生成 {current_count + i + 1} 个人脸\n")

    time.sleep(0.5)  # 避免请求过快

print()
print("=" * 60)
print("生成完成！")
print("=" * 60)
print(f"本次成功: {success}")
print(f"本次失败: {failed}")
print(f"总人脸数: {current_count + success}")
print(f"总耗时: {(time.time() - start_time)/60:.1f} 分钟")
print()
