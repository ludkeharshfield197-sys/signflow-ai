<script setup>
import { CircleCheck, RefreshRight, Search, Warning } from '@element-plus/icons-vue'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import EmptyState from '@/components/ui/EmptyState.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getAdminRoles, getAdminSystem, getAdminUsers } from '@/services/admin'
import { getApiError } from '@/services/api'

const route = useRoute()
const loading = ref(true)
const errorMessage = ref('')
const users = ref({ items: [], total: 0, source: '' })
const roles = ref({ items: [], total: 0, source: '' })
const system = ref(null)
const query = ref('')

const section = computed(() => route.path.split('/').at(-1) || 'users')
const sectionTitle = computed(() => ({
  users: '用户管理',
  roles: '角色权限',
  system: '系统运行',
})[section.value] || '管理后台')

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium' }).format(new Date(value))
}

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    if (section.value === 'users') users.value = await getAdminUsers({ query: query.value })
    if (section.value === 'roles') roles.value = await getAdminRoles()
    if (section.value === 'system') system.value = await getAdminSystem()
  } catch (error) {
    errorMessage.value = getApiError(error, '管理数据读取失败，请稍后重试。')
  } finally {
    loading.value = false
  }
}

watch(() => route.path, load)
onMounted(load)
</script>

<template>
  <section class="sf-admin sf-page">
    <PageHeader
      :title="sectionTitle"
      description="管理区域只显示经过权限校验的数据库与运行状态；不会暴露密码、完整手机号或服务密钥。"
    >
      <template #actions>
        <el-button :loading="loading" @click="load">
          <el-icon><RefreshRight /></el-icon>
          刷新
        </el-button>
      </template>
    </PageHeader>

    <nav class="sf-admin__tabs sf-panel" aria-label="管理后台分区">
      <RouterLink to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/admin/roles">角色权限</RouterLink>
      <RouterLink to="/admin/system">系统运行</RouterLink>
    </nav>

    <div v-if="errorMessage" class="sf-admin__error" role="alert">
      <el-icon><Warning /></el-icon>
      <span>{{ errorMessage }}</span>
      <el-button text @click="load">重试</el-button>
    </div>

    <template v-else-if="section === 'users'">
      <div class="sf-admin__toolbar">
        <p>共 {{ users.total }} 个账户 · 来源：{{ users.source || '用户数据库' }}</p>
        <el-input
          v-model="query"
          clearable
          aria-label="搜索用户"
          placeholder="搜索用户名或邮箱"
          @keyup.enter="load"
          @clear="load"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
      <div v-if="loading" class="sf-admin__loading sf-panel">正在读取用户数据…</div>
      <EmptyState
        v-else-if="!users.items.length"
        class="sf-panel"
        title="没有匹配的账户"
        description="调整搜索条件后重试。"
      />
      <div v-else class="sf-admin__table sf-panel">
        <el-table :data="users.items" table-layout="fixed">
          <el-table-column label="账户" min-width="180">
            <template #default="{ row }">
              <div class="sf-admin__identity">
                <span>{{ row.username.slice(0, 1).toUpperCase() }}</span>
                <div><strong>{{ row.username }}</strong><small>ID {{ row.id }}</small></div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="脱敏邮箱" min-width="180" />
          <el-table-column label="角色" min-width="150">
            <template #default="{ row }">{{ row.roles.join('、') || '未分配' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <StatusBadge :label="row.statusLabel" :tone="row.status === 'active' ? 'success' : 'danger'" />
            </template>
          </el-table-column>
          <el-table-column label="最近登录" width="140">
            <template #default="{ row }">{{ formatDate(row.lastLoginAt) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <template v-else-if="section === 'roles'">
      <p class="sf-admin__source">共 {{ roles.total }} 个角色 · 来源：{{ roles.source || '权限数据库' }}</p>
      <div v-if="loading" class="sf-admin__loading sf-panel">正在读取角色数据…</div>
      <EmptyState v-else-if="!roles.items.length" class="sf-panel" title="尚未配置角色" />
      <div v-else class="sf-admin__roles">
        <article v-for="role in roles.items" :key="role.id" class="sf-panel">
          <header>
            <div><span>{{ role.code }}</span><h2>{{ role.name }}</h2></div>
            <strong>{{ role.userCount }}<small>成员</small></strong>
          </header>
          <p>{{ role.description }}</p>
          <footer>权限标识：<code>{{ role.code || '未设置' }}</code></footer>
        </article>
      </div>
    </template>

    <template v-else>
      <div v-if="loading" class="sf-admin__loading sf-panel">正在检查运行依赖…</div>
      <template v-else-if="system">
        <div class="sf-admin__system-summary sf-panel">
          <div>
            <StatusBadge
              :label="system.status === 'ready' ? '全部依赖就绪' : '部分依赖不可用'"
              :tone="system.status === 'ready' ? 'success' : 'warning'"
              pulse
            />
            <p>{{ system.service }} · {{ system.environment }} · 数据保留 {{ system.retentionDays }} 天</p>
          </div>
          <small>{{ system.source }}</small>
        </div>
        <div class="sf-admin__counts">
          <div class="sf-panel"><span>账户</span><strong>{{ system.counts.users }}</strong></div>
          <div class="sf-panel"><span>角色</span><strong>{{ system.counts.roles }}</strong></div>
          <div class="sf-panel"><span>模型</span><strong>{{ system.counts.models }}</strong></div>
          <div class="sf-panel"><span>任务</span><strong>{{ system.counts.tasks }}</strong></div>
        </div>
        <div class="sf-admin__checks">
          <article v-for="(check, name) in system.checks" :key="name" class="sf-panel">
            <el-icon :class="{ 'is-ok': check.ok }">
              <component :is="check.ok ? CircleCheck : Warning" />
            </el-icon>
            <div><h2>{{ name }}</h2><p>{{ check.ok ? `${check.latencyMs ?? 0} ms` : check.code }}</p></div>
            <StatusBadge :label="check.ok ? '就绪' : '不可用'" :tone="check.ok ? 'success' : 'danger'" />
          </article>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.sf-admin__tabs { display: flex; min-height: 56px; padding: 6px; align-items: center; gap: var(--sf-space-1); }
.sf-admin__tabs a { min-height: 42px; padding: 0 var(--sf-space-5); display: inline-flex; align-items: center; border-radius: var(--sf-radius-control); color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); font-weight: 650; }
.sf-admin__tabs a:hover { background: var(--sf-color-surface-subtle); color: var(--sf-color-text); }
.sf-admin__tabs a.router-link-active { background: var(--sf-color-primary-soft); color: var(--sf-color-primary); }
.sf-admin__error { display: flex; min-height: 52px; margin-top: var(--sf-space-4); padding: 0 var(--sf-space-4); align-items: center; gap: var(--sf-space-3); border: 1px solid #fecdca; border-radius: var(--sf-radius-control); background: var(--sf-color-danger-soft); color: var(--sf-color-danger); font-size: var(--sf-text-sm); }
.sf-admin__error span { flex: 1; }
.sf-admin__toolbar { display: flex; min-height: 72px; align-items: center; justify-content: space-between; gap: var(--sf-space-4); }
.sf-admin__toolbar p,
.sf-admin__source { margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-admin__toolbar .el-input { max-width: 300px; }
.sf-admin__loading { display: grid; min-height: 260px; place-items: center; color: var(--sf-color-text-muted); }
.sf-admin__table { overflow: hidden; }
.sf-admin__identity { display: flex; min-width: 0; align-items: center; gap: var(--sf-space-3); }
.sf-admin__identity > span { display: grid; width: 34px; height: 34px; flex: 0 0 34px; place-items: center; border-radius: 10px; background: var(--sf-color-primary-soft); color: var(--sf-color-primary); font-weight: 750; }
.sf-admin__identity > div { display: flex; min-width: 0; flex-direction: column; }
.sf-admin__identity strong { overflow: hidden; color: var(--sf-color-text); text-overflow: ellipsis; white-space: nowrap; }
.sf-admin__identity small { margin-top: 2px; color: var(--sf-color-text-disabled); font-size: 10px; }
.sf-admin__source { padding: var(--sf-space-5) var(--sf-space-2); }
.sf-admin__roles { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--sf-space-4); }
.sf-admin__roles article { overflow: hidden; }
.sf-admin__roles header { display: flex; padding: var(--sf-space-5); align-items: flex-start; justify-content: space-between; gap: var(--sf-space-4); }
.sf-admin__roles header span { color: var(--sf-color-primary); font-family: var(--sf-font-mono); font-size: 10px; text-transform: uppercase; }
.sf-admin__roles h2 { margin: 4px 0 0; font-size: var(--sf-text-lg); }
.sf-admin__roles header > strong { font-size: 28px; }
.sf-admin__roles header small { display: block; color: var(--sf-color-text-muted); font-size: 10px; font-weight: 500; text-align: right; }
.sf-admin__roles article > p { min-height: 58px; padding: 0 var(--sf-space-5); margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.6; }
.sf-admin__roles footer { padding: var(--sf-space-3) var(--sf-space-5); border-top: 1px solid var(--sf-color-border); background: var(--sf-color-surface-subtle); color: var(--sf-color-text-muted); font-size: 10px; }
.sf-admin__roles code { color: var(--sf-color-text-secondary); }
.sf-admin__system-summary { display: flex; margin-top: var(--sf-space-4); padding: var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-4); }
.sf-admin__system-summary p { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-admin__system-summary > small { color: var(--sf-color-text-disabled); }
.sf-admin__counts { display: grid; margin-top: var(--sf-space-4); grid-template-columns: repeat(4, 1fr); gap: var(--sf-space-3); }
.sf-admin__counts > div { display: flex; min-height: 96px; padding: var(--sf-space-5); flex-direction: column; justify-content: center; }
.sf-admin__counts span { color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-admin__counts strong { margin-top: var(--sf-space-2); font-size: 26px; }
.sf-admin__checks { display: grid; margin-top: var(--sf-space-4); grid-template-columns: 1fr 1fr; gap: var(--sf-space-3); }
.sf-admin__checks article { display: grid; min-height: 88px; padding: var(--sf-space-4); grid-template-columns: 36px minmax(0, 1fr) auto; align-items: center; gap: var(--sf-space-3); }
.sf-admin__checks article > .el-icon { color: var(--sf-color-danger); font-size: 24px; }
.sf-admin__checks article > .el-icon.is-ok { color: var(--sf-color-accent); }
.sf-admin__checks h2 { margin: 0; font-family: var(--sf-font-mono); font-size: var(--sf-text-sm); }
.sf-admin__checks p { margin: 4px 0 0; color: var(--sf-color-text-muted); font-size: 10px; }

@media (max-width: 900px) {
  .sf-admin__roles { grid-template-columns: 1fr 1fr; }
  .sf-admin__counts { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px) {
  .sf-admin__tabs { overflow-x: auto; }
  .sf-admin__tabs a { flex: 0 0 auto; }
  .sf-admin__toolbar,
  .sf-admin__system-summary { align-items: flex-start; flex-direction: column; }
  .sf-admin__toolbar .el-input { max-width: none; }
  .sf-admin__roles,
  .sf-admin__checks { grid-template-columns: 1fr; }
  .sf-admin__system-summary > small { overflow-wrap: anywhere; }
}
</style>
