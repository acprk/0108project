# Vercel 部署指南

本项目已配置支持部署到 Vercel，并使用 Supabase 存储已知人脸数据。

## 前置要求

1.  **GitHub 账号**: 用于托管代码。
2.  **Vercel 账号**: 用于部署应用。
3.  **Supabase 账号**: 用于存储人脸图片。

## 步骤 1: 准备 Supabase

1.  登录 [Supabase](https://supabase.com/) 并创建一个新项目。
2.  进入 **Storage** (存储) 页面。
3.  创建一个新的 Bucket，命名为 `known_faces`。
    *   设为 Public (公开) 或 Private (私有) 均可，因为后端使用 API Key 访问。建议设为 Private 以保护隐私。
4.  进入 **Settings -> API**。
5.  复制 `Project URL` 和 `service_role` secret (注意：使用 `service_role` 可以绕过 RLS 权限策略，适合后端使用。请勿在前端暴露此 Key)。

## 步骤 2: 准备代码

1.  将代码提交到 GitHub 仓库。

## 步骤 3: 部署到 Vercel

1.  登录 Vercel，点击 **Add New... -> Project**。
2.  导入你的 GitHub 仓库。
3.  在 **Environment Variables** (环境变量) 部分，添加以下变量：
    *   `STORAGE_TYPE`: `supabase`
    *   `SUPABASE_URL`: 你的 Supabase Project URL
    *   `SUPABASE_KEY`: 你的 Supabase service_role key (或者 anon key，需配置 RLS)
    *   `SUPABASE_BUCKET`: `known_faces` (如果你改了名字)
4.  点击 **Deploy**。

## 注意事项

*   **构建时间**: 由于依赖 `dlib` 和 `face_recognition`，构建过程可能会比较慢。Vercel 的免费版函数大小限制为 250MB (解压后)，如果遇到大小超限问题，可能需要考虑使用 Docker 部署 (如 Render.com) 或寻找更轻量的人脸识别库。
*   **冷启动**: Serverless 函数会有冷启动时间，首次请求可能会稍慢，因为需要从 Supabase 加载已知人脸数据。
*   **摄像头权限**: 部署到 HTTPS (Vercel 默认支持) 后，浏览器才能正常调用摄像头。

## 本地开发

如果在本地开发想使用 Supabase，请在 `.env` 文件中设置上述环境变量。如果想使用本地文件存储，设置 `STORAGE_TYPE=local` (默认)。
