<script setup>
import { ArrowLeftBold, ArrowRightBold, Grid } from '@element-plus/icons-vue'

import BrandMark from '@/components/brand/BrandMark.vue'
import { canAccessAdmin, productNavigation } from './navigation'

defineProps({
  role: { type: String, default: 'user' },
  collapsed: { type: Boolean, default: false },
})

defineEmits(['toggle'])
</script>

<template>
  <aside class="sf-sidebar" :class="{ 'sf-sidebar--collapsed': collapsed }" aria-label="产品导航">
    <div class="sf-sidebar__brand">
      <BrandMark :compact="collapsed" />
    </div>

    <nav class="sf-sidebar__nav" aria-label="主要功能">
      <RouterLink
        v-for="item in productNavigation"
        :key="item.to"
        class="sf-sidebar__item"
        :to="item.to"
        :title="collapsed ? item.label : undefined"
      >
        <el-icon :size="19"><component :is="item.icon" /></el-icon>
        <span v-if="!collapsed">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sf-sidebar__footer">
      <div v-if="canAccessAdmin(role)" class="sf-sidebar__admin">
        <span v-if="!collapsed" class="sf-sidebar__group-label">管理</span>
        <RouterLink
          class="sf-sidebar__item"
          to="/admin/users"
          :title="collapsed ? '管理后台' : undefined"
        >
          <el-icon :size="19"><Grid /></el-icon>
          <span v-if="!collapsed">管理后台</span>
        </RouterLink>
      </div>
      <button
        class="sf-sidebar__collapse"
        type="button"
        :aria-label="collapsed ? '展开侧栏' : '收起侧栏'"
        @click="$emit('toggle')"
      >
        <el-icon><component :is="collapsed ? ArrowRightBold : ArrowLeftBold" /></el-icon>
        <span v-if="!collapsed">收起侧栏</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sf-sidebar {
  position: fixed;
  z-index: 30;
  inset: 0 auto 0 0;
  display: flex;
  width: var(--sf-sidebar-width);
  min-width: 0;
  padding: var(--sf-space-4) var(--sf-space-3);
  flex-direction: column;
  border-right: 1px solid var(--sf-color-border);
  background: var(--sf-color-surface);
  transition: width var(--sf-motion-base) var(--sf-ease);
}

.sf-sidebar--collapsed {
  width: var(--sf-sidebar-collapsed-width);
}

.sf-sidebar__brand {
  display: flex;
  height: 48px;
  padding: 5px 9px;
  align-items: center;
}

.sf-sidebar__nav {
  display: flex;
  min-height: 0;
  margin-top: var(--sf-space-6);
  flex: 1;
  flex-direction: column;
  gap: var(--sf-space-1);
}

.sf-sidebar__item,
.sf-sidebar__collapse {
  display: flex;
  width: 100%;
  min-height: 44px;
  padding: 0 13px;
  align-items: center;
  gap: var(--sf-space-3);
  border: 0;
  border-radius: var(--sf-radius-control);
  background: transparent;
  color: var(--sf-color-text-muted);
  cursor: pointer;
  font-size: var(--sf-text-sm);
  font-weight: 650;
  text-align: left;
  transition:
    color var(--sf-motion-fast) var(--sf-ease),
    background var(--sf-motion-fast) var(--sf-ease);
}

.sf-sidebar__item:hover,
.sf-sidebar__collapse:hover {
  background: var(--sf-color-surface-subtle);
  color: var(--sf-color-text);
}

.sf-sidebar__item.router-link-active {
  background: var(--sf-color-primary-soft);
  color: var(--sf-color-primary);
}

.sf-sidebar--collapsed .sf-sidebar__item,
.sf-sidebar--collapsed .sf-sidebar__collapse {
  justify-content: center;
  padding-inline: 0;
}

.sf-sidebar__footer {
  display: grid;
  gap: var(--sf-space-3);
  padding-top: var(--sf-space-4);
  border-top: 1px solid var(--sf-color-border);
}

.sf-sidebar__admin {
  display: grid;
  gap: var(--sf-space-1);
}

.sf-sidebar__group-label {
  padding: 0 13px var(--sf-space-1);
  color: var(--sf-color-text-disabled);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.sf-sidebar__collapse {
  color: var(--sf-color-text-disabled);
}

@media (max-width: 1023px) {
  .sf-sidebar {
    display: none;
  }
}
</style>
