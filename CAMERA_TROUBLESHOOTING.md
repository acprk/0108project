# 摄像头访问故障排除指南

## 问题：无法访问摄像头

### 最常见原因：使用 IP 地址访问（非 localhost）

**现象**：点击"启动摄像头"后提示"无法访问摄像头，请检查权限设置"

**原因**：出于安全考虑，现代浏览器只允许在以下情况下访问摄像头：
- HTTPS 连接
- localhost（本机）访问
- 127.0.0.1 访问

**✅ 解决方案（推荐）：**

### 方法一：使用 localhost 访问（最简单）

如果你在本机浏览器访问，请使用：
```
http://localhost:8000
```

而不是：
```
http://192.168.111.172:8000  ❌ 会被浏览器阻止
```

### 方法二：配置 HTTPS（用于远程访问）

如果需要在其他设备上访问，需要配置 HTTPS：

**1. 生成自签名证书**

```bash
cd /home/luck/xzy/0108project

# 生成私钥和证书
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=localhost"
```

**2. 修改启动配置**

编辑 `main.py` 最后一行：

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="key.pem",      # 添加这行
        ssl_certfile="cert.pem",    # 添加这行
        log_level="info"
    )
```

**3. 重启服务**

```bash
pkill -f "python main.py"
venv/bin/python main.py
```

**4. 使用 HTTPS 访问**

```
https://192.168.111.172:8000
```

⚠️ 首次访问会提示证书不安全，点击"高级" → "继续访问"即可。

---

## 其他常见问题

### 问题 2：浏览器权限被拒绝

**症状**：点击"启动摄像头"后弹出权限请求，点击了"拒绝"或"阻止"

**解决方法**：

**Chrome / Edge：**
1. 点击地址栏左侧的 **🔒** 或 **ⓘ** 图标
2. 找到"摄像头"设置
3. 选择"允许"
4. 刷新页面（F5）
5. 再次点击"启动摄像头"

**Firefox：**
1. 点击地址栏左侧的 **🔒** 图标
2. 点击"连接安全"旁边的 **>** 箭头
3. 点击"更多信息"
4. 切换到"权限"标签页
5. 找到"使用摄像头"，取消勾选"使用默认设置"
6. 选择"允许"
7. 刷新页面

**Safari (macOS)：**
1. Safari 菜单 → 偏好设置
2. 网站标签页
3. 左侧选择"摄像头"
4. 找到你的网站，设置为"允许"
5. 刷新页面

---

### 问题 3：未检测到摄像头设备

**症状**：提示"未检测到摄像头设备"

**检查清单**：

1. **摄像头是否连接**
   - 外接摄像头：检查 USB 连接
   - 笔记本内置摄像头：确保未被物理遮挡

2. **检查系统设置（Windows）**
   ```
   设置 → 隐私 → 摄像头
   - 确保"允许应用访问你的摄像头"已开启
   - 确保"允许桌面应用访问你的摄像头"已开启
   ```

3. **检查系统设置（macOS）**
   ```
   系统偏好设置 → 安全性与隐私 → 摄像头
   - 勾选浏览器（Chrome/Firefox/Safari）
   ```

4. **检查系统设置（Linux）**
   ```bash
   # 检查是否识别摄像头
   ls /dev/video*

   # 应该看到 /dev/video0 等设备

   # 检查权限
   ls -l /dev/video0

   # 如果没有权限，添加当前用户到 video 组
   sudo usermod -a -G video $USER
   # 注销后重新登录
   ```

---

### 问题 4：摄像头被其他应用占用

**症状**：提示"摄像头被其他应用占用"

**解决方法**：

关闭以下可能占用摄像头的应用：
- Zoom / Teams / Skype 等视频会议软件
- OBS / Streamlabs 等直播软件
- 其他浏览器标签页中的视频应用
- 视频录制软件

**Windows - 查看占用进程：**
```
任务管理器 → 性能 → 打开资源监视器 → 关联的句柄 → 搜索 "video"
```

**macOS - 查看占用进程：**
```bash
sudo lsof | grep "AppleCamera"
```

**Linux - 查看占用进程：**
```bash
sudo lsof /dev/video0
```

---

### 问题 5：浏览器不支持

**症状**：提示"您的浏览器不支持摄像头访问"

**解决方法**：

使用以下现代浏览器之一：
- ✅ Google Chrome 53+
- ✅ Microsoft Edge 79+
- ✅ Mozilla Firefox 36+
- ✅ Safari 11+
- ✅ Opera 40+

**不支持的浏览器：**
- ❌ Internet Explorer（任何版本）
- ❌ 部分旧版移动浏览器

---

### 问题 6：摄像头分辨率不支持

**症状**：提示"摄像头不支持请求的分辨率"

**说明**：系统会自动尝试降低分辨率（1280x720 → 640x480）

如果仍然失败，可能是摄像头太旧或损坏。

---

## 测试摄像头

可以使用以下网站测试摄像头是否正常：

1. **WebRTC 测试页面**
   ```
   https://webrtc.github.io/samples/src/content/devices/input-output/
   ```

2. **浏览器测试工具**
   - Chrome: chrome://settings/content/camera
   - Firefox: about:preferences#privacy → 权限 → 摄像头

3. **本地测试（Linux）**
   ```bash
   # 安装测试工具
   sudo apt-get install cheese

   # 打开摄像头测试
   cheese
   ```

---

## 快速诊断脚本

在浏览器控制台（F12 → Console）运行：

```javascript
// 检测浏览器支持
console.log('浏览器支持:', 'mediaDevices' in navigator);

// 检测访问协议
console.log('访问协议:', window.location.protocol);
console.log('主机名:', window.location.hostname);

// 尝试获取设备列表
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    const cameras = devices.filter(d => d.kind === 'videoinput');
    console.log('检测到摄像头数量:', cameras.length);
    cameras.forEach((cam, i) => {
      console.log(`摄像头 ${i+1}:`, cam.label || '未授权');
    });
  })
  .catch(err => console.error('错误:', err));
```

---

## 仍然无法解决？

请提供以下信息以便进一步诊断：

1. **操作系统**：Windows / macOS / Linux（版本）
2. **浏览器**：Chrome / Firefox / Edge（版本号）
3. **访问地址**：localhost 还是 IP 地址
4. **错误信息**：完整的错误提示
5. **控制台日志**：按 F12 打开开发者工具，复制 Console 中的错误

---

**最后更新**：2026-01-08
