# SignFlow AI

面向手语沟通场景的多模态识别与结果管理平台。项目把图片、视频和实时摄像头统一到同一个工作台中，提供可追踪的任务状态、结果详情、数据洞察、模型目录与管理员控制台。

当前版本定位为可部署的产品验证版本：只运行已有模型做推理，不包含模型训练，也不会把用户上传内容默认加入训练集。

## 产品能力

- 商业化公开首页、登录注册、响应式应用壳和移动端抽屉导航。
- Vue 3 + uni-app 手机端，可构建为 H5 和微信小程序，并复用同一套真实识别 API。
- 无需登录的产品导览页，内置 3 组原创 AI 生成样例，并明确标注“演示数据”。
- 图片、视频与实时摄像头统一识别工作台。
- 异步检测任务状态机：排队、处理、完成、失败、取消与重试。
- 结果中心、结果详情、标签时间轴、参数追溯与结果导出。
- 真实任务数据驱动的总览、7 日趋势和数据洞察；无数据时显示空状态。
- 模型目录与模型版本展示。
- 用户、角色和系统依赖状态管理员控制台。
- JWT 鉴权、HttpOnly 刷新 Cookie、owner 数据隔离、上传校验和结构化日志。
- Django Channels 实时识别通道、一次性票据及帧率/消息/会话限制。
- MySQL、Redis、Celery、MinIO/S3、Nginx 与 Docker Compose 部署方案。

## 技术架构

```text
Browser
  ├─ Vue 3 + Vite + Element Plus + ECharts
  ├─ REST /api/v1
  └─ WebSocket /ws/camera
               │
             Nginx
               │
      Django REST + Channels
        ├─ MySQL
        ├─ Redis / Celery
        ├─ MinIO / S3
        └─ Ultralytics YOLO inference
```

前端使用 Vue Router、Axios、Vitest 与 Playwright；后端使用 Django 4.2、Django REST Framework、SimpleJWT、Channels、Celery、Ultralytics、OpenCV 与 pytest。

## 当前可展示入口

本地服务启动后：

- 产品首页：`http://127.0.0.1:8080/`
- 产品导览：`http://127.0.0.1:8080/product-tour`
- 登录：`http://127.0.0.1:8080/auth/login`
- 产品总览：`http://127.0.0.1:8080/app/overview`
- 管理后台：`http://127.0.0.1:8080/admin/users`
- 后端存活检查：`http://127.0.0.1:8001/health/live`
- 后端就绪检查：`http://127.0.0.1:8001/health/ready`
- 手机 H5：`http://127.0.0.1:5173`

## 快速运行

把项目交给另一台 Windows 电脑运行时，优先阅读
[队友交付包运行说明](TEAM-QUICKSTART.md)，然后依次双击 `setup-windows.cmd` 和
`start-windows.cmd`。脚本会创建独立环境、初始化随机管理员，并同时登记 CSL / ASL
两套本地模型；整个流程只执行推理，不执行训练。

### 1. 前端与产品导览

```powershell
cd sign
pnpm install
pnpm dev
```

打开 `http://127.0.0.1:8080/product-tour`。产品导览在后端暂时不可用时仍能走通完整样例流程，但会一直保留“演示数据”标识。

### 2. 本地完整推理

```powershell
cd web_project
python -m pip install -r requirements/dev.txt -r requirements/prod.txt
python manage.py migrate

$env:ENABLE_CAMERA_WEBSOCKET = "1"
$env:CELERY_TASK_ALWAYS_EAGER = "1"
$env:DETECTION_AUTO_DISPATCH = "1"
uvicorn web_project.asgi:application --host 127.0.0.1 --port 8001
```

`CELERY_TASK_ALWAYS_EAGER=1` 只适合本地调试环境，它让任务在当前进程中执行，省去单独启动 Redis 与 Worker。正式部署应移除该变量并使用 Celery Worker。

模型权重放在 `web_project/model/`。模型表中的 `file_path` 只能保存权重文件名，不应保存任意绝对路径。

### 3. 创建本地管理员

```powershell
cd web_project
python manage.py bootstrap_demo
```

命令会创建或更新 `signflow_admin`、超级管理员角色和本地模型记录，并把随机密码写入被 Git 忽略的 `web_project/.demo-credentials`。不要把这个文件提交、截图或投屏。

### 4. 手机 H5 与微信小程序

```powershell
cd sign-app
pnpm install
pnpm dev:h5
pnpm build:mp-weixin
```

H5 默认运行在 `http://127.0.0.1:5173`。微信小程序构建结果位于
`sign-app/dist/build/mp-weixin`，可直接导入微信开发者工具。局域网真机调试和正式发布要求见
[手机端与微信小程序使用手册](docs/mobile-mini-program.md)。

## 生产部署

复制环境变量模板并替换所有 `CHANGE_ME`：

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

生产环境必须使用真实 HTTPS 域名、强随机 `DJANGO_SECRET_KEY`、独立数据库密码和私有对象存储凭据。容器编排包含 MySQL、Redis、MinIO、Django ASGI、CPU/GPU Worker、前端构建与 Nginx。

详细部署、健康检查、备份和回滚流程见 [运行与发布手册](docs/runbook.md)。

## 质量验证

前端：

```powershell
cd sign
pnpm run lint
pnpm run test:unit
pnpm run build
pnpm run test:e2e
```

后端：

```powershell
cd web_project
ruff format --check api detections health inference storage web_project tests
ruff check api detections health inference storage web_project tests
pytest -q
python manage.py check --deploy --settings=web_project.settings.prod
```

GitHub Actions 会执行上述检查，并在前后端通过后构建两个 Docker 镜像。

## 项目结构

```text
sign-yolo/
├─ sign/                       Vue 3 前端
├─ sign-app/                   Vue 3 + uni-app 手机 H5 / 微信小程序
├─ web_project/
│  ├─ api/                    v1 产品与管理员 API
│  ├─ detections/             检测任务、事件与清理命令
│  ├─ inference/              模型缓存与推理服务
│  ├─ storage/                本地及 S3 对象存储抽象
│  ├─ health/                 live / ready 健康检查
│  └─ web_project/            Django 配置、ASGI 与 Celery
├─ deploy/nginx.conf
├─ docker-compose.yml
├─ Dockerfile.frontend
├─ Dockerfile.backend
└─ docs/
   ├─ model-evaluation/
   ├─ release-checklist.md
   ├─ runbook.md
   └─ design/commercial-redesign/
```

## 产品与交付资料

- [发布验收清单](docs/release-checklist.md)
- [商业化设计系统](docs/design/commercial-redesign/design-system.md)
- [手机端与微信小程序使用手册](docs/mobile-mini-program.md)
- [真实模型评测报告](docs/model-evaluation/2026-07-30-model-evaluation.md)

## 安全说明

- 登录密码使用 Django 密码哈希；旧 MD5 账号只在成功登录时自动升级。
- Web 端 access token 只保存在浏览器内存，刷新令牌通过 HttpOnly Cookie 管理；小程序端
  access token 只保存在运行内存，refresh token 保存在客户端并仅用于换取新令牌。
- 检测结果、详情、取消、重试和保存操作均按 owner 隔离。
- 上传会校验扩展名、MIME、文件签名、大小和对象 key。
- 日志不得记录密码、令牌、Cookie、原始图片或第三方密钥。
- `.env`、本地管理员凭据、数据库、日志、媒体和模型权重不得提交到公开仓库。

发布到公共环境前，请完整执行 [发布验收清单](docs/release-checklist.md)，并轮换任何曾经出现在 Git 历史中的第三方密钥。
