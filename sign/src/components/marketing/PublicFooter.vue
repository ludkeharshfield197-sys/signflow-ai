<script setup>
import BrandMark from '@/components/brand/BrandMark.vue'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="sf-public-footer">
    <div class="sf-public-footer__inner">
      <div>
        <BrandMark />
        <p>让无障碍沟通成为每个数字场景的基础能力。</p>
      </div>
      <nav aria-label="页脚导航">
        <RouterLink to="/#capabilities">产品能力</RouterLink>
        <RouterLink to="/privacy">隐私政策</RouterLink>
        <a id="status" href="/health/ready" target="_blank" rel="noreferrer">服务状态</a>
        <RouterLink to="/auth/login">登录系统</RouterLink>
      </nav>
    </div>
    <div class="sf-public-footer__legal">
      <span>© {{ year }} SignFlow AI. 保留所有权利。</span>
      <span>官方样例均标注来源与授权范围</span>
    </div>
  </footer>
</template>

<style scoped>
.sf-public-footer {
  padding: var(--sf-space-16) max(var(--sf-space-8), calc((100vw - 1376px) / 2));
  border-top: 1px solid var(--sf-color-border);
  background: var(--sf-color-surface);
}

.sf-public-footer__inner,
.sf-public-footer__legal {
  display: flex;
  justify-content: space-between;
  gap: var(--sf-space-8);
}

.sf-public-footer__inner p {
  max-width: 420px;
  margin: var(--sf-space-4) 0 0;
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
}

.sf-public-footer__inner nav {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: var(--sf-space-6);
}

.sf-public-footer a {
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-sm);
  font-weight: 650;
}

.sf-public-footer a:hover { color: var(--sf-color-primary); }

.sf-public-footer__legal {
  padding-top: var(--sf-space-8);
  margin-top: var(--sf-space-10);
  border-top: 1px solid var(--sf-color-border);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-xs);
}

@media (max-width: 767px) {
  .sf-public-footer { padding: var(--sf-space-12) var(--sf-space-4); }
  .sf-public-footer__inner,
  .sf-public-footer__legal { flex-direction: column; }
  .sf-public-footer__inner nav { display: grid; grid-template-columns: 1fr 1fr; }
}
</style>
