# SignFlow AI — Accessible AI Studio

This directory contains the accepted visual references for the commercial and
competition redesign. Product controls, labels, tables, charts, and results are
implemented as native Vue components; the concept screenshots are visual
references only.

## Reference surfaces

- `landing-desktop-concept.png`: public product story, hero balance, product
  preview, and open-section rhythm.
- `overview-desktop-concept.png`: authenticated shell, navigation, operational
  overview, chart/list density, and table treatment.
- `workbench-desktop-concept.png`: three-column recognition workflow, canvas
  priority, settings, results, and timeline.
- `mobile-overview-workbench-concept.png`: responsive navigation, list
  conversion, mobile workbench order, and touch sizing.

## Locked visual direction

- Backgrounds: true white and cool `#f7f9fc`; never cream or warm gray.
- Primary: indigo `#5b5bd6`; success/live: teal `#0e9384`.
- Media canvas: `#0b1220`; body text: `#182230`; muted text: `#667085`.
- Typography: Inter, PingFang SC, Microsoft YaHei, sans-serif.
- Geometry: 8px spacing grid, 10px controls, 16px major panels.
- Containers: open bands, rails, lists, tables, and one purposeful media frame.
  Do not convert every region into a floating card.
- Icons: one consistent Element Plus outline family; no emoji or text glyphs.
- Motion: 150–240ms for navigation, drawers, task progress, and result reveal,
  with reduced-motion support.

## Above-the-fold copy lock

Public page: `SignFlow AI`, `产品能力`, `技术与安全`, `应用场景`, `登录`,
`让每一次手语表达，都被准确看见`, `面向图片、视频与实时场景的智能手语识别工作台，让沟通更自然，让技术更有温度。`,
`体验官方样例`, `登录系统`.

Authenticated overview: `概览`, `识别工作台`, `结果中心`, `数据洞察`,
`模型中心`, `设置`, `管理后台`, `开始识别`.

Workbench: `实时摄像头`, `图片`, `视频`, `输入来源`, `标准`, `高精度`,
`低延迟`, `高级设置`, `识别结果`, `保存结果`, `导出报告`.

## Responsive contract

- Desktop shell: 232px expanded sidebar, collapsible to 76px.
- Tablet: collapsed rail by default.
- Mobile: no fixed desktop sidebar; use a drawer and one natural page scroll.
- Minimum target size: 44×44px.
- Tables become semantic list rows on narrow screens.
- Workbench order on mobile: mode → media → result → actions → input/settings.
- Never hide overflow to mask a layout defect.

