# SignFlow AI 手机端与微信小程序使用手册

## 当前交付

`sign-app` 已升级为 Vue 3 + uni-app CLI 工程，活动源码位于 `sign-app/src`。它与桌面 Web
共用 `/api/v1`、任务数据和账号体系，可输出：

- 手机 H5：`sign-app/dist/build/h5`
- 微信小程序：`sign-app/dist/build/mp-weixin`

项目复用已登记的 `SignFlow Base · 2.1-local` 权重进行推理，不执行训练，不下载来源或授权
不明确的第三方模型，也不会把用户素材自动加入训练集。

## 本机启动

后端本地调试模式：

```powershell
cd web_project
$env:ENABLE_CAMERA_WEBSOCKET = "1"
$env:CELERY_TASK_ALWAYS_EAGER = "1"
$env:DETECTION_AUTO_DISPATCH = "1"
uvicorn web_project.asgi:application --host 0.0.0.0 --port 8001
```

手机 H5：

```powershell
cd sign-app
pnpm install
pnpm dev:h5
```

电脑浏览器可使用 `http://127.0.0.1:5173`。手机与电脑处于同一 Wi-Fi 时，使用电脑的局域网
IP，例如：

```text
H5：http://192.168.31.80:5173
API：http://192.168.31.80:8001
```

局域网 IP 会随网络变化。可通过 `ipconfig` 重新确认，再到手机端“我的 → 服务地址”修改。
若手机无法连接，检查 Windows 防火墙、路由器的客户端隔离设置，以及后端是否监听
`0.0.0.0:8001`。

## 构建微信小程序

```powershell
cd sign-app
pnpm build:mp-weixin
```

在微信开发者工具中选择“导入项目”，目录填写：

```text
sign-app/dist/build/mp-weixin
```

本地联调可在微信开发者工具中按团队规则临时关闭合法域名校验；这只用于开发。正式发布前必须：

1. 将 API 部署到已备案的 HTTPS 域名；
2. 将同一域名加入微信后台的 `request` 和 `uploadFile` 合法域名；
3. 将 WSS 域名加入 `socket` 合法域名；
4. 配置有效 TLS 证书、摄像头隐私说明和用户授权；
5. 在 `.env.production` 设置 `VITE_SIGNFLOW_API_ORIGIN=https://api.example.com` 后重新构建；
6. 使用项目所属微信公众平台账号上传、审核并发布。

代码和构建产物不包含微信后台私钥。上传和发布必须由项目所属微信开发者账号完成。

## 真实识别链路

### 图片与视频

1. 客户端读取模型目录；
2. 通过 multipart 上传文件并创建检测任务；
3. 后端校验文件类型、签名和大小；
4. 本地调试环境可使用 eager 模式调用现有 YOLO 权重；
5. 客户端轮询任务状态并展示真实标签、置信度和模型版本；
6. 用户可保存结果，再从结果中心打开详情。

### 微信摄像头

1. 客户端申请短时一次性摄像头票据；
2. 使用 `wss://.../ws/camera` 建立受限会话；
3. 前置摄像头顺序采集压缩帧，不并发堆积；
4. 后端限制帧率、消息大小、单帧大小、会话时长和单用户会话数；
5. 服务返回真实帧级标签，客户端汇总后保存为识别任务。

H5 端支持真实图片和视频识别；实时摄像头模式使用微信小程序的原生 camera 能力。

## 登录与隐私

- 密码只用于当前登录请求，不写入 URL、日志或本地存储；
- access token 只存在运行内存；
- 小程序无法依赖浏览器 HttpOnly Cookie，因此 refresh token 保存在客户端并通过 JSON
  刷新接口换取短时 access token；
- 服务地址会拒绝携带用户名、密码、查询参数或非 HTTP(S) 协议的值；
- 账号只可访问自己的任务和结果；
- 用户素材默认只用于当前识别，不会自动进入训练集。

生产环境若需要更高安全等级，可使用微信登录临时码换取服务端会话，并将 refresh token
迁移到平台安全存储或设备绑定会话。

## 验证命令

```powershell
cd sign-app
pnpm run test
```

验收应至少覆盖：登录刷新、图片上传、视频上传、任务失败与重试、结果保存、详情页、弱网提示、
真机相机授权、WebSocket 中断恢复，以及 iOS/Android 微信真机。
