# SignFlow AI 商业化与比赛展示版实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不重新训练模型的前提下，把现有 Sign YOLO 项目升级为可参加比赛演示、可小规模商业试点、具有统一高级视觉和可信产品叙事的手语识别平台。

**Architecture:** 保留 Vue 3 + Element Plus、Django + MySQL + Channels、Ultralytics YOLO 的核心技术栈；前端引入统一设计令牌、应用壳层和统一识别工作台，后端拆分认证、业务 API、异步推理任务和模型服务。比赛版与商业版共享同一套代码，通过访客演示、权限和部署配置区分。

**Tech Stack:** Vue 3、Element Plus、Vue Router、Vite、Vitest、Playwright、Django 4.2、Django REST Framework、SimpleJWT、Channels、Celery、Redis、MySQL、Ultralytics YOLO、MinIO/S3、Docker、Nginx、GitHub Actions。

## Global Constraints

- 不运行训练脚本，不改动现有 `.pt` / `.onnx` 权重内容。
- 第一阶段保留现有 Vue 3、Element Plus、Django、MySQL 和 YOLO，禁止为了“现代化”重写全部业务。
- 比赛演示必须支持 90 秒内完成“选择样例 → 识别 → 翻译/结果 → 导出”的闭环。
- 所有公开指标必须来自真实接口或明确标注为“演示数据”；准确率必须附模型版本、数据集、样本量和统计日期。
- 桌面端验收视口为 1440×900、1280×720；移动端验收视口为 390×844；不得出现横向滚动或内容裁切。
- 可访问性目标为 WCAG 2.2 AA：正文文字对比度至少 4.5:1，键盘焦点清晰，交互目标最小 24×24 CSS px，关键按钮建议 44px 高。
- 生产环境禁止 `DEBUG=True`、通配 `ALLOWED_HOSTS`、通配 CORS、硬编码密钥、明文数据库口令、MD5 密码和 URL 查询参数传递密码。
- 所有上传文件必须限制扩展名、MIME、大小和存储路径；用户不能通过文件名控制服务器路径。
- 每项任务都要包含自动化测试、视觉验证或接口验收，完成后形成独立可审查提交。

---

## 1. 当前审计结论

### 1.1 已捕获界面

- 桌面登录：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/03-login-desktop-viewport.jpg`
- 桌面注册：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/04-register-desktop.jpg`
- 移动登录：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/05-login-mobile.jpg`
- 公开展示页：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/06-public-home-desktop.jpg`
- 管理员首页：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/08-admin-dashboard-viewport.jpg`
- 用户管理：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/09-admin-users.jpg`
- 图片识别工作台：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/10-image-workbench.jpg`
- 模型管理：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/13-model-management.jpg`
- 2D/3D 数据页：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/14-2d-data.jpg`、`15-3d-data.jpg`
- 角色管理运行时错误：`C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/17-role-runtime-error.jpg`
- 登录后移动端：首页 `C:/Users/11430/.codex/visualizations/2026/07/28/019fa944-e453-7713-8821-a9c8e18b356e/sign-yolo-product-audit/18-admin-dashboard-mobile.jpg`

### 1.2 结构问题

1. 认证页、公开展示页、后台管理页分别使用“太空蓝渐变”“深色绿黑”“Element Plus 默认蓝 + 黄色侧栏高亮”，没有统一品牌语言。
2. 390px 移动端登录页出现输入框和注册链接横向裁切；`reset.css` 使用 `overflow-x: hidden` 掩盖了真实溢出。
3. 公开展示页三块可视化区域为空，浏览器报错 `xAxis3D "0" not found`；页面仍展示硬编码业务数字，比赛答辩时可信度不足。
4. 首页、识别页、历史页和系统管理页信息层级一致，核心用户任务与管理员功能混在同一导航中。
5. 图片、视频、摄像头三个识别页大量复制“模型选择、阈值、预览、结果、导出”结构，视觉和交互难以统一维护。
6. 普通识别流程直接暴露模型上传、IoU 和置信度微调；对普通用户过于技术化，对专业用户又缺少版本、性能、部署状态等完整信息。
7. 登录输入仅用 placeholder，没有稳定可见标签；当前颜色、焦点、键盘顺序、错误提示关联和响应式回流尚未达到可上线标准。
8. 登录后的 390×844 页面仍固定显示约 200px 侧栏，主内容只剩狭窄区域，标题逐字换行并出现横向滚动，无法作为移动端产品使用。
9. 顶部每访问一个页面就持续新增可关闭标签；在审计过程中已累积十余个标签，移动端和窄屏下导航状态不可控。
10. 管理员首页的 `95%`、`200+`、`1000+` 与公开页指标一样没有数据来源、统计周期或模型版本说明。
11. 用户管理和模型管理表格在 1440px 下仍出现用户名、时间戳和备注的强制换行，操作按钮颜色过多，扫描效率低。
12. 2D/3D 页面使用旧模板路由名，面包屑仍显示“部门管理”“岗位管理”；图表数据缺少来源、筛选条件和更新时间语义。
13. “超级管理员”角色仅分配 15/17 个菜单，未包含“智能/智能手语问答”，角色名称与实际授权范围不一致。

### 1.3 上线阻断项

1. `web_project/settings.py` 硬编码 `SECRET_KEY`、数据库口令，且启用 `DEBUG=True`、`ALLOWED_HOSTS=['*']`、`CORS_ALLOW_ALL_ORIGINS=True`。
2. 登录密码通过 `request.GET` 传输并被 `print(username, password)` 输出到日志。
3. 用户密码使用 MD5；JWT 使用已老化的 `rest_framework_jwt`；中间件和检测代码会打印 token。
4. 后端没有可复现的 `requirements.txt`，前后端没有 Docker、CI、健康检查、结构化日志和生产部署配置。
5. 视频和实时帧处理在 Web/Django 进程中承担大量同步工作，缺少任务队列、取消、重试、超时和资源配额。
6. 媒体、模型和推理结果依赖本机目录，无法支持多实例部署、备份和权限隔离。
7. 当前 JWT 默认仅 5 分钟有效且 `JWT_ALLOW_REFRESH=False`；过期后中间件返回 HTTP 200 的纯文本，而非标准 401 JSON，前端不会退出或刷新会话，随后图片、视频、摄像头历史页只显示“获取数据失败/获取会话列表失败”。
8. 会话过期后继续进入角色管理会进一步触发 `Cannot read properties of null (reading 'getBoundingClientRect')`，开发环境错误遮罩覆盖整个应用；重新登录后历史接口和角色列表均恢复，说明这是认证失效与页面容错共同导致的级联故障。
9. 首页菜单点击后内容已切换，但标签选中状态仍停留在上一个页面，路由、标签和内容状态可能失去同步。
10. 开发服务器会把运行时错误直接暴露给用户；比赛版必须使用生产构建并配置统一错误边界、降级页和可追踪错误编号。

---

## 2. 目标产品方案

### 2.1 产品定位

工作品牌使用 **SignFlow AI / 手语智译平台**。产品不再表现为“YOLO 管理后台”，而是一个面向真实沟通场景的无障碍 AI 工作台：

- 访客：无需注册即可用官方样例体验识别闭环。
- 普通用户：上传图片/视频或打开摄像头，获得手语标签、句子、置信度和可导出结果。
- 专业用户：可查看模型版本、阈值、耗时、检测轨迹和批量任务。
- 管理员：独立管理用户、权限、模型、配额、审计日志和系统健康。

### 2.2 信息架构

| 一级区域 | 页面 | 核心目标 |
|---|---|---|
| 公开体验 | 产品首页、样例演示、技术与隐私说明 | 让评委和潜在客户 30 秒理解价值 |
| 工作台 | 实时、图片、视频三种模式 | 完成一次识别任务 |
| 结果中心 | 全部任务、结果详情、导出 | 复查、分享和追溯 |
| 数据洞察 | 使用趋势、类别分布、延迟、成功率 | 证明产品稳定性和业务价值 |
| 模型中心 | 版本、指标、状态、部署、回滚 | 专业模型治理 |
| 团队与设置 | 成员、角色、配额、通知、隐私 | 商业账户管理 |
| 管理后台 | 用户、权限、菜单、系统日志 | 仅管理员可见 |

目标路由：

```text
/
/demo
/auth/login
/auth/register
/app/overview
/app/workbench?mode=live|image|video
/app/results
/app/results/:id
/app/analytics
/app/models
/app/team
/app/settings
/admin/users
/admin/roles
/admin/system
```

旧路由保留 301/客户端重定向，避免已有链接失效。

### 2.3 核心工作台

统一为一个三栏工作台：

```text
左侧：输入来源与模型预设
中间：原始画面 / 识别画面 / 空状态 / 进度
右侧：实时标签、生成句子、置信度、耗时
底部：时间轴、导出、保存到结果中心
```

- 顶部使用 `实时摄像头 / 图片 / 视频` 模式切换。
- 默认只显示“标准 / 高精度 / 低延迟”三个预设。
- IoU、置信度、设备和模型版本放入“高级设置”抽屉。
- 模型上传从识别页移到模型中心。
- 长任务显示排队、处理中、可取消、失败原因和重试。
- 相机权限被拒绝时给出明确恢复步骤，不显示空白黑框。

### 2.4 视觉方向

方向名称：**Accessible AI Studio**。

- 气质：可信、清晰、安静、专业；避免常见“赛博大屏”和全屏霓虹。
- 主色：靛蓝 `#5B5BD6`，用于主按钮、选中状态和焦点。
- 辅色：青绿 `#0E9384`，用于识别成功、实时状态和数据强调。
- 深色：`#0B1220`，仅用于公开页 Hero、视频画布和深色模式。
- 页面底色：`#F7F9FC`；卡片：`#FFFFFF`；边框：`#E6EAF2`。
- 正文：`#182230`；次级文字：`#667085`；错误：`#D92D20`。
- 字体：`Inter, "PingFang SC", "Microsoft YaHei", sans-serif`。
- 间距：8px 基准网格；页面 24/32px，卡片 20/24px，控件间距 12/16px。
- 圆角：按钮/输入 10px，卡片 16px；避免每个容器都加阴影。
- 动效：150–240ms，仅用于状态切换、抽屉、结果出现和进度反馈。
- 图标：统一 Element Plus Icons；不得使用 emoji 或文本符号代替图标。

设计令牌初稿：

```css
:root {
  --sf-color-primary: #5b5bd6;
  --sf-color-primary-hover: #4747c6;
  --sf-color-accent: #0e9384;
  --sf-color-bg: #f7f9fc;
  --sf-color-surface: #ffffff;
  --sf-color-canvas: #0b1220;
  --sf-color-text: #182230;
  --sf-color-text-muted: #667085;
  --sf-color-border: #e6eaf2;
  --sf-color-danger: #d92d20;
  --sf-radius-control: 10px;
  --sf-radius-card: 16px;
  --sf-shadow-card: 0 8px 32px rgb(15 23 42 / 8%);
  --sf-space-1: 4px;
  --sf-space-2: 8px;
  --sf-space-3: 12px;
  --sf-space-4: 16px;
  --sf-space-6: 24px;
  --sf-space-8: 32px;
}
```

---

## 3. 分期与优先级

| 阶段 | 目标 | 建议工期 | 上线门槛 |
|---|---|---:|---|
| P0 | 安全、依赖和可运行基线 | 3–5 天 | 不再泄露密码/token/密钥 |
| P1 | 设计系统、应用壳、认证与公开页 | 5–7 天 | 桌面/移动无裁切，无控制台错误 |
| P2 | 统一识别工作台 | 6–9 天 | 三种输入完成同一识别闭环 |
| P3 | 结果、模型、数据洞察 | 5–7 天 | 数据真实可追溯 |
| P4 | 异步推理、存储、部署与监控 | 7–12 天 | 可在测试环境连续运行 |
| P5 | 比赛演示与发布验收 | 3–5 天 | 90 秒演示稳定通过 |

一个全栈开发者建议 5–7 周；两名开发者并行建议 3–4 周。不得通过跳过 P0 换取界面进度。

---

## 4. 实施任务

### Task 1: 建立前端构建、测试和视觉基线

**Files:**
- Create: `sign/vite.config.js`
- Create: `sign/index.html`
- Create: `sign/tests/setup.js`
- Create: `sign/tests/e2e/smoke.spec.js`
- Modify: `sign/package.json`
- Modify: `sign/src/main.js`

**Interfaces:**
- Consumes: 现有 `src/main.js`、Vue Router、Vuex 和 Element Plus。
- Produces: `npm run dev`、`npm run build`、`npm run test:unit`、`npm run test:e2e` 四个稳定命令。

- [ ] **Step 1: 先写浏览器烟雾测试**

```js
import { test, expect } from '@playwright/test'

test('public and auth routes render without console errors', async ({ page }) => {
  const errors = []
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text())
  })
  await page.goto('/home')
  await expect(page.getByRole('heading', { name: '手语识别智能分析平台' })).toBeVisible()
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: '手语识别系统' })).toBeVisible()
  expect(errors).toEqual([])
})
```

- [ ] **Step 2: 运行测试并确认当前展示页失败**

Run: `cd sign && npx playwright test tests/e2e/smoke.spec.js`

Expected: FAIL，错误中包含 `xAxis3D "0" not found`。

- [ ] **Step 3: 增加 Vite 配置并保持别名兼容**

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 8080,
  },
})
```

- [ ] **Step 4: 更新脚本并锁定运行版本**

```json
{
  "scripts": {
    "dev": "vite --host 127.0.0.1 --port 8080",
    "build": "vite build",
    "preview": "vite preview --host 127.0.0.1 --port 8080",
    "test:unit": "vitest run",
    "test:e2e": "playwright test"
  }
}
```

- [ ] **Step 5: 验证构建**

Run: `npm run build`

Expected: PASS，无错误，产物位于 `sign/dist/`。

- [ ] **Step 6: Commit**

```bash
git add sign/package.json sign/vite.config.js sign/index.html sign/tests sign/src/main.js
git commit -m "build: establish frontend test and vite baseline"
```

### Task 2: 建立统一设计令牌与基础组件

**Files:**
- Create: `sign/src/styles/tokens.css`
- Create: `sign/src/styles/element-theme.scss`
- Create: `sign/src/styles/base.css`
- Create: `sign/src/components/ui/PageHeader.vue`
- Create: `sign/src/components/ui/MetricCard.vue`
- Create: `sign/src/components/ui/StatusBadge.vue`
- Create: `sign/src/components/ui/EmptyState.vue`
- Create: `sign/tests/unit/design-system.spec.js`
- Modify: `sign/src/main.js`
- Remove after migration: `sign/src/assets/styles/reset.css`

**Interfaces:**
- Consumes: Element Plus CSS variables。
- Produces: `PageHeader`, `MetricCard`, `StatusBadge`, `EmptyState` 和 `--sf-*` 全局令牌。

- [ ] **Step 1: 写令牌测试**

```js
import { describe, expect, it } from 'vitest'
import tokens from '@/styles/tokens.css?raw'

describe('design tokens', () => {
  it('defines the required commercial theme tokens', () => {
    expect(tokens).toContain('--sf-color-primary: #5b5bd6')
    expect(tokens).toContain('--sf-radius-card: 16px')
    expect(tokens).toContain('--sf-color-text: #182230')
  })
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `npm run test:unit -- design-system.spec.js`

Expected: FAIL，`tokens.css` 不存在。

- [ ] **Step 3: 创建令牌并映射 Element Plus**

```css
:root {
  --el-color-primary: var(--sf-color-primary);
  --el-color-success: var(--sf-color-accent);
  --el-border-radius-base: var(--sf-radius-control);
  --el-bg-color-page: var(--sf-color-bg);
  --el-text-color-primary: var(--sf-color-text);
  --el-text-color-regular: var(--sf-color-text-muted);
  --el-border-color: var(--sf-color-border);
}
```

- [ ] **Step 4: 重置全局样式**

`base.css` 必须使用 `box-sizing: border-box`、正常字号和 `min-width: 0`，不得使用 `overflow-x: hidden` 掩盖布局问题。

- [ ] **Step 5: 为四个基础组件补充快照与键盘测试**

Run: `npm run test:unit`

Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add sign/src/styles sign/src/components/ui sign/tests/unit sign/src/main.js
git commit -m "feat: add accessible commercial design system"
```

### Task 3: 重建应用壳层和导航

**Files:**
- Create: `sign/src/layout/app/AppShell.vue`
- Create: `sign/src/layout/app/AppSidebar.vue`
- Create: `sign/src/layout/app/AppTopbar.vue`
- Create: `sign/src/layout/app/MobileNavDrawer.vue`
- Create: `sign/src/router/routes.js`
- Create: `sign/src/router/guards.js`
- Create: `sign/tests/unit/app-shell.spec.js`
- Modify: `sign/src/router/index.js`
- Modify: `sign/src/layout/index.vue`
- Modify: `sign/src/layout/menu/index.vue`
- Modify: `sign/src/layout/header/index.vue`
- Remove: `sign/src/layout/tabs/index.vue`

**Interfaces:**
- Consumes: 用户角色、菜单权限和 Vue Router。
- Produces: `AppShell` 插槽、折叠侧栏、移动抽屉、面包屑和角色隔离导航。

- [ ] **Step 1: 写路由与角色测试**

```js
it('hides admin navigation for a normal user', async () => {
  const wrapper = mount(AppSidebar, {
    props: { role: 'user', collapsed: false },
  })
  expect(wrapper.text()).toContain('识别工作台')
  expect(wrapper.text()).not.toContain('用户管理')
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `npm run test:unit -- app-shell.spec.js`

Expected: FAIL，`AppSidebar` 不存在。

- [ ] **Step 3: 实现浅层导航**

普通用户仅显示：概览、识别工作台、结果中心、数据洞察、模型中心、设置。管理员入口放在底部独立分组。

- [ ] **Step 4: 删除多标签页导航**

用浏览器历史、面包屑和页面标题代替当前可关闭 tab；避免出现“路由名即标签名”和移动端无法操作的问题。

- [ ] **Step 5: 验证 1440、1280、390 三个视口**

Run: `npm run test:e2e -- app-shell`

Expected: 侧栏桌面可折叠、移动端进入抽屉、主内容没有横向滚动。

- [ ] **Step 6: Commit**

```bash
git add sign/src/layout sign/src/router sign/tests/unit/app-shell.spec.js
git commit -m "feat: rebuild product navigation and app shell"
```

### Task 4: 重做公开首页、登录和注册

**Files:**
- Create: `sign/src/components/marketing/DemoPreview.vue`
- Create: `sign/src/components/auth/AuthShell.vue`
- Create: `sign/src/services/auth.js`
- Create: `sign/tests/e2e/auth-flow.spec.js`
- Modify: `sign/src/views/HomeView.vue`
- Modify: `sign/src/views/Login.vue`
- Modify: `sign/src/views/Register.vue`

**Interfaces:**
- Consumes: `auth.login(credentials)`、`auth.register(payload)`。
- Produces: 公开价值页、访客样例入口、响应式认证页和可访问错误状态。

- [ ] **Step 1: 写移动端回流测试**

```js
test('login reflows at 390px without horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/login')
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
  await expect(page.getByLabel('账号')).toBeVisible()
  await expect(page.getByLabel('密码')).toBeVisible()
})
```

- [ ] **Step 2: 运行测试确认当前失败**

Run: `npm run test:e2e -- auth-flow`

Expected: FAIL，移动端存在横向溢出，且输入框缺少稳定 label。

- [ ] **Step 3: 实现公开首页**

公开首页按顺序呈现：

1. 一句话价值主张和“体验样例 / 登录系统”；
2. 真实识别前后对比；
3. 图片、视频、实时三种场景；
4. 有方法说明的模型指标；
5. 隐私、本地推理和数据保留说明；
6. 典型应用场景与团队信息。

移除报错的 ECharts GL 大板块和无来源的硬编码数字。

- [ ] **Step 4: 实现认证体验**

使用可见 label、密码显示切换、Caps Lock 提示、加载状态、服务端错误映射和登录后回跳。注册至少包含密码长度、确认密码和隐私说明。

- [ ] **Step 5: 修复页脚**

更新年份为运行时年份，移除 `python222.com` 外链和个人团队字样，改为品牌、隐私政策、服务状态。

- [ ] **Step 6: 运行桌面和移动视觉测试**

Run: `npm run test:e2e -- auth-flow smoke`

Expected: PASS，无控制台错误，无内容裁切。

- [ ] **Step 7: Commit**

```bash
git add sign/src/views/HomeView.vue sign/src/views/Login.vue sign/src/views/Register.vue sign/src/components/marketing sign/src/components/auth sign/src/services/auth.js sign/tests/e2e
git commit -m "feat: redesign public and authentication experience"
```

### Task 5: 合并图片、视频和摄像头识别为统一工作台

**Files:**
- Create: `sign/src/views/workbench/RecognitionWorkbench.vue`
- Create: `sign/src/components/workbench/ModeSwitcher.vue`
- Create: `sign/src/components/workbench/SourcePanel.vue`
- Create: `sign/src/components/workbench/PreviewStage.vue`
- Create: `sign/src/components/workbench/ResultInspector.vue`
- Create: `sign/src/components/workbench/AdvancedSettingsDrawer.vue`
- Create: `sign/src/composables/useDetectionJob.js`
- Create: `sign/src/composables/useModelCatalog.js`
- Create: `sign/src/services/detections.js`
- Create: `sign/tests/unit/recognition-workbench.spec.js`
- Modify: `sign/src/views/bsns/Image/index.vue`
- Modify: `sign/src/views/bsns/video/index.vue`
- Modify: `sign/src/views/bsns/camera/index.vue`

**Interfaces:**
- Consumes:

```ts
type DetectionMode = 'image' | 'video' | 'live'
type DetectionPreset = 'balanced' | 'quality' | 'speed'
type DetectionStatus = 'idle' | 'uploading' | 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled'
```

- Produces:

```js
useDetectionJob({
  mode,
  source,
  modelId,
  preset,
  advanced: { iou, confidence },
})
```

- [ ] **Step 1: 写模式切换和渐进披露测试**

```js
it('keeps advanced thresholds hidden until requested', () => {
  const wrapper = mount(RecognitionWorkbench, {
    props: { initialMode: 'image' },
  })
  expect(wrapper.get('[data-testid="advanced-settings"]').isVisible()).toBe(false)
  wrapper.get('[data-testid="open-advanced"]').trigger('click')
  expect(wrapper.get('[data-testid="advanced-settings"]').isVisible()).toBe(true)
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `npm run test:unit -- recognition-workbench.spec.js`

Expected: FAIL，统一工作台尚不存在。

- [ ] **Step 3: 提取重复业务逻辑**

`useModelCatalog` 只负责模型列表和预设；`useDetectionJob` 只负责任务状态；页面组件不得直接拼接 API URL。

- [ ] **Step 4: 实现工作台空、加载、成功、失败、取消状态**

每个状态必须有明确标题、说明和唯一主操作。失败状态展示可读原因与重试，不展示原始 Python 异常。

- [ ] **Step 5: 保留旧页面为轻量兼容路由**

旧的 Image/Video/Camera 页面只负责重定向到 `/app/workbench?mode=*`，确认稳定后删除重复实现。

- [ ] **Step 6: 验证三种模式**

Run: `npm run test:unit -- recognition-workbench.spec.js && npm run test:e2e -- workbench`

Expected: 三种模式均可选择官方样例并进入结果状态；移动端切换为纵向布局。

- [ ] **Step 7: Commit**

```bash
git add sign/src/views/workbench sign/src/components/workbench sign/src/composables sign/src/services/detections.js sign/src/views/bsns sign/tests
git commit -m "feat: unify image video and live recognition workbench"
```

### Task 6: 重做概览、结果中心、模型中心和数据洞察

**Files:**
- Create: `sign/src/views/overview/OverviewPage.vue`
- Create: `sign/src/views/results/ResultsPage.vue`
- Create: `sign/src/views/results/ResultDetailPage.vue`
- Create: `sign/src/views/models/ModelCatalogPage.vue`
- Create: `sign/src/views/analytics/AnalyticsPage.vue`
- Create: `sign/src/services/results.js`
- Create: `sign/src/services/models.js`
- Create: `sign/src/services/analytics.js`
- Create: `sign/tests/e2e/results-flow.spec.js`
- Modify: `sign/src/views/index/index.vue`
- Modify: `sign/src/views/bsns/model/index.vue`
- Modify: `sign/src/views/history/*/index.vue`

**Interfaces:**
- Consumes: 标准分页响应 `{ items, page, pageSize, total }`。
- Produces: 统一结果详情、真实指标卡、模型版本和可追溯导出。

- [ ] **Step 1: 写真实数据契约测试**

```js
it('does not render metrics without source metadata', () => {
  const wrapper = mount(MetricCard, {
    props: {
      label: '系统准确率',
      value: '96.8%',
      source: '',
    },
  })
  expect(wrapper.text()).toContain('数据来源未配置')
})
```

- [ ] **Step 2: 概览页只展示可行动信息**

展示“继续最近任务、今日成功率、平均处理时长、待处理任务、最近结果、服务状态”；删除无来源的 `1000+`、`200+`。

- [ ] **Step 3: 合并三套历史记录**

结果中心使用类型筛选代替三个独立页面，详情页展示原始媒体、标注结果、类别、时间轴、模型版本、参数和导出记录。

- [ ] **Step 4: 模型中心增加治理信息**

每个模型展示版本、类别数、文件大小、状态、最近使用、准确率来源和部署位置。上传、启停、回滚属于管理员操作。

- [ ] **Step 5: 修复所有图表**

仅使用 ECharts 2D；图表必须有空状态、加载状态、数据单位、时间范围和数据来源。

- [ ] **Step 6: 运行结果流程测试**

Run: `npm run test:e2e -- results-flow`

Expected: 可以从概览进入结果详情并导出；没有空白图表。

- [ ] **Step 7: Commit**

```bash
git add sign/src/views/overview sign/src/views/results sign/src/views/models sign/src/views/analytics sign/src/services sign/tests/e2e/results-flow.spec.js
git commit -m "feat: build trustworthy results models and analytics experience"
```

### Task 7: 修复认证、安全和 API 基线

**Files:**
- Create: `web_project/requirements/base.txt`
- Create: `web_project/requirements/dev.txt`
- Create: `web_project/requirements/prod.txt`
- Create: `web_project/web_project/settings/base.py`
- Create: `web_project/web_project/settings/dev.py`
- Create: `web_project/web_project/settings/prod.py`
- Create: `web_project/api/response.py`
- Create: `web_project/api/urls.py`
- Create: `web_project/tests/test_auth_api.py`
- Create: `web_project/tests/test_settings.py`
- Modify: `web_project/user/models.py`
- Modify: `web_project/user/views.py`
- Modify: `web_project/user/middleware.py`
- Modify: `web_project/web_project/urls.py`
- Remove after migration: `rest_framework_jwt`

**Interfaces:**
- Consumes: `POST /api/v1/auth/login` JSON `{ username, password }`。
- Produces: access/refresh token、统一错误响应和安全密码存储。

- [ ] **Step 1: 写认证安全测试**

```python
def test_login_accepts_json_and_never_returns_password(api_client, user):
    response = api_client.post(
        "/api/v1/auth/login",
        {"username": user.username, "password": "Correct-Horse-2026"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data["data"]
    assert "refresh" in response.data["data"]
    assert "password" not in response.data["data"]["user"]
```

- [ ] **Step 2: 写生产配置测试**

```python
def test_production_settings_are_closed():
    from web_project.settings import prod

    assert prod.DEBUG is False
    assert "*" not in prod.ALLOWED_HOSTS
    assert prod.CORS_ALLOW_ALL_ORIGINS is False
    assert not prod.SECRET_KEY.startswith("django-insecure")
```

- [ ] **Step 3: 运行测试确认失败**

Run: `pytest web_project/tests/test_auth_api.py web_project/tests/test_settings.py -q`

Expected: FAIL，当前使用 GET 密码、MD5 和开放配置。

- [ ] **Step 4: 迁移到 Django 密码哈希与 SimpleJWT**

使用 `make_password` / `check_password`；登录请求只接收 JSON；日志不得输出用户名+密码、token 或完整上传路径。

- [ ] **Step 5: 拆分配置并使用环境变量**

必须通过环境变量提供 `DJANGO_SECRET_KEY`、`DB_*`、`CORS_ALLOWED_ORIGINS`、`MODEL_STORAGE_ROOT`、`MEDIA_STORAGE_*`。

- [ ] **Step 6: 标准化 API 响应**

```json
{
  "success": true,
  "data": {},
  "error": null,
  "requestId": "01J..."
}
```

- [ ] **Step 7: 添加旧 MD5 密码的登录时升级**

首次验证旧 MD5 成功后立即用 Django 哈希重新保存；迁移窗口结束后删除 MD5 兼容。

- [ ] **Step 8: 运行后端测试**

Run: `pytest -q`

Expected: PASS，日志中不出现密码和 token。

- [ ] **Step 9: Commit**

```bash
git add web_project/requirements web_project/web_project/settings web_project/api web_project/user web_project/tests
git commit -m "security: harden authentication settings and api contracts"
```

### Task 8: 引入异步推理任务、存储和模型服务

**Files:**
- Create: `web_project/detections/models.py`
- Create: `web_project/detections/serializers.py`
- Create: `web_project/detections/views.py`
- Create: `web_project/detections/tasks.py`
- Create: `web_project/inference/service.py`
- Create: `web_project/storage/backends.py`
- Create: `web_project/tests/test_detection_jobs.py`
- Modify: `web_project/ImageModel/views.py`
- Modify: `web_project/videoModel/views.py`
- Modify: `web_project/CameraModel/consumers.py`

**Interfaces:**
- Consumes:

```json
POST /api/v1/detections
{
  "mode": "image",
  "assetId": "asset_123",
  "modelId": 41,
  "preset": "balanced",
  "advanced": null
}
```

- Produces:

```json
{
  "id": "det_123",
  "status": "queued",
  "progress": 0,
  "result": null,
  "error": null
}
```

- [ ] **Step 1: 写状态机测试**

```python
def test_detection_job_state_machine(detection_job):
    detection_job.mark_running()
    assert detection_job.status == "running"
    detection_job.mark_succeeded({"detections": []})
    assert detection_job.status == "succeeded"
    assert detection_job.progress == 100
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest web_project/tests/test_detection_jobs.py -q`

Expected: FAIL，`DetectionJob` 不存在。

- [ ] **Step 3: 创建任务模型和 Celery 执行器**

任务必须支持排队、进度、取消、重试、超时、失败原因、用户归属、模型版本和参数快照。

- [ ] **Step 4: 把 YOLO 加载封装到模型服务**

`inference/service.py` 对外只暴露：

```python
class InferenceService:
    def predict_image(self, model_id: int, image_path: str, *, iou: float, conf: float) -> dict: ...
    def predict_video(self, model_id: int, video_path: str, *, iou: float, conf: float) -> dict: ...
```

服务进程缓存模型，Django 请求不得重复加载权重。

- [ ] **Step 5: 引入对象存储适配层**

开发环境使用本地文件；测试/生产使用 MinIO 或 S3。业务代码只保存对象 key，不拼接本机绝对路径。

- [ ] **Step 6: 保留实时 Channels 通道**

摄像头帧继续使用 Channels，但增加帧率上限、消息大小、会话超时、断线清理和每用户并发限制。

- [ ] **Step 7: 运行任务测试**

Run: `pytest web_project/tests/test_detection_jobs.py -q`

Expected: PASS，失败任务可重试，取消后不再写入结果。

- [ ] **Step 8: Commit**

```bash
git add web_project/detections web_project/inference web_project/storage web_project/ImageModel web_project/videoModel web_project/CameraModel web_project/tests
git commit -m "feat: add resilient asynchronous inference pipeline"
```

### Task 9: 建立生产部署、监控和数据保护

**Files:**
- Create: `Dockerfile.frontend`
- Create: `Dockerfile.backend`
- Create: `docker-compose.yml`
- Create: `deploy/nginx.conf`
- Create: `deploy/entrypoint.sh`
- Create: `.env.example`
- Create: `.github/workflows/ci.yml`
- Create: `web_project/health/views.py`
- Create: `web_project/web_project/logging.py`
- Create: `docs/runbook.md`

**Interfaces:**
- Consumes: 前端静态产物、ASGI 应用、Celery、Redis、MySQL、对象存储。
- Produces: `/health/live`、`/health/ready`、可复现部署和故障处理手册。

- [ ] **Step 1: 写健康检查**

`/health/live` 仅验证进程；`/health/ready` 验证数据库、Redis、对象存储和模型服务。

- [ ] **Step 2: 创建容器编排**

服务包含 `nginx`、`frontend-build`、`web`、`worker`、`redis`、`mysql`、`minio`。GPU 推理通过独立 profile 启用。

- [ ] **Step 3: 配置 Nginx**

静态文件缓存一年并带 hash；媒体使用鉴权 URL；API 和 WebSocket 分流；上传大小和超时显式配置。

- [ ] **Step 4: 添加结构化日志与 request ID**

日志字段至少包含 `timestamp`、`level`、`requestId`、`route`、`status`、`durationMs`、`userId`；不得包含密码、token、原始图片内容。

- [ ] **Step 5: 添加 CI**

CI 顺序：前端 lint → unit → build → Playwright；后端 format/check → pytest → Django deployment check → Docker build。

- [ ] **Step 6: 验证生产配置**

Run: `python manage.py check --deploy --settings=web_project.settings.prod`

Expected: 无高危警告。

- [ ] **Step 7: 验证容器**

Run: `docker compose up --build`

Expected: 健康检查全部通过，公开页、API、WebSocket 可访问。

- [ ] **Step 8: Commit**

```bash
git add Dockerfile.frontend Dockerfile.backend docker-compose.yml deploy .env.example .github web_project/health web_project/web_project/logging.py docs/runbook.md
git commit -m "ops: add production deployment health checks and ci"
```

### Task 10: 完成比赛演示模式与发布验收

**Files:**
- Create: `sign/src/views/demo/CompetitionDemo.vue`
- Create: `sign/src/demo/sample-manifest.js`
- Create: `sign/tests/e2e/competition-demo.spec.js`
- Create: `web_project/demo/fixtures/demo_results.json`
- Create: `docs/competition-script.md`
- Create: `docs/release-checklist.md`

**Interfaces:**
- Consumes: 三个经过授权的样例媒体和对应固定模型版本。
- Produces: 无登录只读演示、90 秒演示脚本、发布清单。

- [ ] **Step 1: 写 90 秒闭环测试**

```js
test('guest completes the curated demo', async ({ page }) => {
  await page.goto('/demo')
  await page.getByRole('button', { name: '体验图片识别' }).click()
  await page.getByRole('button', { name: '开始识别' }).click()
  await expect(page.getByText('识别完成')).toBeVisible()
  await expect(page.getByRole('button', { name: '查看完整结果' })).toBeVisible()
})
```

- [ ] **Step 2: 准备三个合法样例**

样例覆盖图片、视频、实时录制替代演示；每个样例记录来源、授权、模型版本、预期标签和预期耗时范围。

- [ ] **Step 3: 编写比赛叙事**

演示顺序固定为：痛点 15 秒 → 样例识别 45 秒 → 结果和指标 20 秒 → 隐私与落地 10 秒。

- [ ] **Step 4: 运行发布矩阵**

浏览器：Chrome、Edge；视口：1440×900、1280×720、390×844；网络：正常、慢速、后端不可用；权限：相机允许、拒绝。

- [ ] **Step 5: 验证可访问性**

检查键盘顺序、焦点、标签、错误关联、200% 缩放、对比度、减少动效和屏幕阅读器可读名称。

- [ ] **Step 6: 验证性能和可靠性**

公开页不得加载不必要的 ECharts GL、训练代码或模型权重；图片和视频均展示真实任务进度；连续运行 2 小时无内存持续增长。

- [ ] **Step 7: 运行完整验收**

Run:

```bash
cd sign && npm run test:unit && npm run build && npm run test:e2e
cd ../web_project && pytest -q
python manage.py check --deploy --settings=web_project.settings.prod
```

Expected: 全部 PASS。

- [ ] **Step 8: Commit**

```bash
git add sign/src/views/demo sign/src/demo sign/tests/e2e/competition-demo.spec.js web_project/demo docs
git commit -m "feat: deliver competition demo and release acceptance"
```

---

## 5. 发布验收标准

### 比赛版

- 评委打开页面 5 秒内理解“手语识别与翻译”。
- 无需账号即可体验官方样例，90 秒内完成完整演示。
- 页面不出现空白图表、控制台错误、硬编码无来源指标和第三方个人站点链接。
- 公开展示准确率时同时显示模型版本、数据集、样本量、统计日期。
- 断网、模型服务不可用、摄像头拒绝时有可解释降级。

### 商业试点版

- 所有密钥、口令、允许域名和 CORS 来源来自环境变量。
- 用户密码迁移为 Django 安全哈希，登录不通过 URL 参数，不记录密码/token。
- 图片、视频、模型和导出文件有用户归属、访问控制、保留期和删除策略。
- 异步任务支持排队、取消、超时、重试和审计。
- 生产部署可复现，具备健康检查、结构化日志、备份和回滚。
- 核心功能具备自动化测试，发布清单可重复执行。

---

## 6. 明确不做

- 不在本轮重新训练或调参模型。
- 不为了追求“高级感”加入无业务意义的 3D 地球、粒子、霓虹大屏或重动画。
- 不把现有 Vue/Django 全部重写成另一套框架。
- 不在普通识别页保留模型上传和管理员操作。
- 不用假数字装饰首页。
- 不在安全整改前部署到公网。

---

## 7. 参考

- Element Plus 官方主题能力：https://element-plus.org/en-US/guide/theming
- Ant Design 企业布局与 8px 节奏：https://ant.design/docs/spec/layout/ 、https://ant.design/docs/spec/proximity/
- W3C WCAG 2.2：https://www.w3.org/TR/WCAG22/
