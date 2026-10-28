<script setup>
import { DataLine, Key, Lock, SwitchButton, User } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { logout } from '@/services/auth'
import { useSession } from '@/services/session'

const router = useRouter()
const { state } = useSession()

const roleLabel = computed(() => (
  ['admin', 'superadmin'].includes(state.user?.role) ? '管理员' : '普通用户'
))

async function signOut() {
  await logout().catch(() => {})
  await router.replace({ path: '/auth/login', query: { loggedOut: '1' } })
}
</script>

<template>
  <section class="sf-settings sf-page">
    <PageHeader
      title="账户与设置"
      description="查看当前账户、安全会话和数据保留策略。敏感凭据不会显示在浏览器中。"
    >
      <template #actions>
        <el-button @click="signOut">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </template>
    </PageHeader>

    <div class="sf-settings__grid">
      <article class="sf-settings__profile sf-panel">
        <header>
          <span class="sf-settings__avatar">{{ state.user?.displayName?.slice(0, 1) || '用' }}</span>
          <div>
            <h2>{{ state.user?.displayName || state.user?.username }}</h2>
            <p>@{{ state.user?.username }}</p>
          </div>
          <StatusBadge :label="roleLabel" :tone="roleLabel === '管理员' ? 'processing' : 'neutral'" />
        </header>
        <dl>
          <div><dt>账户编号</dt><dd>{{ state.user?.id || '—' }}</dd></div>
          <div><dt>邮箱</dt><dd>{{ state.user?.email || '未设置' }}</dd></div>
          <div><dt>账户状态</dt><dd>正常</dd></div>
        </dl>
      </article>

      <div class="sf-settings__stack">
        <article class="sf-settings__card sf-panel">
          <span class="sf-settings__icon"><el-icon><Lock /></el-icon></span>
          <div>
            <h2>会话安全</h2>
            <p>访问令牌仅保存在当前页面内存；刷新令牌使用 HttpOnly Cookie，脚本无法读取。</p>
          </div>
          <StatusBadge label="已保护" tone="success" />
        </article>

        <article class="sf-settings__card sf-panel">
          <span class="sf-settings__icon"><el-icon><DataLine /></el-icon></span>
          <div>
            <h2>识别数据</h2>
            <p>上传素材、任务和结果按账户隔离。默认保留 30 天，管理员可通过部署配置调整并执行清理。</p>
          </div>
          <StatusBadge label="30 天默认值" tone="neutral" />
        </article>

        <article class="sf-settings__card sf-panel">
          <span class="sf-settings__icon"><el-icon><Key /></el-icon></span>
          <div>
            <h2>密码与权限</h2>
            <p>密码使用 Django 安全哈希保存；角色由管理员控制，页面与 API 会同时校验权限。</p>
          </div>
          <StatusBadge label="双重校验" tone="success" />
        </article>
      </div>
    </div>

    <section id="team" class="sf-settings__team sf-panel">
      <div>
        <span class="sf-settings__icon"><el-icon><User /></el-icon></span>
        <div>
          <h2>团队与成员</h2>
          <p>当前部署使用单工作区账户模型；管理员可在管理后台查看成员与角色分配。</p>
        </div>
      </div>
      <el-button
        v-if="['admin', 'superadmin'].includes(state.user?.role)"
        @click="router.push('/admin/users')"
      >
        打开管理后台
      </el-button>
    </section>
  </section>
</template>

<style scoped>
.sf-settings__grid { display: grid; grid-template-columns: minmax(280px, .8fr) minmax(0, 1.2fr); gap: var(--sf-space-4); }
.sf-settings__profile { align-self: start; padding: var(--sf-space-6); }
.sf-settings__profile header { display: flex; align-items: center; gap: var(--sf-space-3); padding-bottom: var(--sf-space-5); border-bottom: 1px solid var(--sf-color-border); }
.sf-settings__profile header > div { min-width: 0; flex: 1; }
.sf-settings__profile h2,
.sf-settings__card h2,
.sf-settings__team h2 { margin: 0; color: var(--sf-color-text); font-size: var(--sf-text-md); }
.sf-settings__profile p,
.sf-settings__card p,
.sf-settings__team p { margin: 4px 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.65; }
.sf-settings__avatar { display: grid; width: 48px; height: 48px; flex: 0 0 48px; place-items: center; border-radius: 14px; background: var(--sf-color-primary); color: white; font-weight: 750; }
.sf-settings__profile dl { display: grid; margin: var(--sf-space-4) 0 0; gap: var(--sf-space-1); }
.sf-settings__profile dl div { display: flex; min-height: 42px; align-items: center; justify-content: space-between; gap: var(--sf-space-4); font-size: var(--sf-text-xs); }
.sf-settings__profile dt { color: var(--sf-color-text-muted); }
.sf-settings__profile dd { overflow: hidden; margin: 0; color: var(--sf-color-text-secondary); font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
.sf-settings__stack { display: grid; gap: var(--sf-space-3); }
.sf-settings__card { display: grid; min-height: 108px; padding: var(--sf-space-5); grid-template-columns: 44px minmax(0, 1fr) auto; align-items: center; gap: var(--sf-space-4); }
.sf-settings__icon { display: grid; width: 44px; height: 44px; flex: 0 0 44px; place-items: center; border-radius: 12px; background: var(--sf-color-primary-soft); color: var(--sf-color-primary); font-size: 20px; }
.sf-settings__team { display: flex; margin-top: var(--sf-space-4); padding: var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-5); }
.sf-settings__team > div { display: flex; min-width: 0; align-items: center; gap: var(--sf-space-4); }

@media (max-width: 860px) {
  .sf-settings__grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .sf-settings__card { grid-template-columns: 44px minmax(0, 1fr); align-items: start; }
  .sf-settings__card :deep(.sf-status-badge) { grid-column: 2; justify-self: start; }
  .sf-settings__team { align-items: flex-start; flex-direction: column; }
  .sf-settings__team .el-button { width: 100%; }
}
</style>
