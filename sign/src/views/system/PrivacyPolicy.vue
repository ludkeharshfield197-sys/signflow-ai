<script setup>
import { Check, Delete, Document, Lock, View } from '@element-plus/icons-vue'

import PublicFooter from '@/components/marketing/PublicFooter.vue'
import PublicHeader from '@/components/marketing/PublicHeader.vue'

const principles = [
  {
    icon: Lock,
    title: '用途限定',
    description: '图片、视频和摄像头帧仅用于完成用户主动发起的识别任务，不会默认进入训练集。',
  },
  {
    icon: View,
    title: '访问受控',
    description: '原始媒体、识别结果和追溯记录仅向任务所有者及经授权的系统管理员开放。',
  },
  {
    icon: Delete,
    title: '保留可控',
    description: '任务媒体默认保留 30 天；部署方可缩短期限，用户也可以在到期前申请删除。',
  },
]
</script>

<template>
  <div class="sf-privacy">
    <PublicHeader />

    <main>
      <header class="sf-privacy__hero">
        <span>PRIVACY &amp; RETENTION</span>
        <h1>隐私与数据保留</h1>
        <p>
          本说明解释 SignFlow AI 在图片、视频和实时手语识别过程中如何收集、使用、
          保存和保护数据，以及你可以如何查看、导出或删除自己的记录。
        </p>
        <div>
          <strong>当前版本</strong>
          <span>2026 年 7 月 30 日生效</span>
        </div>
      </header>

      <section class="sf-privacy__principles" aria-label="隐私原则">
        <article v-for="item in principles" :key="item.title">
          <div><el-icon :size="24"><component :is="item.icon" /></el-icon></div>
          <h2>{{ item.title }}</h2>
          <p>{{ item.description }}</p>
        </article>
      </section>

      <section class="sf-privacy__body">
        <aside aria-label="本页目录">
          <strong>本页目录</strong>
          <a href="#data">处理的数据</a>
          <a href="#purpose">使用目的</a>
          <a href="#retention">保留与删除</a>
          <a href="#access">访问与共享</a>
          <a href="#security">安全措施</a>
          <a href="#rights">你的权利</a>
          <a href="#limits">模型边界</a>
        </aside>

        <article>
          <section id="data">
            <span>01</span>
            <h2>我们处理哪些数据</h2>
            <p>
              当你发起识别时，系统会处理你选择的图片、视频或摄像头画面，以及文件名、
              文件类型、大小和文件哈希。系统还会记录模型名称与版本、识别参数、任务状态、
              识别标签、置信度、处理耗时、确认状态和必要的安全审计信息。
            </p>
            <p>
              账号信息限于登录、权限控制和结果归属所需的字段。密码仅以安全散列形式保存；
              客户端不会把密码写入 URL、识别记录或业务日志。
            </p>
          </section>

          <section id="purpose">
            <span>02</span>
            <h2>数据如何被使用</h2>
            <p>
              数据用于执行识别、展示结果、支持重新识别与版本对比、生成统计信息、排查故障
              以及防止未授权访问。未经用户另行明确授权，上传内容不会用于训练、微调或扩充模型数据集。
            </p>
          </section>

          <section id="retention">
            <span>03</span>
            <h2>保留期限与删除机制</h2>
            <p>
              原始媒体和任务记录默认保留 30 天，并在到期后由清理任务删除。部署组织可以根据
              业务要求配置更短期限。已删除或到期的原始文件不再用于重新识别；必要的安全审计记录
              可按适用要求单独保留，但不会包含可直接播放的原始媒体。
            </p>
            <p>
              浏览器中的官方样例结果和本机协助卡保存在当前设备，可通过浏览器数据设置清除。
            </p>
          </section>

          <section id="access">
            <span>04</span>
            <h2>访问、授权与共享</h2>
            <p>
              已登录用户只能访问归属于自己的任务。原始媒体通过短期授权地址或受保护接口提供，
              不公开真实存储路径。除提供基础设施所必需的数据库、缓存和对象存储服务外，
              系统不会主动向第三方出售或共享识别内容。
            </p>
          </section>

          <section id="security">
            <span>05</span>
            <h2>安全保护措施</h2>
            <ul>
              <li><el-icon><Check /></el-icon>生产环境使用 HTTPS、安全 Cookie、严格来源白名单和访问令牌。</li>
              <li><el-icon><Check /></el-icon>对象存储凭据、数据库密码和签名密钥仅通过私密环境配置加载。</li>
              <li><el-icon><Check /></el-icon>文件类型、体积和路径经过服务端校验，原始存储键不会在列表接口中暴露。</li>
              <li><el-icon><Check /></el-icon>结果保留文件哈希、模型版本和参数快照，便于核验与审计。</li>
            </ul>
          </section>

          <section id="rights">
            <span>06</span>
            <h2>你的数据权利</h2>
            <p>
              你可以在结果中心查看自己的任务与追溯信息，并可联系当前系统部署方申请导出、
              更正账号资料、提前删除原始媒体或撤回额外授权。处理请求时，部署方可能需要先核验账号归属。
            </p>
          </section>

          <section id="limits">
            <span>07</span>
            <h2>模型能力边界</h2>
            <p>
              识别结果可能受手语体系、光线、遮挡、动作速度、拍摄角度和类别覆盖范围影响。
              本产品用于沟通辅助，不替代人工手语翻译、医疗诊断、紧急救援或其他专业判断。
              对关键内容，请由沟通双方确认后再采取行动。
            </p>
          </section>

          <footer>
            <el-icon :size="22"><Document /></el-icon>
            <p>
              隐私规则或产品能力发生实质变化时，本页会更新版本日期。有关数据处理的问题，
              请通过当前部署组织提供的系统管理员或支持渠道联系。
            </p>
          </footer>
        </article>
      </section>
    </main>

    <PublicFooter />
  </div>
</template>

<style scoped>
.sf-privacy { min-height: 100vh; background: var(--sf-color-bg); }
.sf-privacy__hero {
  padding: 88px max(var(--sf-space-8), calc((100vw - 1120px) / 2)) 72px;
  border-bottom: 1px solid var(--sf-color-border);
  background:
    radial-gradient(circle at 78% 12%, rgb(91 91 214 / 13%), transparent 32%),
    var(--sf-color-surface);
}
.sf-privacy__hero > span { color: var(--sf-color-primary); font-size: 11px; font-weight: 800; letter-spacing: .12em; }
.sf-privacy__hero h1 { max-width: 760px; margin: var(--sf-space-4) 0 0; font-size: clamp(42px, 6vw, 68px); letter-spacing: -.055em; line-height: 1.05; }
.sf-privacy__hero > p { max-width: 760px; margin: var(--sf-space-5) 0 0; color: var(--sf-color-text-secondary); font-size: var(--sf-text-md); line-height: 1.85; }
.sf-privacy__hero > div { display: flex; margin-top: var(--sf-space-6); gap: var(--sf-space-3); color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-privacy__hero > div strong { color: var(--sf-color-text-secondary); }
.sf-privacy__principles { display: grid; width: min(calc(100% - 48px), 1120px); margin: -28px auto 0; grid-template-columns: repeat(3, 1fr); gap: var(--sf-space-4); }
.sf-privacy__principles article { padding: var(--sf-space-6); border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-card); background: var(--sf-color-surface); box-shadow: var(--sf-shadow-card); }
.sf-privacy__principles article > div { display: grid; width: 44px; height: 44px; place-items: center; border-radius: 12px; background: var(--sf-color-primary-soft); color: var(--sf-color-primary); }
.sf-privacy__principles h2 { margin: var(--sf-space-4) 0 0; font-size: var(--sf-text-lg); }
.sf-privacy__principles p { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); line-height: 1.75; }
.sf-privacy__body { display: grid; width: min(calc(100% - 48px), 1120px); padding: 72px 0 96px; margin: 0 auto; grid-template-columns: 220px minmax(0, 1fr); gap: 72px; }
.sf-privacy__body aside { position: sticky; top: 104px; display: flex; height: fit-content; flex-direction: column; gap: var(--sf-space-2); }
.sf-privacy__body aside strong { margin-bottom: var(--sf-space-3); font-size: var(--sf-text-sm); }
.sf-privacy__body aside a { padding: 7px 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); font-weight: 650; }
.sf-privacy__body aside a:hover { color: var(--sf-color-primary); }
.sf-privacy__body article > section { scroll-margin-top: 96px; padding: 0 0 var(--sf-space-10); margin-bottom: var(--sf-space-10); border-bottom: 1px solid var(--sf-color-border); }
.sf-privacy__body article > section > span { color: var(--sf-color-primary); font-family: var(--sf-font-mono); font-size: 11px; font-weight: 800; }
.sf-privacy__body h2 { margin: var(--sf-space-2) 0 var(--sf-space-4); font-size: var(--sf-text-2xl); letter-spacing: -.035em; }
.sf-privacy__body article p { margin: var(--sf-space-3) 0 0; color: var(--sf-color-text-secondary); font-size: var(--sf-text-sm); line-height: 1.95; }
.sf-privacy__body ul { display: grid; padding: 0; margin: var(--sf-space-5) 0 0; gap: var(--sf-space-3); list-style: none; }
.sf-privacy__body li { display: flex; align-items: flex-start; gap: var(--sf-space-3); color: var(--sf-color-text-secondary); font-size: var(--sf-text-sm); line-height: 1.75; }
.sf-privacy__body li .el-icon { margin-top: 4px; flex: 0 0 auto; color: var(--sf-color-accent); }
.sf-privacy__body article > footer { display: flex; padding: var(--sf-space-5); align-items: flex-start; gap: var(--sf-space-4); border: 1px solid #b8e5dd; border-radius: var(--sf-radius-card); background: var(--sf-color-accent-soft); color: var(--sf-color-accent); }
.sf-privacy__body article > footer p { margin: 0; color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
@media (max-width: 820px) {
  .sf-privacy__principles { grid-template-columns: 1fr; }
  .sf-privacy__body { grid-template-columns: 1fr; gap: var(--sf-space-8); }
  .sf-privacy__body aside { position: static; display: grid; grid-template-columns: 1fr 1fr; }
  .sf-privacy__body aside strong { grid-column: 1 / -1; }
}
@media (max-width: 640px) {
  .sf-privacy__hero { padding: 64px var(--sf-space-4) 56px; }
  .sf-privacy__principles,
  .sf-privacy__body { width: calc(100% - 32px); }
  .sf-privacy__body { padding-block: 56px 72px; }
}
</style>
