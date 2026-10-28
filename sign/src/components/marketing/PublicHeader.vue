<script setup>
import { Close, Menu } from '@element-plus/icons-vue'
import { ref } from 'vue'

import BrandMark from '@/components/brand/BrandMark.vue'

const menuOpen = ref(false)
</script>

<template>
  <header class="sf-public-header">
    <div class="sf-public-header__inner">
      <RouterLink to="/" aria-label="SignFlow AI 首页"><BrandMark /></RouterLink>
      <nav class="sf-public-header__nav" aria-label="公开页面导航">
        <RouterLink to="/#capabilities">产品能力</RouterLink>
        <RouterLink to="/#security">技术与安全</RouterLink>
        <RouterLink to="/#scenarios">应用场景</RouterLink>
      </nav>
      <div class="sf-public-header__actions">
        <RouterLink class="sf-public-header__demo" to="/product-tour">产品导览</RouterLink>
        <RouterLink class="sf-public-header__login" to="/auth/login">登录</RouterLink>
      </div>
      <button
        class="sf-public-header__menu sf-button-reset"
        type="button"
        :aria-expanded="menuOpen"
        aria-controls="mobile-public-nav"
        :aria-label="menuOpen ? '关闭导航' : '打开导航'"
        @click="menuOpen = !menuOpen"
      >
        <el-icon :size="22"><component :is="menuOpen ? Close : Menu" /></el-icon>
      </button>
    </div>
    <Transition name="sf-public-menu">
      <nav v-if="menuOpen" id="mobile-public-nav" class="sf-public-header__mobile" aria-label="移动公开导航">
        <RouterLink to="/#capabilities" @click="menuOpen = false">产品能力</RouterLink>
        <RouterLink to="/#security" @click="menuOpen = false">技术与安全</RouterLink>
        <RouterLink to="/#scenarios" @click="menuOpen = false">应用场景</RouterLink>
        <RouterLink to="/product-tour" @click="menuOpen = false">产品导览</RouterLink>
        <RouterLink class="sf-public-header__mobile-login" to="/auth/login" @click="menuOpen = false">登录系统</RouterLink>
      </nav>
    </Transition>
  </header>
</template>

<style scoped>
.sf-public-header {
  position: sticky;
  z-index: 50;
  top: 0;
  border-bottom: 1px solid var(--sf-color-border);
  background: rgb(255 255 255 / 94%);
  backdrop-filter: blur(14px);
}

.sf-public-header__inner {
  display: flex;
  width: min(100%, 1440px);
  height: 72px;
  padding: 0 var(--sf-space-8);
  margin: 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: var(--sf-space-8);
}

.sf-public-header__nav,
.sf-public-header__actions {
  display: flex;
  align-items: center;
}

.sf-public-header__nav { gap: var(--sf-space-10); }
.sf-public-header__actions { gap: var(--sf-space-3); }

.sf-public-header__nav a {
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-sm);
  font-weight: 650;
}

.sf-public-header__nav a:hover { color: var(--sf-color-primary); }

.sf-public-header__demo,
.sf-public-header__login {
  display: inline-flex;
  min-height: 40px;
  padding: 0 var(--sf-space-4);
  align-items: center;
  justify-content: center;
  border-radius: var(--sf-radius-control);
  font-size: var(--sf-text-sm);
  font-weight: 700;
}

.sf-public-header__demo { color: var(--sf-color-text-secondary); }
.sf-public-header__demo:hover { background: var(--sf-color-surface-subtle); }
.sf-public-header__login { background: var(--sf-color-primary); color: white; }
.sf-public-header__login:hover { background: var(--sf-color-primary-hover); }

.sf-public-header__menu,
.sf-public-header__mobile { display: none; }

@media (max-width: 820px) {
  .sf-public-header__inner { height: 64px; padding: 0 var(--sf-space-4); }
  .sf-public-header__nav,
  .sf-public-header__actions { display: none; }
  .sf-public-header__menu {
    display: grid;
    width: 44px;
    height: 44px;
    place-items: center;
    border-radius: var(--sf-radius-control);
  }
  .sf-public-header__mobile {
    display: grid;
    padding: var(--sf-space-3) var(--sf-space-4) var(--sf-space-5);
    gap: var(--sf-space-1);
    border-top: 1px solid var(--sf-color-border);
    background: var(--sf-color-surface);
  }
  .sf-public-header__mobile a {
    display: flex;
    min-height: 48px;
    padding: 0 var(--sf-space-3);
    align-items: center;
    border-radius: var(--sf-radius-control);
    color: var(--sf-color-text-secondary);
    font-size: var(--sf-text-sm);
    font-weight: 650;
  }
  .sf-public-header__mobile-login {
    margin-top: var(--sf-space-2);
    justify-content: center;
    background: var(--sf-color-primary);
    color: white !important;
  }
}

.sf-public-menu-enter-active,
.sf-public-menu-leave-active { transition: opacity var(--sf-motion-fast) var(--sf-ease); }
.sf-public-menu-enter-from,
.sf-public-menu-leave-to { opacity: 0; }
</style>
