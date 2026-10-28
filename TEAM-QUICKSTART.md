# SignFlow AI 队友交付包：运行说明

本压缩包是可直接开发、演示和继续交付的运行源码包。它包含桌面 Web、手机 H5 / 微信小程序、Django 后端、数据库迁移、自动化测试、部署配置，以及本地 CSL / ASL 手语识别权重。

> 本项目只加载已有模型执行推理，不会训练模型，也不会把上传的图片或视频自动加入训练集。

## 一、最快启动方式（Windows）

### 1. 准备环境

请先安装：

- Windows 10 / 11 64 位；
- Python 3.11 或 3.12 64 位，安装时勾选 `Add Python to PATH`；
- Node.js 20 或更高版本（推荐当前 LTS）；
- 可访问 npm 与 PyPI 的网络；
- 至少 6 GB 可用磁盘空间。压缩包小于 200 MB，但 PyTorch、OpenCV 和前端依赖解压安装后会占用数 GB。

不需要安装 MySQL、Redis、MinIO，也不需要显卡。首次体验默认使用 SQLite、本地文件存储、Celery eager 模式和 CPU 推理。

### 2. 解压

把 ZIP 完整解压到一个普通本地目录，推荐：

```text
D:\SignFlow-AI
```

不要在 ZIP 压缩包预览窗口中直接双击脚本，也尽量避免过长路径。

### 3. 一键安装

双击根目录中的：

```text
setup-windows.cmd
```

它会依次完成：

1. 检查 Python、Node.js、Corepack / pnpm 和两个核心模型；
2. 创建项目独立的 `.venv`；
3. 安装固定版本的后端与真实推理依赖；
4. 安装桌面 Web 和手机端依赖；
5. 创建本地 SQLite 数据库并执行迁移；
6. 创建随机密码管理员；
7. 登记 ASL-80 与 CSL-37 两套本地模型及其评测卡。

首次安装通常需要 5–20 分钟，主要取决于 PyTorch 下载速度。安装过程不进行任何模型训练。

### 4. 查看登录账号

安装完成后，随机管理员账号保存在：

```text
web_project\.demo-credentials
```

在项目根目录打开 PowerShell，可以执行：

```powershell
Get-Content .\web_project\.demo-credentials
```

默认用户名通常是 `signflow_admin`，密码以该文件中的实际内容为准。这个文件只供本机使用，不要发到群聊、截图投屏或提交到 Git。

### 5. 一键运行

双击：

```text
start-windows.cmd
```

脚本会启动三个后台进程、等待健康检查通过，并自动打开桌面 Web 与手机 H5：

| 入口 | 地址 | 用途 |
|---|---|---|
| 桌面 Web | `http://127.0.0.1:8080/` | 完整产品、识别工作台、结果中心、数据洞察和管理端 |
| 手机 H5 | `http://127.0.0.1:5173/#/` | 手机布局与移动识别流程 |
| 后端就绪检查 | `http://127.0.0.1:8001/health/ready` | 数据库、存储与服务状态 |
| 后端存活检查 | `http://127.0.0.1:8001/health/live` | 后端进程状态 |

后台日志写在 `.team-runtime`，不会进入交付包或 Git。

### 6. 停止和检查

- 双击 `check-windows.cmd`：检查三个入口是否可访问；
- 双击 `stop-windows.cmd`：只终止启动脚本记录的 SignFlow 进程，不会按端口误杀其他程序。

## 二、真实识别演示

### 图片识别

1. 登录桌面 Web；
2. 进入“识别工作台”；
3. 选择“图片”；
4. 选择识别语言 / 模型：
   - `SignFlow Base`：美国手语 ASL，80 类；
   - `SignFlow CSL 37`：中国手语 CSL，37 类；
5. 上传 JPG、PNG 或 WebP 图片；
6. 提交任务并等待“已完成”；
7. 在右侧结果或“结果中心”查看标签、置信度、模型版本、参数、文件哈希和识别版本。

### 视频识别

1. 在工作台切换到“视频”；
2. 上传 MP4 / WebM 等受支持视频；
3. 选择 CSL 或 ASL 模型；
4. 提交后查看逐帧检测、标签时间线和汇总结果。

CPU 首次识别会加载模型，因此第一次任务比后续任务慢。演示前建议用一张图片预热对应模型。

### 实时摄像头

1. 使用 Chrome 或 Edge 打开桌面 Web；
2. 进入“实时摄像头”，允许浏览器访问摄像头；
3. 选择模型后启动识别；
4. 页面通过一次性 WebSocket 票据发送受限帧率画面，并显示实时标签。

摄像头只允许在 `localhost` 或 HTTPS 安全来源中调用。如果浏览器拒绝权限，请在地址栏左侧的网站权限中重新允许。

## 三、手机或同一局域网调试

先停止已有服务，然后在项目根目录 PowerShell 中运行：

```powershell
.\scripts\team\start.ps1 -Lan
```

脚本会显示电脑的局域网地址，例如：

```text
Phone H5  : http://192.168.1.20:5173/#/
Phone API : http://192.168.1.20:8001
```

手机与电脑必须连接同一个 Wi-Fi。首次登录时，把手机端“服务器地址”填写为脚本显示的 `Phone API`。如果手机无法访问，请允许 Python 与 Node.js 通过 Windows 防火墙的“专用网络”。

## 四、微信小程序构建

安装完成后执行：

```powershell
cd sign-app
corepack pnpm run build:mp-weixin
```

构建结果位于：

```text
sign-app\dist\build\mp-weixin
```

将该目录导入微信开发者工具。正式发布必须配置合法 AppID、HTTPS API 域名、微信后台 request / uploadFile / socket 合法域名和隐私声明。详细说明见 `docs/mobile-mini-program.md`。

## 五、手动运行命令

一键脚本不可用时，可在项目根目录分别打开三个 PowerShell 窗口。

后端：

```powershell
$env:DJANGO_SETTINGS_MODULE = "web_project.settings.dev"
$env:ENABLE_CAMERA_WEBSOCKET = "1"
$env:CELERY_TASK_ALWAYS_EAGER = "1"
$env:DETECTION_AUTO_DISPATCH = "1"
$env:YOLO_AUTOINSTALL = "false"
cd web_project
..\.venv\Scripts\python.exe -m uvicorn web_project.asgi:application --host 127.0.0.1 --port 8001
```

桌面 Web：

```powershell
cd sign
corepack pnpm run dev
```

手机 H5：

```powershell
cd sign-app
corepack pnpm run dev:h5
```

## 六、测试与验收

后端：

```powershell
cd web_project
..\.venv\Scripts\python.exe -m pytest -q
```

桌面 Web：

```powershell
cd sign
corepack pnpm run lint
corepack pnpm run test:unit
corepack pnpm run build
```

手机端：

```powershell
cd sign-app
corepack pnpm run test:unit
corepack pnpm run build:h5
corepack pnpm run build:mp-weixin
```

## 七、常见问题

### 提示端口被占用

本地默认占用 8001、8080、5173。先运行 `stop-windows.cmd`。如果仍冲突，执行：

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8001,8080,5173 |
  Select-Object LocalPort, OwningProcess
```

确认占用程序后自行关闭。脚本不会自动结束未知进程。

### `setup-windows.cmd` 下载失败

确认网络可以访问 PyPI 与 npm，然后重新运行。pip 和 pnpm 会复用已下载缓存，不需要删除 `.venv` 或 `node_modules`。

### Python 版本错误

模型依赖固定支持 Python 3.11 / 3.12。不要使用 Python 3.13 创建本项目虚拟环境。

### 登录失败或忘记密码

先查看 `web_project\.demo-credentials`。需要重置时，在项目根目录执行：

```powershell
cd web_project
..\.venv\Scripts\python.exe manage.py bootstrap_demo `
  --username signflow_admin `
  --password "请替换为至少12位且包含字母数字的强密码"
```

### 模型列表为空

确认以下文件存在：

```text
web_project\model\ASl-v8.pt
web_project\model\csl.pt
```

然后执行：

```powershell
cd web_project
..\.venv\Scripts\python.exe manage.py bootstrap_demo
..\.venv\Scripts\python.exe manage.py sync_model_cards
```

### 识别没有标签

这通常不是服务故障，而是输入动作不属于所选模型的有限类别。确认：

- CSL 素材选择 `SignFlow CSL 37`；
- ASL 素材选择 `SignFlow Base`；
- 手部清晰、光线稳定、主体尺寸足够；
- 置信度阈值没有设置过高。

模型类别、数据集、Precision、Recall、mAP50、延迟、测试硬件和能力边界见 `docs/model-evaluation/2026-07-30-model-evaluation.md`。

## 八、生产部署说明

本地一键脚本用于开发和演示，不等同于公网生产配置。公网部署应使用根目录的 Docker Compose：MySQL、Redis、Celery、MinIO、Django ASGI、Nginx 和独立前端构建。

部署前必须：

1. 复制 `.env.example` 为 `.env`；
2. 替换所有 `CHANGE_ME`；
3. 使用真实 HTTPS 域名；
4. 设置高强度 `DJANGO_SECRET_KEY`、数据库、Redis 和 MinIO 密码；
5. 完整执行 `docs/release-checklist.md`。

不要把 `.env`、`.demo-credentials`、SQLite 数据库、用户上传文件或运行日志发给队友之外的人员。

## 九、交付包内容与边界

包含：

- `sign`：桌面 Vue 3 + Vite 前端；
- `sign-app`：uni-app 手机 H5 / 微信小程序；
- `web_project`：Django / DRF / Channels / Celery 后端；
- `web_project/model`：运行所需本地模型权重；
- `deploy` 与 Docker 文件：生产部署配置；
- `docs` 精选文档、模型评测和图文技术报告；
- `scripts/team` 与根目录 CMD：安装、启动、停止、健康检查、重新打包脚本；
- `PACKAGE-SHA256SUMS.txt`：包内每个文件的 SHA-256 清单。

为保证 ZIP 小于 200 MB 且不泄露本机数据，未包含：

- `.git` 历史、IDE 配置；
- `.venv`、`node_modules`、构建缓存；
- 训练代码副本、数据集、训练输出和历史模型仓库；
- 用户上传媒体、数据库、日志和录屏帧；
- 本机 `.env`、管理员密码和第三方密钥；
- 历史备份和旧交付 ZIP。

因此，队友收到的是可复现运行的源码交付包，而不是包含你本机状态的镜像。首次安装会在队友电脑上独立生成依赖、数据库和随机管理员密码。

