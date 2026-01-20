#!/bin/bash

# 人脸识别系统启动脚本

echo "================================"
echo "  AI 人脸识别系统"
echo "================================"
echo ""

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
    echo ""
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate

# 检查依赖
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "⚠️  依赖未安装，正在安装..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✓ 依赖安装完成"
    echo ""
fi

# 确保必要的目录存在
mkdir -p models/known_faces
mkdir -p uploads

echo "================================"
echo "🚀 启动服务..."
echo "================================"
echo ""
echo "访问地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python main.py
