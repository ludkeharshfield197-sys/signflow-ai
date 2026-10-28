<script setup>
import { Expand, QuestionFilled } from '@element-plus/icons-vue'

import StatusBadge from '@/components/ui/StatusBadge.vue'

defineProps({
  title: { type: String, default: 'SignFlow AI' },
  user: { type: Object, default: () => ({ displayName: '演示用户', role: 'user' }) },
})

defineEmits(['menu', 'logout'])
</script>

<template>
  <header class="sf-topbar">
    <div class="sf-topbar__leading">
      <button class="sf-topbar__menu sf-button-reset" type="button" aria-label="打开导航" @click="$emit('menu')">
        <el-icon :size="21"><Expand /></el-icon>
      </button>
      <span class="sf-topbar__title">{{ title }}</span>
    </div>
    <div class="sf-topbar__actions">
      <StatusBadge class="sf-topbar__status" label="服务运行正常" tone="success" pulse />
      <RouterLink class="sf-topbar__icon sf-button-reset" to="/product-tour" aria-label="打开产品导览">
        <el-icon :size="19"><QuestionFilled /></el-icon>
      </RouterLink>
      <el-dropdown trigger="click" @command="(command) => command === 'logout' && $emit('logout')">
        <button class="sf-topbar__profile sf-button-reset" type="button">
          <span class="sf-topbar__avatar">{{ user.displayName?.slice(0, 1) || '用' }}</span>
          <span class="sf-topbar__profile-copy">
            <strong>{{ user.displayName || user.username || '演示用户' }}</strong>
            <small>{{ ['admin', 'superadmin'].includes(user.role) ? '管理员' : '专业版' }}</small>
          </span>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped>
.sf-topbar {
  position: sticky;
  z-index: 20;
  top: 0;
  display: flex;
  height: var(--sf-header-height);
  padding: 0 var(--sf-space-8);
  align-items: center;
  justify-content: space-between;
  gap: var(--sf-space-4);
  border-bottom: 1px solid var(--sf-color-border);
  background: rgb(255 255 255 / 94%);
  backdrop-filter: blur(12px);
}

.sf-topbar__leading,
.sf-topbar__actions,
.sf-topbar__profile {
  display: flex;
  min-width: 0;
  align-items: center;
}

.sf-topbar__leading { gap: var(--sf-space-3); }
.sf-topbar__actions { gap: var(--sf-space-3); }
.sf-topbar__menu { display: none; }

.sf-topbar__title {
  overflow: hidden;
  font-size: var(--sf-text-sm);
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sf-topbar__icon,
.sf-topbar__menu {
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: var(--sf-radius-control);
  color: var(--sf-color-text-muted);
}

.sf-topbar__icon { display: grid; }
.sf-topbar__icon:hover,
.sf-topbar__menu:hover { background: var(--sf-color-surface-subtle); color: var(--sf-color-text); }

.sf-topbar__profile {
  gap: var(--sf-space-2);
  padding: 4px 6px;
  border-radius: var(--sf-radius-control);
  cursor: pointer;
}

.sf-topbar__profile:hover { background: var(--sf-color-surface-subtle); }

.sf-topbar__avatar {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 50%;
  background: var(--sf-color-primary);
  color: white;
  font-size: var(--sf-text-sm);
  font-weight: 750;
}

.sf-topbar__profile-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.sf-topbar__profile-copy strong { font-size: var(--sf-text-xs); }
.sf-topbar__profile-copy small { margin-top: 3px; color: var(--sf-color-text-muted); font-size: 10px; }

@media (max-width: 1023px) {
  .sf-topbar__menu { display: grid; }
}

@media (max-width: 767px) {
  .sf-topbar { padding: 0 var(--sf-space-4); }
  .sf-topbar__status,
  .sf-topbar__icon,
  .sf-topbar__profile-copy { display: none; }
}
</style>
