#!/bin/bash
# 人脸识别系统启动脚本

echo "========================================"
echo "人脸识别系统 - 启动脚本"
echo "========================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    echo "请先运行: python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 停止旧服务
echo "停止旧服务..."
pkill -f "python main.py" 2>/dev/null
sleep 2

# 检查端口占用
echo "检查端口8001..."
if ss -tlnp | grep -q ":8001 "; then
    echo "⚠️  警告: 端口8001已被占用"
    echo "正在尝试释放..."
    PORT_PID=$(ss -tlnp | grep ":8001 " | grep -oP 'pid=\K\d+' | head -1)
    if [ -n "$PORT_PID" ]; then
        kill -9 $PORT_PID 2>/dev/null
        sleep 1
    fi
fi

# 启动服务
echo "启动服务..."
nohup venv/bin/python main.py > service.log 2>&1 &
SERVICE_PID=$!

echo ""
echo "等待服务启动（约2-3分钟，加载1001个人脸）..."
sleep 5

# 检查服务状态
if ps -p $SERVICE_PID > /dev/null; then
    echo "✓ 服务进程已启动 (PID: $SERVICE_PID)"
else
    echo "❌ 服务启动失败，请查看 service.log"
    exit 1
fi

# 等待服务就绪
echo "正在加载人脸数据..."
for i in {1..30}; do
    sleep 5
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo ""
        echo "========================================"
        echo "✓ 服务启动成功！"
        echo "========================================"
        echo ""

        # 获取人脸数量
        FACE_COUNT=$(curl -s http://localhost:8001/health | grep -oP '"known_faces_count":\K\d+')

        echo "服务信息:"
        echo "  - 服务端口: 8001"
        echo "  - 已加载人脸: $FACE_COUNT 个"
        echo "  - 识别阈值: tolerance=0.5"
        echo ""
        echo "访问地址:"
        echo "  - 本地访问: http://localhost:8001"
        echo "  - 局域网访问: http://192.168.111.172:8001"
        echo "  - 摄像头客户端: http://192.168.111.172:8001/static/local_camera_client.html"
        echo ""
        echo "管理命令:"
        echo "  - 查看日志: tail -f service.log"
        echo "  - 停止服务: pkill -f 'python main.py'"
        echo "  - 查看状态: curl http://localhost:8001/health"
        echo ""
        exit 0
    fi
    echo -n "."
done

echo ""
echo "⚠️  服务启动超时，请检查日志:"
echo "tail -f service.log"
exit 1
