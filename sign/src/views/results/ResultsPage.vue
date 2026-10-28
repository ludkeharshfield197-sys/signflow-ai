<script setup>
import { Download, Search, View } from '@element-plus/icons-vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import EmptyState from '@/components/ui/EmptyState.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { exportResultFile, getResults } from '@/services/results'

const router = useRouter()
const loading = ref(true)
const rows = ref([])
const total = ref(0)
const source = ref('')
const filters = reactive({
  query: '',
  mode: 'all',
  status: 'all',
  page: 1,
  pageSize: 10,
})

let searchTimer

const sourceText = computed(() => (
  source.value === 'api' ? '识别结果接口' : '本地保存结果与官方演示样例'
))

async function load() {
  loading.value = true
  const response = await getResults(filters)
  rows.value = response.items
  total.value = response.total
  source.value = response.source
  loading.value = false
}

function scheduleLoad() {
  clearTimeout(searchTimer)
  filters.page = 1
  searchTimer = setTimeout(load, 250)
}

function formatDate(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

watch(() => [filters.mode, filters.status, filters.page, filters.pageSize], load)
onMounted(load)
</script>

<template>
  <section class="sf-results sf-page">
    <PageHeader title="结果中心" description="集中复查图片、视频与实时任务，追溯输入、模型、参数和导出记录。">
      <template #actions>
        <el-button type="primary" @click="router.push('/app/workbench')">新建识别</el-button>
      </template>
    </PageHeader>

    <div v-if="source === 'demo'" class="sf-results__notice">
      <StatusBadge label="演示数据" tone="processing" />
      <span>当前列表包含本地保存结果和官方样例，真实服务数据接入后会自动替换。</span>
    </div>

    <div class="sf-results__toolbar sf-panel">
      <el-input
        v-model="filters.query"
        clearable
        placeholder="搜索任务、句子或结果 ID"
        aria-label="搜索结果"
        @input="scheduleLoad"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filters.mode" data-testid="mode-filter" aria-label="输入类型筛选">
        <el-option label="全部输入" value="all" />
        <el-option label="实时" value="live" />
        <el-option label="图片" value="image" />
        <el-option label="视频" value="video" />
      </el-select>
      <el-select v-model="filters.status" aria-label="任务状态筛选">
        <el-option label="全部状态" value="all" />
        <el-option label="已完成" value="succeeded" />
        <el-option label="处理中" value="running" />
        <el-option label="失败" value="failed" />
      </el-select>
      <span>数据来源：{{ sourceText }}</span>
    </div>

    <section class="sf-results__table sf-panel" :aria-busy="loading">
      <div v-if="loading" class="sf-results__loading" role="status">正在加载结果…</div>
      <EmptyState
        v-else-if="!rows.length"
        title="没有匹配的识别结果"
        description="调整筛选条件，或开始一次新的识别任务。"
        action-label="开始识别"
        @action="router.push('/app/workbench')"
      />
      <template v-else>
        <div class="sf-results__row sf-results__row--head" role="row">
          <span>任务与结果</span><span>输入</span><span>置信度</span><span>模型版本</span>
          <span>耗时</span><span>状态</span><span>创建时间</span><span>操作</span>
        </div>
        <article v-for="item in rows" :key="item.id" class="sf-results__row">
          <div class="sf-results__primary">
            <strong>{{ item.sentence || '暂无生成句子' }}</strong>
            <small>{{ item.sourceName }} · {{ item.id }}</small>
          </div>
          <span data-label="输入">{{ { live: '实时', image: '图片', video: '视频' }[item.mode] }}</span>
          <span data-label="置信度">{{ item.confidence != null ? `${(item.confidence * 100).toFixed(1)}%` : '—' }}</span>
          <span data-label="模型">{{ item.model?.name }} {{ item.model?.version }}</span>
          <span data-label="耗时">{{ item.durationMs != null ? `${(item.durationMs / 1000).toFixed(2)} 秒` : '—' }}</span>
          <span data-label="状态">
            <StatusBadge
              :label="item.status === 'succeeded' ? '已完成' : item.status === 'failed' ? '失败' : '处理中'"
              :tone="item.status === 'succeeded' ? 'success' : item.status === 'failed' ? 'danger' : 'processing'"
            />
          </span>
          <span data-label="时间">{{ formatDate(item.createdAt) }}</span>
          <div class="sf-results__actions">
            <button type="button" aria-label="查看结果详情" @click="router.push(`/app/results/${item.id}`)">
              <el-icon><View /></el-icon>
            </button>
            <button type="button" aria-label="导出结果" @click="exportResultFile(item)">
              <el-icon><Download /></el-icon>
            </button>
          </div>
        </article>
        <footer class="sf-results__pagination">
          <span>共 {{ total }} 条</span>
          <el-pagination
            v-model:current-page="filters.page"
            v-model:page-size="filters.pageSize"
            background
            layout="prev, pager, next"
            :total="total"
          />
        </footer>
      </template>
    </section>
  </section>
</template>

<style scoped>
.sf-results__notice { display: flex; min-height: 48px; padding: var(--sf-space-3) var(--sf-space-4); margin-bottom: var(--sf-space-4); align-items: center; gap: var(--sf-space-3); border: 1px solid #c9c9f4; border-radius: var(--sf-radius-control); background: var(--sf-color-primary-soft); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-results__toolbar { display: grid; min-height: 76px; padding: var(--sf-space-4); align-items: center; grid-template-columns: minmax(240px, 1fr) 150px 150px auto; gap: var(--sf-space-3); }
.sf-results__toolbar > span { color: var(--sf-color-text-muted); font-size: 10px; text-align: right; }
.sf-results__table { margin-top: var(--sf-space-4); overflow: hidden; }
.sf-results__loading { display: grid; min-height: 320px; place-items: center; color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); }
.sf-results__row { display: grid; min-height: 72px; padding: 0 var(--sf-space-5); align-items: center; grid-template-columns: minmax(220px, 1.35fr) 66px 80px 130px 80px 92px 150px 82px; gap: var(--sf-space-3); border-bottom: 1px solid var(--sf-color-border); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-results__row--head { min-height: 44px; background: var(--sf-color-surface-subtle); color: var(--sf-color-text-muted); font-size: 10px; font-weight: 700; }
.sf-results__row:not(.sf-results__row--head):hover { background: var(--sf-color-surface-subtle); }
.sf-results__primary { display: flex; min-width: 0; flex-direction: column; }
.sf-results__primary strong { overflow: hidden; font-size: var(--sf-text-sm); text-overflow: ellipsis; white-space: nowrap; }
.sf-results__primary small { overflow: hidden; margin-top: 4px; color: var(--sf-color-text-muted); font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.sf-results__row > span { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sf-results__actions { display: flex; gap: var(--sf-space-1); }
.sf-results__actions button { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-sm); background: white; color: var(--sf-color-text-muted); cursor: pointer; }
.sf-results__actions button:hover { border-color: var(--sf-color-primary); color: var(--sf-color-primary); }
.sf-results__pagination { display: flex; min-height: 68px; padding: 0 var(--sf-space-5); align-items: center; justify-content: space-between; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }

@media (max-width: 1199px) {
  .sf-results__toolbar { grid-template-columns: 1fr 140px 140px; }
  .sf-results__toolbar > span { grid-column: 1 / -1; text-align: left; }
  .sf-results__row { grid-template-columns: minmax(180px, 1.4fr) 60px 76px 110px 90px 128px 76px; }
  .sf-results__row > :nth-child(5),
  .sf-results__row--head > :nth-child(5) { display: none; }
}

@media (max-width: 767px) {
  .sf-results__notice { align-items: flex-start; }
  .sf-results__toolbar { grid-template-columns: 1fr 1fr; }
  .sf-results__toolbar .el-input { grid-column: 1 / -1; }
  .sf-results__row--head { display: none; }
  .sf-results__row { position: relative; display: grid; min-height: 0; padding: var(--sf-space-4); grid-template-columns: 1fr 84px; gap: var(--sf-space-2) var(--sf-space-3); }
  .sf-results__primary { grid-column: 1 / -1; padding-right: var(--sf-space-8); }
  .sf-results__row > span { display: block !important; grid-column: 1; }
  .sf-results__row > span::before { content: attr(data-label) " · "; color: var(--sf-color-text-muted); }
  .sf-results__actions { position: absolute; right: var(--sf-space-4); top: var(--sf-space-4); }
  .sf-results__pagination { align-items: flex-start; flex-direction: column; justify-content: center; gap: var(--sf-space-2); }
}
</style>
