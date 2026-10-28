# SignFlow AI 运行与发布手册

## 1. 系统边界

SignFlow AI 的生产部署由以下服务组成：

- Nginx：同源入口、静态资源、API 与 WebSocket 分流。
- Vue 3 前端：公开产品页、只读产品导览、登录后的产品工作区。
- Django ASGI：认证、任务、结果、模型目录、数据洞察和摄像头票据。
- Celery Worker：图片与视频异步推理。Django 请求进程不直接加载模型。
- Redis：任务队列、Channels 与一次性摄像头票据共享缓存。
- MySQL：账号、权限、模型元数据、识别任务和审计事件。
- MinIO/S3：用户上传的原始媒体。数据库仅保存对象 key。

本项目的运行流程只做推理，不包含模型训练，也不会把用户上传默认加入训练集。

## 2. 本地产品验证（无需模型训练）

前端内置三种经过标注的官方演示入口，后端离线时仍能展示完整产品闭环。

```powershell
cd sign
pnpm install
pnpm dev
```

打开 `http://127.0.0.1:8080/product-tour`。正式验收前仍应启动后端并检查 `/health/ready`，避免把样例导览状态误认为真实服务在线。

本地后端：

```powershell
cd web_project
python -m pip install -r requirements/dev.txt -r requirements/prod.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

真实图片/视频任务还需要 Redis 和 Celery Worker：

```powershell
celery -A web_project worker --loglevel=INFO --queues=detections --concurrency=1
```

模型权重放在 `MODEL_STORAGE_ROOT`，模型表中的 `file_path` 只写文件名，不能写任意绝对路径。

## 3. 容器化部署

1. 复制 `.env.example` 为 `.env`。
2. 替换所有 `CHANGE_ME`，并将域名、CORS、CSRF 配置为实际 HTTPS 地址。
3. 将已授权的推理权重放到 `web_project/model/`。不要把权重提交到 Git。
4. 启动并观察健康状态：

```bash
docker compose up --build -d
docker compose ps
curl -fsS http://127.0.0.1:8080/health/live
curl -fsS http://127.0.0.1:8080/health/ready
```

CPU Worker 默认启用。GPU 推理节点可额外运行：

```bash
docker compose --profile gpu up -d worker-gpu
```

GPU 主机必须预先安装 NVIDIA Container Toolkit，并确认容器内 PyTorch 能识别 CUDA；否则保持 CPU Worker。

## 4. 健康检查

- `/health/live`：只说明 ASGI 进程可响应，不代表依赖可用。
- `/health/ready`：检查数据库、Redis、对象存储和模型权重目录；任一失败返回 HTTP 503。

总览页只有在 readiness 为 `ready` 时才显示“全部服务在线”。接口失败时显示降级状态，不伪造在线状态。

## 5. 日志与排障

应用日志为单行 JSON，至少包含：

`timestamp`、`level`、`requestId`、`route`、`status`、`durationMs`、`userId`。

日志不得记录密码、JWT、刷新 Cookie、原始图像、完整对象存储路径或第三方密钥。

常用命令：

```bash
docker compose logs -f nginx web worker
docker compose exec web python manage.py check
docker compose exec web python manage.py showmigrations
docker compose exec worker celery -A web_project inspect ping
```

故障定位顺序：

1. 先看 `/health/ready` 的失败组件。
2. 用响应头 `X-Request-ID` 对齐 Nginx 与 Django 日志。
3. 任务失败时查看 `DetectionJob.error_code` 和任务事件，不向界面返回 Python 堆栈。
4. 摄像头 4401 表示票据或登录失效，4429 表示用户并发会话已达上限。

## 6. 数据保护

- 刷新令牌只放入 `HttpOnly + Secure + SameSite=Strict` Cookie。
- access token 只保存在浏览器内存，不写 localStorage。
- 上传先校验大小、MIME 和文件签名，然后写入用户隔离的随机对象 key。
- 生产媒体桶保持私有；不要由 Nginx 暴露整个媒体目录。
- 默认保留期由 `DETECTION_RETENTION_DAYS` 控制。
- 清理命令默认只预览，明确加 `--apply` 才执行：

```bash
python manage.py purge_expired_detections
python manage.py purge_expired_detections --apply --limit 500
```

## 7. 备份、恢复与回滚

发布前至少备份：

- MySQL 逻辑备份；
- MinIO/S3 桶版本或快照；
- `.env` 的安全托管副本；
- 当前镜像 tag/digest；
- 模型权重与模型元数据版本。

恢复顺序：数据库 → 对象存储 → 模型权重 → Web/Worker → Nginx。恢复后先跑 readiness，再使用官方样例和一个真实小图片任务验证。

回滚时切回上一组前后端镜像，数据库迁移只使用向后兼容迁移。不要用 `git reset --hard` 或直接删除生产卷。

## 8. 发布前最低检查

```bash
cd sign
pnpm run lint
pnpm run test:unit
pnpm run build
pnpm run test:e2e

cd ../web_project
ruff format --check api detections health inference storage web_project tests
ruff check api detections health inference storage web_project tests
pytest -q
python manage.py check --deploy --settings=web_project.settings.prod
```

最后按 `docs/release-checklist.md` 在桌面和移动视口完成浏览器验收。
