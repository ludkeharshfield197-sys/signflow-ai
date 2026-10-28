<script setup>
import { Close, Grid } from '@element-plus/icons-vue'
import { watch } from 'vue'
import { useRoute } from 'vue-router'

import BrandMark from '@/components/brand/BrandMark.vue'
import { canAccessAdmin, productNavigation } from './navigation'

const props = defineProps({
  open: { type: Boolean, default: false },
  role: { type: String, default: 'user' },
})

const emit = defineEmits(['close'])
const route = useRoute()

watch(
  () => route.fullPath,
  () => {
    if (props.open) emit('close')
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition name="sf-drawer">
      <div v-if="open" class="sf-mobile-nav" role="dialog" aria-modal="true" aria-label="移动导航">
        <button class="sf-mobile-nav__backdrop" type="button" aria-label="关闭导航" @click="$emit('close')" />
        <aside class="sf-mobile-nav__panel">
          <div class="sf-mobile-nav__header">
            <BrandMark />
            <button class="sf-mobile-nav__close sf-button-reset" type="button" aria-label="关闭导航" @click="$emit('close')">
              <el-icon :size="20"><Close /></el-icon>
            </button>
          </div>
          <nav class="sf-mobile-nav__links" aria-label="产品功能">
            <RouterLink v-for="item in productNavigation" :key="item.to" class="sf-mobile-nav__item" :to="item.to">
              <el-icon :size="20"><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
            </RouterLink>
          </nav>
          <RouterLink v-if="canAccessAdmin(role)" class="sf-mobile-nav__admin" to="/admin/users">
            <el-icon :size="20"><Grid /></el-icon>
            <span>管理后台</span>
          </RouterLink>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.sf-mobile-nav {
  position: fixed;
  z-index: 1000;
  inset: 0;
}

.sf-mobile-nav__backdrop {
  position: absolute;
  inset: 0;
  width: 100%;
  border: 0;
  background: rgb(11 18 32 / 48%);
  backdrop-filter: blur(2px);
}

.sf-mobile-nav__panel {
  position: absolute;
  inset: 0 auto 0 0;
  display: flex;
  width: min(86vw, 320px);
  padding: var(--sf-space-4);
  flex-direction: column;
  background: var(--sf-color-surface);
  box-shadow: var(--sf-shadow-overlay);
}

.sf-mobile-nav__header {
  display: flex;
  height: 48px;
  align-items: center;
  justify-content: space-between;
}

.sf-mobile-nav__close {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: var(--sf-radius-control);
  color: var(--sf-color-text-muted);
}

.sf-mobile-nav__links {
  display: flex;
  margin-top: var(--sf-space-8);
  flex: 1;
  flex-direction: column;
  gap: var(--sf-space-1);
}

.sf-mobile-nav__item,
.sf-mobile-nav__admin {
  display: flex;
  min-height: 48px;
  padding: 0 var(--sf-space-4);
  align-items: center;
  gap: var(--sf-space-3);
  border-radius: var(--sf-radius-control);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
  font-weight: 650;
}

.sf-mobile-nav__item.router-link-active,
.sf-mobile-nav__admin.router-link-active {
  background: var(--sf-color-primary-soft);
  color: var(--sf-color-primary);
}

.sf-mobile-nav__admin {
  border-top: 1px solid var(--sf-color-border);
  border-radius: 0;
}

.sf-drawer-enter-active,
.sf-drawer-leave-active {
  transition: opacity var(--sf-motion-base) var(--sf-ease);
}

.sf-drawer-enter-active .sf-mobile-nav__panel,
.sf-drawer-leave-active .sf-mobile-nav__panel {
  transition: transform var(--sf-motion-base) var(--sf-ease);
}

.sf-drawer-enter-from,
.sf-drawer-leave-to { opacity: 0; }
.sf-drawer-enter-from .sf-mobile-nav__panel,
.sf-drawer-leave-to .sf-mobile-nav__panel { transform: translateX(-100%); }
</style>

