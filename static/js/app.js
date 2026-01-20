// 全局变量
let video = null;
let canvas = null;
let ctx = null;
let stream = null;
let isDetecting = false;
let detectionInterval = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 获取元素
    video = document.getElementById('video');
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');

    // 显示访问提示
    showAccessHint();

    // 初始化标签页切换
    initTabs();

    // 初始化实时识别
    initRealtimeDetection();

    // 初始化图片上传
    initImageUpload();

    // 初始化人脸管理
    initFaceManagement();
});

// 显示访问提示
function showAccessHint() {
    const hintSpan = document.getElementById('accessHint');
    const isSecure = window.location.protocol === 'https:' ||
                    window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1';

    if (!isSecure) {
        hintSpan.innerHTML = '<br><strong style="color: #d9534f;">当前使用 IP 地址访问，浏览器会阻止摄像头！</strong><br>' +
                            '请使用: <a href="http://localhost:8000" style="color: #667eea; font-weight: bold;">http://localhost:8000</a>';
    } else {
        hintSpan.innerHTML = '使用 Chrome/Firefox/Edge 浏览器，并允许摄像头权限';
    }
}

// 标签页切换
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;

            // 切换按钮状态
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // 切换内容
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(targetTab).classList.add('active');

            // 如果切换到管理页面，加载已知人脸列表
            if (targetTab === 'manage') {
                loadKnownFaces();
            }

            // 如果切换离开实时识别，停止检测
            if (targetTab !== 'realtime' && isDetecting) {
                stopDetection();
            }
        });
    });
}

// 实时识别功能
function initRealtimeDetection() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');

    startBtn.addEventListener('click', startDetection);
    stopBtn.addEventListener('click', stopDetection);
}

async function startDetection() {
    try {
        updateStatus('正在启动摄像头...', 'info');

        // 检查浏览器是否支持摄像头访问
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showCameraError('您的浏览器不支持摄像头访问，请使用 Chrome、Firefox 或 Edge 浏览器');
            return;
        }

        // 检查是否为 HTTPS 或 localhost
        const isSecure = window.location.protocol === 'https:' ||
                        window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1';

        if (!isSecure) {
            showCameraError(
                '摄像头访问需要安全连接！<br><br>' +
                '<strong>解决方案：</strong><br>' +
                '1. 使用本机访问: <a href="http://localhost:8000" target="_blank">http://localhost:8000</a><br>' +
                '2. 或使用 HTTPS 访问<br><br>' +
                '<small>当前地址: ' + window.location.href + '</small>'
            );
            return;
        }

        // 请求摄像头权限
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        video.srcObject = stream;
        video.play();

        // 等待视频加载
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            isDetecting = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;

            updateStatus('正在识别中...', 'success');

            // 开始定期检测（每500ms检测一次）
            detectionInterval = setInterval(detectFromVideo, 500);
        };

    } catch (error) {
        console.error('启动摄像头失败:', error);

        let errorMsg = '无法访问摄像头';

        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMsg = '摄像头权限被拒绝！<br><br>' +
                      '<strong>解决方法：</strong><br>' +
                      '1. 点击浏览器地址栏左侧的 🔒 或 ⓘ 图标<br>' +
                      '2. 找到"摄像头"权限设置<br>' +
                      '3. 选择"允许"<br>' +
                      '4. 刷新页面后重试';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            errorMsg = '未检测到摄像头设备<br><br>请确保：<br>1. 摄像头已连接<br>2. 驱动程序正常';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            errorMsg = '摄像头被其他应用占用<br><br>请关闭其他使用摄像头的应用';
        } else if (error.name === 'OverconstrainedError') {
            errorMsg = '摄像头不支持请求的分辨率<br><br>正在尝试降低分辨率...';
            // 尝试使用更低的分辨率
            retryWithLowerResolution();
            return;
        } else if (error.name === 'TypeError') {
            errorMsg = '浏览器不支持摄像头访问<br><br>请使用 Chrome、Firefox 或 Edge 浏览器';
        }

        showCameraError(errorMsg + '<br><br><small>错误详情: ' + error.message + '</small>');
    }
}

// 尝试使用更低的分辨率
async function retryWithLowerResolution() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });

        video.srcObject = stream;
        video.play();

        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            isDetecting = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            updateStatus('正在识别中（低分辨率模式）...', 'success');
            detectionInterval = setInterval(detectFromVideo, 500);
        };
    } catch (err) {
        showCameraError('即使降低分辨率也无法访问摄像头<br>错误: ' + err.message);
    }
}

// 显示摄像头错误提示
function showCameraError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="alert alert-error" style="text-align: left; line-height: 1.8;">
            <h3 style="margin-bottom: 10px;">⚠️ 摄像头访问失败</h3>
            <div>${message}</div>
        </div>
    `;
    updateStatus('摄像头启动失败', 'error');
}

function stopDetection() {
    isDetecting = false;

    // 停止检测间隔
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }

    // 停止视频流
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    // 清空视频
    if (video) {
        video.srcObject = null;
    }

    // 清空覆盖层
    document.getElementById('face-overlay').innerHTML = '';

    // 更新按钮状态
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;

    updateStatus('已停止识别', 'info');
}

async function detectFromVideo() {
    if (!isDetecting) return;

    try {
        // 将视频帧绘制到 canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // 获取 base64 图片数据
        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        // 发送到后端进行检测
        const formData = new FormData();
        formData.append('image_data', imageData);

        const response = await fetch('/api/detect_stream', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // 更新显示
            displayRealtimeResults(result);
        }

    } catch (error) {
        console.error('检测失败:', error);
    }
}

function displayRealtimeResults(result) {
    const overlay = document.getElementById('face-overlay');
    overlay.innerHTML = '';

    if (result.face_count > 0) {
        // 计算视频元素的实际显示尺寸
        const videoRect = video.getBoundingClientRect();
        const scaleX = videoRect.width / canvas.width;
        const scaleY = videoRect.height / canvas.height;

        result.faces.forEach(face => {
            const loc = face.location;

            // 创建人脸框
            const box = document.createElement('div');
            box.style.position = 'absolute';
            box.style.border = face.name === 'Unknown' ? '3px solid red' : '3px solid lime';
            box.style.left = (loc.left * scaleX) + 'px';
            box.style.top = (loc.top * scaleY) + 'px';
            box.style.width = ((loc.right - loc.left) * scaleX) + 'px';
            box.style.height = ((loc.bottom - loc.top) * scaleY) + 'px';

            // 创建标签
            const label = document.createElement('div');
            label.textContent = face.name;
            label.style.position = 'absolute';
            label.style.bottom = '-30px';
            label.style.left = '0';
            label.style.background = face.name === 'Unknown' ? 'red' : 'lime';
            label.style.color = face.name === 'Unknown' ? 'white' : 'black';
            label.style.padding = '4px 8px';
            label.style.fontSize = '14px';
            label.style.fontWeight = 'bold';
            label.style.borderRadius = '3px';

            box.appendChild(label);
            overlay.appendChild(box);
        });

        updateStatus(`检测到 ${result.face_count} 张人脸`, 'success');
    } else {
        updateStatus('未检测到人脸', 'info');
    }
}

// 图片上传功能
function initImageUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');

    uploadBox.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFileSelect);

    // 拖拽上传
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#764ba2';
    });

    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#667eea';
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#667eea';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

async function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showAlert('请选择图片文件', 'error');
        return;
    }

    const resultDiv = document.getElementById('uploadResult');
    resultDiv.innerHTML = '<p>正在处理...</p>';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/detect', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // 显示结果图片
            resultDiv.innerHTML = `
                <img src="${result.result_image}" alt="识别结果">
                <div class="result-info">
                    <h3>识别结果</h3>
                    <p>检测到 <strong>${result.face_count}</strong> 张人脸</p>
                    ${result.faces.map(face => `
                        <div class="result-item">
                            <strong>${face.name}</strong>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            resultDiv.innerHTML = '<p class="alert alert-error">处理失败</p>';
        }

    } catch (error) {
        console.error('上传失败:', error);
        resultDiv.innerHTML = '<p class="alert alert-error">上传失败，请重试</p>';
    }
}

// 人脸管理功能
function initFaceManagement() {
    const addFaceBox = document.getElementById('addFaceBox');
    const faceFileInput = document.getElementById('faceFileInput');
    const addFaceBtn = document.getElementById('addFaceBtn');

    addFaceBox.addEventListener('click', () => faceFileInput.click());

    faceFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            addFaceBox.querySelector('p').textContent = file.name;
        }
    });

    addFaceBtn.addEventListener('click', addNewFace);
}

async function addNewFace() {
    const nameInput = document.getElementById('faceName');
    const fileInput = document.getElementById('faceFileInput');

    const name = nameInput.value.trim();
    const file = fileInput.files[0];

    if (!name) {
        showAlert('请输入姓名', 'error');
        return;
    }

    if (!file) {
        showAlert('请选择图片', 'error');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('file', file);

        const response = await fetch('/api/add_face', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');
            nameInput.value = '';
            fileInput.value = '';
            document.getElementById('addFaceBox').querySelector('p').textContent = '选择人脸图片';
            loadKnownFaces();
        } else {
            showAlert('添加失败', 'error');
        }

    } catch (error) {
        console.error('添加人脸失败:', error);
        showAlert('添加失败，请重试', 'error');
    }
}

async function loadKnownFaces() {
    const listDiv = document.getElementById('knownFacesList');
    listDiv.innerHTML = '<p>加载中...</p>';

    try {
        const response = await fetch('/api/known_faces');
        const result = await response.json();

        if (result.success && result.known_faces.length > 0) {
            listDiv.innerHTML = result.known_faces.map(name => `
                <div class="face-card">
                    <p>${name}</p>
                </div>
            `).join('');
        } else {
            listDiv.innerHTML = '<p>暂无已知人脸，请先添加</p>';
        }

    } catch (error) {
        console.error('加载失败:', error);
        listDiv.innerHTML = '<p class="alert alert-error">加载失败</p>';
    }
}

// 工具函数
function updateStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = 'status';

    if (type === 'success') {
        statusDiv.style.background = '#d4edda';
        statusDiv.style.color = '#155724';
    } else if (type === 'error') {
        statusDiv.style.background = '#f8d7da';
        statusDiv.style.color = '#721c24';
    } else {
        statusDiv.style.background = '#e9ecef';
        statusDiv.style.color = '#333';
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.tab-content.active');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
