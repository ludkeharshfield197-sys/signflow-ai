<script setup>
import { Lock, MagicStick, Monitor } from '@element-plus/icons-vue'

import BrandMark from '@/components/brand/BrandMark.vue'

defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
})

const currentYear = new Date().getFullYear()
</script>

<template>
  <main class="sf-auth">
    <section class="sf-auth__story" aria-label="SignFlow AI 产品介绍">
      <RouterLink to="/" aria-label="返回 SignFlow AI 首页">
        <BrandMark inverse />
      </RouterLink>
      <div class="sf-auth__story-copy">
        <h2>让手语表达被准确看见</h2>
        <p>一个账号即可使用图片、视频与实时识别，并在结果中心安全追溯每次任务。</p>
        <ul>
          <li><el-icon><MagicStick /></el-icon><span>统一识别工作台</span></li>
          <li><el-icon><Monitor /></el-icon><span>完整结果与模型追溯</span></li>
          <li><el-icon><Lock /></el-icon><span>隐私优先的数据策略</span></li>
        </ul>
      </div>
      <p class="sf-auth__story-note">官方演示样例无需账号即可体验</p>
    </section>

    <section class="sf-auth__form-side">
      <div class="sf-auth__mobile-brand">
        <RouterLink to="/"><BrandMark /></RouterLink>
      </div>
      <div class="sf-auth__form-wrap">
        <header class="sf-auth__header">
          <h1>{{ title }}</h1>
          <p>{{ description }}</p>
        </header>
        <slot />
      </div>
      <footer class="sf-auth__footer">
        <span>© {{ currentYear }} SignFlow AI</span>
        <RouterLink to="/privacy">隐私政策</RouterLink>
        <a href="/health/ready" target="_blank" rel="noreferrer">服务状态</a>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.sf-auth {
  display: grid;
  min-height: 100vh;
  grid-template-columns: minmax(360px, 0.9fr) minmax(520px, 1.1fr);
  background: var(--sf-color-surface);
}

.sf-auth__story {
  display: flex;
  min-width: 0;
  padding: clamp(32px, 5vw, 72px);
  flex-direction: column;
  justify-content: space-between;
  background:
    radial-gradient(circle at 80% 15%, rgb(91 91 214 / 24%), transparent 34%),
    var(--sf-color-canvas);
  color: white;
}

.sf-auth__story-copy {
  max-width: 500px;
  margin-block: var(--sf-space-12);
}

.sf-auth__story-copy h2 {
  margin-bottom: var(--sf-space-5);
  font-size: clamp(32px, 4vw, 52px);
  line-height: 1.2;
  letter-spacing: -0.04em;
}

.sf-auth__story-copy p {
  color: #c7cfdf;
  font-size: var(--sf-text-md);
  line-height: 1.8;
}

.sf-auth__story-copy ul {
  display: grid;
  padding: 0;
  margin: var(--sf-space-8) 0 0;
  gap: var(--sf-space-4);
  list-style: none;
}

.sf-auth__story-copy li {
  display: flex;
  align-items: center;
  gap: var(--sf-space-3);
  color: #e8ecf5;
  font-size: var(--sf-text-sm);
  font-weight: 650;
}

.sf-auth__story-copy li .el-icon { color: #8e8ef0; }

.sf-auth__story-note {
  margin: 0;
  color: #98a2b3;
  font-size: var(--sf-text-xs);
}

.sf-auth__form-side {
  display: flex;
  min-width: 0;
  padding: var(--sf-space-8);
  flex-direction: column;
}

.sf-auth__mobile-brand { display: none; }

.sf-auth__form-wrap {
  width: min(100%, 440px);
  margin: auto;
}

.sf-auth__header {
  margin-bottom: var(--sf-space-8);
}

.sf-auth__header h1 {
  margin: 0;
  font-size: var(--sf-text-3xl);
  line-height: 1.25;
  letter-spacing: -0.035em;
}

.sf-auth__header p {
  margin: var(--sf-space-3) 0 0;
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
  line-height: 1.7;
}

.sf-auth__footer {
  display: flex;
  justify-content: center;
  gap: var(--sf-space-5);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-xs);
}

.sf-auth__footer a:hover { color: var(--sf-color-primary); }

@media (max-width: 899px) {
  .sf-auth { display: block; }
  .sf-auth__story { display: none; }
  .sf-auth__form-side { min-height: 100vh; padding: var(--sf-space-6) var(--sf-space-4); }
  .sf-auth__mobile-brand { display: block; margin-bottom: var(--sf-space-12); }
  .sf-auth__form-wrap { margin: 0 auto auto; }
  .sf-auth__footer { flex-wrap: wrap; margin-top: var(--sf-space-10); }
}
</style>
