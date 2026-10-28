# GitHub 项目备份说明

本仓库保存 SignFlow AI 当前工作目录的独立快照，包含 Web、手机端、后端、运行脚本、部署文件、模型权重、项目文档和最终演示视频。

## 运行

Windows 用户先阅读 [TEAM-QUICKSTART.md](TEAM-QUICKSTART.md)，然后使用 `setup-windows.cmd` 安装依赖并初始化，再使用 `start-windows.cmd` 启动。识别运行所需的 CSL 和 ASL 权重保存在 `web_project/model/`，不需要重新训练模型。

## 备份范围

- 包含当前工作目录中的项目源代码和模型文件；这是一个独立的 Git 快照，不包含原 Gitee 仓库的历史提交。
- 排除了原始训练数据集、训练运行目录、大型旧压缩包和历史备份；这些资料仍保留在原电脑上，未上传到本仓库。
- 排除了本机 `.env`、管理员密码文件、数据库、用户上传媒体、日志、依赖目录和缓存。重新部署时请从 `.env.example` 配置自己的环境参数。
- 演示视频位于 `docs/demo-video/SignFlow-AI-competition-FINAL-news-anchor-no-subtitles.mp4`。

请维持私有仓库，确认模型权重和展示素材的使用权限后再对外分享。
