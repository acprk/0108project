# 人脸识别系统 - 阶段1部署指南

本指南包含前端（Vercel）和后端（AWS/阿里云）的完整部署步骤。

## 架构概览

```
Vercel (前端)                    AWS/阿里云 (后端)
┌──────────────┐                ┌─────────────────────┐
│  Next.js     │   HTTPS        │  FastAPI            │
│  - 摄像头     │───────────────▶│  - face_recognition │
│  - 图片上传   │   /api/detect  │  - 1001人脸特征     │
│  - 实时显示   │◀───────────────│  - Uvicorn + Nginx  │
└──────────────┘   JSON结果      └─────────────────────┘
```

## 一、前端部署到Vercel

### 1. 准备工作

```bash
cd /home/luck/xzy/face-recognition-frontend

# 安装依赖
npm install

# 本地测试
npm run dev
# 访问 http://localhost:3000
```

### 2. 部署到Vercel

**方式A：通过Git（推荐）**

```bash
# 1. 创建Git仓库
cd /home/luck/xzy/face-recognition-frontend
git init
git add .
git commit -m "Initial commit: Face Recognition Frontend"

# 2. 推送到GitHub
gh repo create face-recognition-frontend --public --source=. --remote=origin --push
# 或手动在GitHub创建仓库后推送

# 3. 在 Vercel Dashboard 导入项目
# https://vercel.com/new
# - 选择从GitHub导入
# - 选择face-recognition-frontend仓库
# - Framework Preset: Next.js（自动检测）
# - 点击Deploy
```

**方式B：通过CLI**

```bash
# 安装Vercel CLI
npm install -g vercel

# 登录Vercel
vercel login

# 部署
vercel --prod
```

### 3. 配置环境变量

在Vercel Dashboard中配置：

```
Settings > Environment Variables

BACKEND_URL = https://api.your-domain.com
```

### 4. 配置自定义域名（可选）

```
Settings > Domains

添加: face.your-domain.com
```

---

## 二、后端部署到AWS EC2

### 1. 创建EC2实例

**推荐配置**：
- 实例类型：t3.medium (2vCPU, 4GB RAM)
- AMI：Ubuntu 22.04 LTS
- 存储：30GB gp3
- 区域：Singapore (ap-southeast-1) - 靠近Vercel

**安全组规则**：
```
入站规则:
- SSH (22): 您的IP
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0
```

### 2. 连接服务器

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. 安装系统依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和开发工具
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y build-essential cmake pkg-config
sudo apt install -y libopencv-dev python3-opencv

# 安装Nginx
sudo apt install -y nginx

# 安装Certbot（SSL证书）
sudo apt install -y certbot python3-certbot-nginx
```

### 4. 上传项目代码

**方式A：使用rsync（推荐）**

```bash
# 在本地执行
rsync -avz --exclude 'venv' --exclude '__pycache__' \
    /home/luck/xzy/0108project/ ubuntu@your-ec2-ip:/tmp/face_recognition/

# 在服务器上
ssh ubuntu@your-ec2-ip
sudo mkdir -p /opt/face_recognition
sudo mv /tmp/face_recognition/* /opt/face_recognition/
sudo chown -R ubuntu:ubuntu /opt/face_recognition
```

**方式B：使用Git**

```bash
# 在服务器上
sudo mkdir -p /opt/face_recognition
sudo chown ubuntu:ubuntu /opt/face_recognition
cd /opt/face_recognition

# 从GitHub克隆
git clone https://github.com/your-username/face-recognition-backend.git .
```

### 5. 上传人脸数据

```bash
# 在本地执行
rsync -avz --progress \
    /home/luck/xzy/0108project/models/known_faces/ \
    ubuntu@your-ec2-ip:/opt/face_recognition/models/known_faces/

# 预计上传: 1001张图片，约39MB
```

### 6. 安装Python依赖

```bash
cd /opt/face_recognition

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 验证安装
python -c "import face_recognition; print('OK')"
```

### 7. 预计算人脸特征

```bash
# 首次运行需要预计算（约2-3分钟）
python scripts/precompute_encodings.py

# 输出示例:
# 开始预计算 1001 个人脸特征...
# 处理进度: 100%|████████████| 1001/1001 [02:34<00:00,  6.47it/s]
# ✅ 预计算完成
#   成功: 1001 个
#   失败: 0 个
#   缓存文件: data/face_encodings.pkl
#   文件大小: 512.34 KB
```

### 8. 配置环境变量

```bash
cd /opt/face_recognition

# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

配置内容：

```env
ENVIRONMENT=production
KNOWN_FACES_DIR=/opt/face_recognition/models/known_faces
CACHE_DIR=/opt/face_recognition/data
EXTRA_CORS_ORIGINS=https://your-app.vercel.app
```

### 9. 配置Nginx

```bash
# 复制Nginx配置
sudo cp configs/nginx.conf /etc/nginx/sites-available/face-recognition

# 编辑配置，替换域名
sudo nano /etc/nginx/sites-available/face-recognition
# 将 api.your-domain.com 替换为实际域名

# 启用配置
sudo ln -s /etc/nginx/sites-available/face-recognition /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 10. 申请SSL证书

```bash
# 使用Certbot自动配置SSL
sudo certbot --nginx -d api.your-domain.com

# 按提示操作:
# 1. 输入邮箱
# 2. 同意服务条款
# 3. 选择: Redirect HTTP to HTTPS (推荐)

# 测试自动续期
sudo certbot renew --dry-run
```

### 11. 配置systemd服务

```bash
# 复制服务配置
sudo cp configs/face-recognition-worker@.service /etc/systemd/system/

# 创建日志目录
sudo mkdir -p /var/log/face-recognition
sudo chown -R www-data:www-data /var/log/face-recognition

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable face-recognition-worker@{1,2}

# 启动服务
sudo systemctl start face-recognition-worker@{1,2}

# 检查状态
sudo systemctl status face-recognition-worker@1
sudo systemctl status face-recognition-worker@2
```

### 12. 验证部署

```bash
# 本地健康检查
curl http://localhost:8001/health
curl http://localhost:8002/health

# 预期输出:
# {"status":"healthy","known_faces_count":1001,"model":"hog"}

# Nginx健康检查
curl https://api.your-domain.com/health
```

### 13. 测试API

```bash
# 下载测试图片（从0108project）
wget https://your-server/test-image.jpg -O test.jpg

# 测试识别API
curl -X POST https://api.your-domain.com/api/detect \
  -F "file=@test.jpg" \
  | jq

# 预期输出:
# {
#   "success": true,
#   "face_count": 1,
#   "faces": [
#     {
#       "name": "张三",
#       "location": {...}
#     }
#   ]
# }
```

---

## 三、连接前后端

### 1. 更新前端环境变量

在Vercel Dashboard中：

```
Settings > Environment Variables

BACKEND_URL = https://api.your-domain.com
```

### 2. 重新部署前端

```bash
# 在Vercel Dashboard中点击 "Redeploy"
# 或推送新commit触发自动部署

git commit --allow-empty -m "Update backend URL"
git push
```

### 3. 更新后端CORS配置

```bash
# 在服务器上编辑 .env
sudo nano /opt/face_recognition/.env

# 添加Vercel域名
EXTRA_CORS_ORIGINS=https://your-app.vercel.app,https://face.your-domain.com

# 重启服务
sudo systemctl restart face-recognition-worker@{1,2}
```

### 4. 端到端测试

访问 `https://face.your-domain.com` 或 `https://your-app.vercel.app`

测试功能：
- ✅ 启动摄像头
- ✅ 实时人脸识别
- ✅ 图片上传识别
- ✅ 添加新人脸

---

## 四、监控与维护

### 查看日志

```bash
# 查看应用日志
sudo tail -f /var/log/face-recognition/app.log

# 查看systemd日志
sudo journalctl -u face-recognition-worker@1 -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/face-recognition-access.log
sudo tail -f /var/log/nginx/face-recognition-error.log
```

### 重启服务

```bash
# 重启所有服务
sudo systemctl restart face-recognition-worker@{1,2}
sudo systemctl reload nginx

# 或使用部署脚本
cd /opt/face_recognition
./deploy.sh
```

### 更新代码

```bash
# 在服务器上
cd /opt/face_recognition
git pull origin main
./deploy.sh
```

---

## 五、故障排除

### 问题1：摄像头权限被拒绝

**解决方案**：
- 确保前端使用HTTPS（Vercel自动提供）
- 检查浏览器权限设置
- 尝试不同浏览器（Chrome推荐）

### 问题2：CORS错误

**解决方案**：
```bash
# 检查后端CORS配置
cd /opt/face_recognition
cat .env | grep CORS

# 更新配置
nano .env
# 添加前端域名到EXTRA_CORS_ORIGINS

# 重启服务
sudo systemctl restart face-recognition-worker@{1,2}
```

### 问题3：人脸识别失败

**解决方案**：
```bash
# 检查缓存文件
ls -lh /opt/face_recognition/data/face_encodings.pkl

# 重新预计算
python scripts/precompute_encodings.py

# 重启服务
sudo systemctl restart face-recognition-worker@{1,2}
```

### 问题4：服务启动失败

**解决方案**：
```bash
# 查看详细错误
sudo systemctl status face-recognition-worker@1 -l

# 检查日志
sudo journalctl -u face-recognition-worker@1 --no-pager -n 50

# 手动测试
cd /opt/face_recognition
source venv/bin/activate
python main.py
```

---

## 六、成本估算

### 开发成本
- **阶段1开发**: 已完成

### 运营成本（月）
| 项目 | 费用 |
|------|------|
| AWS EC2 t3.medium | $30 |
| 域名 | $12/年 ≈ $1 |
| SSL证书 | $0 (Let's Encrypt) |
| Vercel | $0 (Hobby) 或 $20 (Pro) |
| **总计** | **$31-51/月** |

---

## 七、下一步

阶段1部署完成后，可以开始：

1. **性能优化**
   - 监控响应时间
   - 优化图片压缩
   - CDN加速

2. **准备阶段2**
   - 准备FPSI C++编译环境
   - 测试0109project的隐私保护功能
   - 设计WebSocket集成方案

3. **生产环境完善**
   - 设置监控告警（Prometheus + Grafana）
   - 配置备份策略
   - 添加用户认证

---

## 支持

遇到问题请查看：
- 项目计划文件：`/home/luck/.claude/plans/fluttering-wondering-bubble.md`
- 主README：`/home/luck/xzy/0108project/README.md`
