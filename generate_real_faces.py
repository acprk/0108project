#!/usr/bin/env python3
"""
生成1000个真实的AI人脸
使用 ThisPersonDoesNotExist.com API
"""
import os
import time
import random
import urllib.request
from PIL import Image
import io

# 常见姓氏（100个）
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

# 常见名字
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
    """生成随机中文姓名"""
    surname = random.choice(SURNAMES)
    given_name = random.choice(GIVEN_NAMES)
    return surname + given_name


def download_ai_face(save_path, retry=3):
    """
    从 ThisPersonDoesNotExist 下载AI生成的人脸
    这个网站每次访问都会生成一个全新的、不存在的人脸
    """
    url = "https://thispersondoesnotexist.com/"

    for attempt in range(retry):
        try:
            # 添加随机参数避免缓存
            random_param = f"?{random.randint(1, 999999)}"
            req = urllib.request.Request(
                url + random_param,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                img_data = response.read()

            # 保存图片
            image = Image.open(io.BytesIO(img_data))
            # 调整大小为适合识别的尺寸
            image = image.resize((400, 400), Image.LANCZOS)
            image.save(save_path, 'JPEG', quality=90)
            return True

        except Exception as e:
            print(f"  下载失败 (尝试 {attempt + 1}/{retry}): {e}")
            if attempt < retry - 1:
                time.sleep(2)
            continue

    return False


def main():
    print("=" * 60)
    print("生成1000个真实AI人脸数据")
    print("=" * 60)
    print()
    print("数据源: ThisPersonDoesNotExist.com")
    print("说明: 使用 StyleGAN 生成的真实感人脸")
    print("特点: 每张人脸都是AI生成的，不是真实的人")
    print()

    # 确保目录存在
    output_dir = 'models/known_faces'
    os.makedirs(output_dir, exist_ok=True)

    # 询问是否清理现有文件
    existing_files = [f for f in os.listdir(output_dir) if f.endswith('.jpg') and f != '小徐.jpg']
    if existing_files:
        print(f"发现 {len(existing_files)} 个现有文件")
        response = input("是否清理这些文件? (y/n): ").lower()
        if response == 'y':
            for f in existing_files:
                os.remove(os.path.join(output_dir, f))
            print(f"✓ 已清理 {len(existing_files)} 个文件")

    print()
    print("=" * 60)
    print("开始生成人脸数据")
    print("=" * 60)
    print()
    print("⚠️  注意:")
    print("  - 每张图片需要从网络下载，需要时间")
    print("  - 1000张图片预计需要 30-60 分钟")
    print("  - 建议先生成少量测试（如50张）")
    print()

    # 询问生成数量
    try:
        count_str = input("请输入要生成的数量 (1-1000，推荐先测试50): ").strip()
        target_count = int(count_str)
        if target_count < 1 or target_count > 1000:
            print("数量必须在 1-1000 之间，使用默认值 50")
            target_count = 50
    except:
        print("输入无效，使用默认值 50")
        target_count = 50

    print()
    print(f"准备生成 {target_count} 个人脸...")
    print()

    # 生成人脸
    names_set = set()
    success_count = 0
    failed_count = 0

    # 添加已有的小徐到集合中
    names_set.add('小徐')

    start_time = time.time()

    for i in range(target_count):
        # 生成唯一的名字
        while True:
            name = generate_random_name()
            if name not in names_set:
                names_set.add(name)
                break

        filename = f"{name}.jpg"
        filepath = os.path.join(output_dir, filename)

        # 下载AI人脸
        print(f"[{i+1}/{target_count}] 生成: {name}...", end=' ')

        if download_ai_face(filepath):
            success_count += 1
            print("✓")
        else:
            failed_count += 1
            print("✗")

        # 显示进度
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / (i + 1)
            remaining = avg_time * (target_count - i - 1)
            print(f"  进度: {i+1}/{target_count} | "
                  f"成功: {success_count} | "
                  f"失败: {failed_count} | "
                  f"预计剩余: {remaining/60:.1f}分钟")

        # 避免请求过快
        time.sleep(0.5)

    # 总结
    print()
    print("=" * 60)
    print("生成完成")
    print("=" * 60)
    print()
    print(f"成功生成: {success_count} 个人脸")
    print(f"失败: {failed_count} 个")
    print(f"总耗时: {(time.time() - start_time)/60:.1f} 分钟")
    print(f"保存位置: {output_dir}")
    print()
    print("下一步:")
    print("1. 重启服务加载新人脸:")
    print("   pkill -f 'python main.py'")
    print("   venv/bin/python main.py &")
    print()
    print("2. 测试识别:")
    print("   访问 http://localhost:8000")
    print("   使用'图片上传'功能测试")
    print()


if __name__ == "__main__":
    main()
