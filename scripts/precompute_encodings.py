#!/usr/bin/env python3
"""
人脸特征预计算脚本

功能：
1. 加载所有已知人脸图片
2. 提取人脸特征向量（128维）
3. 保存到缓存文件（pickle格式）
4. 大幅减少应用启动时间（从45秒 → 2-3秒）

使用方法：
    python scripts/precompute_encodings.py

环境变量：
    KNOWN_FACES_DIR: 人脸图片目录（默认: models/known_faces）
    CACHE_DIR: 缓存文件目录（默认: data）
"""

import os
import sys
import pickle
import argparse
from pathlib import Path
from typing import List, Tuple

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import face_recognition
import numpy as np
from tqdm import tqdm

# 导入配置
from config import settings


def precompute_encodings(
    faces_dir: str,
    output_file: str,
    model_type: str = "hog"
) -> Tuple[int, int]:
    """
    预计算所有人脸特征并缓存

    Args:
        faces_dir: 人脸图片目录
        output_file: 输出缓存文件路径
        model_type: 人脸检测模型（"hog" 或 "cnn"）

    Returns:
        (成功数量, 失败数量)
    """
    faces_path = Path(faces_dir)

    if not faces_path.exists():
        print(f"❌ 错误: 目录不存在: {faces_dir}")
        return 0, 0

    # 获取所有图片文件
    image_files = list(faces_path.glob("*.jpg")) + list(faces_path.glob("*.png"))

    if not image_files:
        print(f"❌ 错误: 目录中没有图片文件: {faces_dir}")
        return 0, 0

    print(f"\n开始预计算 {len(image_files)} 个人脸特征...")
    print(f"检测模型: {model_type.upper()}")
    print(f"输出文件: {output_file}\n")

    encodings = []
    names = []
    success_count = 0
    fail_count = 0

    # 处理每张图片
    for image_path in tqdm(image_files, desc="处理进度"):
        try:
            # 加载图片
            image = face_recognition.load_image_file(str(image_path))

            # 提取人脸特征
            face_encodings = face_recognition.face_encodings(
                image,
                model=model_type
            )

            if face_encodings:
                # 取第一个人脸
                encodings.append(face_encodings[0])
                names.append(image_path.stem)
                success_count += 1
            else:
                print(f"\n⚠️  警告: 未检测到人脸: {image_path.name}")
                fail_count += 1

        except Exception as e:
            print(f"\n❌ 错误: 处理失败: {image_path.name} - {e}")
            fail_count += 1

    # 保存到缓存文件
    print(f"\n保存缓存文件...")

    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cache_data = {
        'encodings': encodings,
        'names': names,
        'model_type': model_type,
        'version': '1.0',
        'total_faces': len(encodings)
    }

    with open(output_file, 'wb') as f:
        pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # 统计信息
    file_size = output_path.stat().st_size
    file_size_kb = file_size / 1024

    print(f"\n{'='*50}")
    print(f"✅ 预计算完成")
    print(f"{'='*50}")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {fail_count} 个")
    print(f"  缓存文件: {output_file}")
    print(f"  文件大小: {file_size_kb:.2f} KB")
    print(f"{'='*50}\n")

    return success_count, fail_count


def verify_cache(cache_file: str) -> bool:
    """
    验证缓存文件是否有效

    Args:
        cache_file: 缓存文件路径

    Returns:
        是否有效
    """
    try:
        with open(cache_file, 'rb') as f:
            data = pickle.load(f)

        required_keys = ['encodings', 'names', 'version']
        for key in required_keys:
            if key not in data:
                print(f"❌ 错误: 缓存文件缺少字段: {key}")
                return False

        print(f"\n{'='*50}")
        print(f"缓存文件信息:")
        print(f"{'='*50}")
        print(f"  版本: {data['version']}")
        print(f"  模型: {data.get('model_type', 'unknown')}")
        print(f"  人脸数: {len(data['names'])}")
        print(f"  特征维度: {len(data['encodings'][0]) if data['encodings'] else 0}")
        print(f"{'='*50}\n")

        return True

    except Exception as e:
        print(f"❌ 错误: 无法读取缓存文件: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='人脸特征预计算脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置
  python scripts/precompute_encodings.py

  # 指定目录和输出文件
  python scripts/precompute_encodings.py \\
      --faces-dir models/known_faces \\
      --output data/face_encodings.pkl

  # 使用CNN模型（需GPU）
  python scripts/precompute_encodings.py --model cnn

  # 验证缓存文件
  python scripts/precompute_encodings.py --verify
        """
    )

    parser.add_argument(
        '--faces-dir',
        default=settings.KNOWN_FACES_DIR,
        help=f'人脸图片目录（默认: {settings.KNOWN_FACES_DIR}）'
    )

    parser.add_argument(
        '--output',
        default=settings.FACE_ENCODINGS_CACHE,
        help=f'输出缓存文件（默认: {settings.FACE_ENCODINGS_CACHE}）'
    )

    parser.add_argument(
        '--model',
        choices=['hog', 'cnn'],
        default=settings.FACE_MODEL,
        help=f'人脸检测模型（默认: {settings.FACE_MODEL}）'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='验证缓存文件是否有效'
    )

    args = parser.parse_args()

    # 验证模式
    if args.verify:
        if Path(args.output).exists():
            verify_cache(args.output)
        else:
            print(f"❌ 错误: 缓存文件不存在: {args.output}")
        return

    # 预计算模式
    success, fail = precompute_encodings(
        faces_dir=args.faces_dir,
        output_file=args.output,
        model_type=args.model
    )

    # 验证生成的缓存
    if success > 0:
        print("验证缓存文件...")
        verify_cache(args.output)

    # 退出码
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
