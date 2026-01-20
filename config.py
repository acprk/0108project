"""
配置管理模块
统一管理所有环境变量和配置项
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 环境
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    API_WORKERS: int = 2

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # 本地开发
        "https://your-app.vercel.app",  # 生产环境（需替换）
    ]

    # 人脸识别配置
    KNOWN_FACES_DIR: str = os.getenv(
        "KNOWN_FACES_DIR",
        "/home/luck/xzy/0108project/models/known_faces"
    )
    FACE_MODEL: str = "hog"  # "hog" 或 "cnn" (需GPU)
    FACE_TOLERANCE: float = 0.5  # 容差值，越小越严格

    # 性能配置
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    DETECTION_TIMEOUT: int = 5  # 检测超时（秒）
    ENABLE_FACE_CACHE: bool = True  # 启用人脸特征缓存

    # 缓存配置
    CACHE_DIR: str = os.getenv(
        "CACHE_DIR",
        "/home/luck/xzy/0108project/data"
    )
    FACE_ENCODINGS_CACHE: str = os.path.join(CACHE_DIR, "face_encodings.pkl")

    # 存储配置
    STORAGE_TYPE: str = "supabase"  # "local", "s3", "supabase"
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET: str = "known_faces"

    # S3 (Legacy)
    S3_BUCKET: str = ""
    S3_REGION: str = "ap-southeast-1"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "/var/log/face-recognition"

    # 安全配置
    RATE_LIMIT_PER_MINUTE: int = 60  # 每分钟最多请求数
    ENABLE_RATE_LIMIT: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()


def get_cors_origins() -> List[str]:
    """获取CORS允许的源列表"""
    origins = settings.CORS_ORIGINS.copy()

    # 如果有环境变量指定的额外源，添加进去
    extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
    if extra_origins:
        origins.extend(extra_origins.split(","))

    return origins


def is_production() -> bool:
    """判断是否为生产环境"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """判断是否为开发环境"""
    return settings.ENVIRONMENT == "development"


# 打印当前配置（仅开发环境）
if is_development():
    print("=" * 50)
    print("当前配置:")
    print(f"  环境: {settings.ENVIRONMENT}")
    print(f"  API端口: {settings.API_PORT}")
    print(f"  人脸模型: {settings.FACE_MODEL}")
    print(f"  人脸目录: {settings.KNOWN_FACES_DIR}")
    print(f"  缓存启用: {settings.ENABLE_FACE_CACHE}")
    print(f"  CORS源: {len(get_cors_origins())} 个")
    print("=" * 50)
