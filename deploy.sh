#!/bin/bash
set -e

echo "==========================================="
echo "人脸识别后端部署脚本"
echo "==========================================="

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/opt/face_recognition"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/face-recognition"
NGINX_CONF="/etc/nginx/sites-available/face-recognition"
SYSTEMD_SERVICE="/etc/systemd/system/face-recognition-worker@.service"

# 检查是否为root或有sudo权限
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    echo -e "${RED}❌ 错误: 需要root权限或sudo权限${NC}"
    exit 1
fi

# 1. 更新代码
echo -e "\n${YELLOW}📦 步骤1: 更新代码...${NC}"
cd $PROJECT_DIR
if [ -d ".git" ]; then
    git pull origin main
else
    echo "  ⚠️  警告: 不是Git仓库，跳过拉取"
fi

# 2. 安装/更新依赖
echo -e "\n${YELLOW}📚 步骤2: 安装依赖...${NC}"
source $VENV_DIR/bin/activate
pip install -r requirements.txt --upgrade

# 3. 预计算人脸特征（如果缓存不存在）
CACHE_FILE="$PROJECT_DIR/data/face_encodings.pkl"
if [ ! -f "$CACHE_FILE" ]; then
    echo -e "\n${YELLOW}🧠 步骤3: 预计算人脸特征（首次部署）...${NC}"
    python scripts/precompute_encodings.py
else
    echo -e "\n${GREEN}✅ 步骤3: 人脸特征缓存已存在，跳过${NC}"
    # 可选：验证缓存
    python scripts/precompute_encodings.py --verify
fi

# 4. 配置Nginx（如果未配置）
if [ ! -L "$NGINX_CONF" ]; then
    echo -e "\n${YELLOW}⚙️  步骤4: 配置Nginx...${NC}"
    sudo cp configs/nginx.conf $NGINX_CONF
    sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/face-recognition
    sudo nginx -t
    echo -e "${GREEN}  ✅ Nginx配置完成${NC}"
else
    echo -e "\n${GREEN}✅ 步骤4: Nginx已配置，跳过${NC}"
fi

# 5. 配置systemd服务（如果未配置）
if [ ! -f "$SYSTEMD_SERVICE" ]; then
    echo -e "\n${YELLOW}⚙️  步骤5: 配置systemd服务...${NC}"
    sudo cp configs/face-recognition-worker@.service $SYSTEMD_SERVICE
    sudo systemctl daemon-reload
    sudo systemctl enable face-recognition-worker@{1,2}
    echo -e "${GREEN}  ✅ systemd服务配置完成${NC}"
else
    echo -e "\n${GREEN}✅ 步骤5: systemd服务已配置${NC}"
    sudo systemctl daemon-reload
fi

# 6. 创建日志目录
if [ ! -d "$LOG_DIR" ]; then
    echo -e "\n${YELLOW}📝 步骤6: 创建日志目录...${NC}"
    sudo mkdir -p $LOG_DIR
    sudo chown -R www-data:www-data $LOG_DIR
else
    echo -e "\n${GREEN}✅ 步骤6: 日志目录已存在${NC}"
fi

# 7. 重启服务
echo -e "\n${YELLOW}🔄 步骤7: 重启服务...${NC}"
sudo systemctl restart face-recognition-worker@1
sudo systemctl restart face-recognition-worker@2
sudo systemctl reload nginx

# 等待服务启动
echo "  等待服务启动..."
sleep 3

# 8. 健康检查
echo -e "\n${YELLOW}🏥 步骤8: 健康检查...${NC}"
for port in 8001 8002; do
    if curl -f http://localhost:$port/health >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Worker $port: 运行正常${NC}"
    else
        echo -e "${RED}  ❌ Worker $port: 启动失败${NC}"
        sudo systemctl status face-recognition-worker@$(($port - 8000))
        exit 1
    fi
done

# 9. 显示状态
echo -e "\n${YELLOW}📊 步骤9: 服务状态...${NC}"
sudo systemctl status face-recognition-worker@1 --no-pager -l | head -10
sudo systemctl status face-recognition-worker@2 --no-pager -l | head -10

# 完成
echo -e "\n${GREEN}==========================================="
echo "✅ 部署完成！"
echo "==========================================="
echo "服务地址:"
echo "  - Worker 1: http://localhost:8001"
echo "  - Worker 2: http://localhost:8002"
echo "  - Nginx: http://localhost (或 https://api.your-domain.com)"
echo ""
echo "查看日志:"
echo "  sudo journalctl -u face-recognition-worker@1 -f"
echo "  sudo tail -f $LOG_DIR/app.log"
echo "==========================================${NC}"
