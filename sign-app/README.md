# SignFlow AI 移动端

这是 SignFlow AI 的 Vue 3 + uni-app 客户端，同一套活动源码可构建为手机 H5 和微信小程序。
图片、视频和微信摄像头模式均调用后端真实任务接口，复用项目现有模型，不执行训练，也不会把
用户素材自动加入训练集。

## 能力

- 安全登录、注册和令牌刷新，不保存密码；
- 真实图片、视频上传，任务进度轮询、取消、保存和详情查看；
- 微信小程序前置摄像头采帧，通过一次性 WebSocket 票据完成实时识别；
- 结果中心、模型信息、服务健康状态和可配置服务地址；
- H5 与微信小程序双端构建。

## 本地运行

```powershell
pnpm install
pnpm dev:h5
```

H5 默认访问 `http://127.0.0.1:5173`，识别服务默认访问
`http://127.0.0.1:8001`。也可复制 `.env.example` 并修改
`VITE_SIGNFLOW_API_ORIGIN`。

## 微信小程序

```powershell
pnpm build:mp-weixin
```

把 `dist/build/mp-weixin` 导入微信开发者工具。真机不能访问电脑的
`127.0.0.1`；同一 Wi-Fi 调试时，在“我的 → 服务地址”填写电脑局域网地址。

正式发布必须使用已备案且加入微信后台白名单的 HTTPS/WSS 域名，并配置 `request`、
`uploadFile`、`socket` 合法域名、摄像头隐私说明和用户授权。

完整说明见 [手机端与微信小程序使用手册](../docs/mobile-mini-program.md)。

## 验证

```powershell
pnpm run test
```

命令会运行移动端单元测试，并分别构建 H5 与微信小程序。
