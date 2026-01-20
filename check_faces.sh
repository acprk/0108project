#!/bin/bash

echo "==================================="
echo "检查人脸识别系统状态"
echo "==================================="
echo ""

# 检查服务状态
echo "1. 服务状态："
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ 服务正在运行"
else
    echo "   ✗ 服务未运行"
    exit 1
fi

echo ""
echo "2. 已加载的人脸："
curl -s http://localhost:8000/api/known_faces | python3 -m json.tool

echo ""
echo "3. 人脸文件列表："
face_count=$(ls models/known_faces/*.jpg 2>/dev/null | wc -l)
if [ $face_count -eq 0 ]; then
    echo "   ✗ 没有人脸文件"
    echo ""
    echo "请通过 Web 界面 (http://localhost:8000) 添加你的照片！"
else
    echo "   ✓ 找到 $face_count 个人脸文件："
    ls -lh models/known_faces/*.jpg
fi

echo ""
echo "==================================="
