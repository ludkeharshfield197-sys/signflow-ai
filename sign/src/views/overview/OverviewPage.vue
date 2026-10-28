<script setup>
import { Camera, Picture, Right, VideoCamera, VideoPlay } from '@element-plus/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import BaseChart from '@/components/charts/BaseChart.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getOverview } from '@/services/analytics'
import { useSession } from '@/services/session'

const router = useRouter()
const { state } = useSession()
const loading = ref(true)
const data = ref(null)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const sourceLabel = computed(() => (
  data.value?.dataKind === 'demo'
    ? 'SignFlow AI 本地演示数据'
    : data.value?.source || '识别任务接口'
))

const trendOption = computed(() => ({
  color: ['#0e9384'],
  tooltip: { trigger: 'axis' },
  grid: { left: 44, right: 24, top: 28, bottom: 36 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: data.value?.daily?.map((item) => item.date) || [],
    axisLine: { lineStyle: { color: '#e6eaf2' } },
    axisLabel: { color: '#667085', fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#eef1f6' } },
    axisLabel: { color: '#667085', fontSize: 11 },
  },
  series: [{
    name: '完成任务',
    type: 'line',
    smooth: 0.35,
    symbolSize: 7,
    data: data.value?.daily?.map((item) => item.tasks) || [],
    areaStyle: { color: 'rgba(14,147,132,0.10)' },
    lineStyle: { width: 3 },
  }],
}))

const quickModes = [
  { id: 'live', label: '实时摄像头', description: '现场低延迟识别', icon: Camera },
  { id: 'image', label: '图片', description: '上传单帧图片', icon: Picture },
  { id: 'video', label: '视频', description: '识别连续表达', icon: VideoCamera },
]

function formatTime(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

onMounted(async () => {
  data.value = await getOverview()
  loading.value = false
})
</script>

<template>
  <section class="sf-overview sf-page">
    <PageHeader
      :title="`${greeting}，${state.user?.displayName || state.user?.username || '欢迎回来'}`"
      description="这里汇总可行动的任务状态、最近结果与服务信息。"
    >
      <template #actions>
        <el-button type="primary" size="large" @click="router.push('/app/workbench')">
          <el-icon><VideoPlay /></el-icon>开始识别
        </el-button>
      </template>
    </PageHeader>

    <div v-if="data?.dataKind === 'demo'" class="sf-overview__notice">
      <StatusBadge label="演示数据" tone="processing" />
      <span>识别 API 尚未返回业务汇总，以下数字来自本地官方样例，并已单独标注来源。</span>
    </div>

    <div class="sf-overview__status sf-panel">
      <div>
        <strong>服务与任务概览</strong>
        <StatusBadge
          :label="data?.serviceStatus === 'healthy' ? '全部服务在线' : '演示适配器运行中'"
          :tone="data?.serviceStatus === 'healthy' ? 'success' : 'warning'"
          :pulse="data?.serviceStatus === 'healthy'"
        />
      </div>
      <p>服务健康状态来自 `/health/ready`；连接失败时不伪装为在线。</p>
    </div>

    <div class="sf-overview__metrics">
      <MetricCard
        label="今日完成"
        :value="loading ? '—' : data?.metrics?.completed ?? '—'"
        helper="已完成的识别任务"
        tone="positive"
        :source="sourceLabel"
      />
      <MetricCard
        label="今日成功率"
        :value="loading ? '—' : data?.metrics?.successRate != null ? `${data.metrics.successRate}%` : '—'"
        helper="完成状态任务 / 已结束任务"
        tone="positive"
        :source="sourceLabel"
      />
      <MetricCard
        label="平均处理时长"
        :value="loading ? '—' : data?.metrics?.averageLatencyMs != null ? `${(data.metrics.averageLatencyMs / 1000).toFixed(2)} 秒` : '—'"
        helper="仅统计成功任务"
        :source="sourceLabel"
      />
      <MetricCard
        label="待处理任务"
        :value="loading ? '—' : data?.metrics?.pending ?? '—'"
        helper="排队中与处理中"
        :source="sourceLabel"
      />
    </div>

    <div class="sf-overview__middle">
      <BaseChart
        title="近 7 天完成任务"
        description="按任务完成日期统计"
        :option="trendOption"
        :loading="loading"
        :empty="!loading && !data?.daily?.length"
        :source="sourceLabel"
        range="近 7 天"
        unit="任务数"
        :height="270"
      />

      <aside class="sf-overview__quick sf-panel">
        <header><h2>快速开始</h2><p>选择输入方式进入同一识别工作台</p></header>
        <button
          v-for="item in quickModes"
          :key="item.id"
          type="button"
          @click="router.push(`/app/workbench?mode=${item.id}`)"
        >
          <span><el-icon :size="21"><component :is="item.icon" /></el-icon></span>
          <div><strong>{{ item.label }}</strong><small>{{ item.description }}</small></div>
          <el-icon><Right /></el-icon>
        </button>
      </aside>
    </div>

    <section class="sf-overview__recent sf-panel">
      <header>
        <div><h2>最近识别活动</h2><p>从这里继续查看结果、模型和输入信息</p></div>
        <RouterLink to="/app/results">查看全部 <el-icon><Right /></el-icon></RouterLink>
      </header>
      <div class="sf-overview__table" role="table" aria-label="最近识别活动">
        <div class="sf-overview__row sf-overview__row--head" role="row">
          <span role="columnheader">任务</span><span role="columnheader">输入类型</span>
          <span role="columnheader">识别结果</span><span role="columnheader">置信度</span>
          <span role="columnheader">耗时</span><span role="columnheader">状态</span>
          <span role="columnheader">时间</span><span />
        </div>
        <RouterLink
          v-for="item in data?.recentResults || []"
          :key="item.id"
          class="sf-overview__row"
          :to="`/app/results/${item.id}`"
        >
          <span data-label="任务">{{ item.sourceName }}</span>
          <span data-label="输入类型">{{ { live: '实时', image: '图片', video: '视频' }[item.mode] }}</span>
          <strong data-label="识别结果">{{ item.sentence }}</strong>
          <span data-label="置信度">{{ (item.confidence * 100).toFixed(1) }}%</span>
          <span data-label="耗时">{{ (item.durationMs / 1000).toFixed(2) }} 秒</span>
          <span data-label="状态"><StatusBadge label="已完成" tone="success" /></span>
          <span data-label="时间">{{ formatTime(item.createdAt) }}</span>
          <el-icon><Right /></el-icon>
        </RouterLink>
      </div>
    </section>
  </section>
</template>

<style scoped>
.sf-overview__notice { display: flex; min-height: 48px; padding: var(--sf-space-3) var(--sf-space-4); margin-bottom: var(--sf-space-5); align-items: center; gap: var(--sf-space-3); border: 1px solid #c9c9f4; border-radius: var(--sf-radius-control); background: var(--sf-color-primary-soft); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-overview__status { display: flex; min-height: 84px; padding: var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-6); }
.sf-overview__status > div { display: flex; align-items: center; flex-wrap: wrap; gap: var(--sf-space-3); }
.sf-overview__status strong { font-size: var(--sf-text-sm); }
.sf-overview__status p { max-width: 480px; margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); text-align: right; }
.sf-overview__metrics { display: grid; margin-top: var(--sf-space-4); grid-template-columns: repeat(4, 1fr); gap: var(--sf-space-4); }
.sf-overview__middle { display: grid; margin-top: var(--sf-space-4); grid-template-columns: minmax(0, 1.65fr) minmax(280px, 0.72fr); gap: var(--sf-space-4); }
.sf-overview__quick { padding: var(--sf-space-5); }
.sf-overview__quick header { margin-bottom: var(--sf-space-3); }
.sf-overview__quick h2,
.sf-overview__recent h2 { margin: 0; font-size: var(--sf-text-sm); }
.sf-overview__quick header p,
.sf-overview__recent header p { margin: var(--sf-space-1) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-overview__quick > button { display: grid; width: 100%; min-height: 68px; padding: var(--sf-space-3); align-items: center; grid-template-columns: 42px 1fr auto; gap: var(--sf-space-3); border: 0; border-bottom: 1px solid var(--sf-color-border); background: transparent; color: var(--sf-color-text-secondary); cursor: pointer; text-align: left; }
.sf-overview__quick > button:last-child { border-bottom: 0; }
.sf-overview__quick > button:hover { background: var(--sf-color-surface-subtle); }
.sf-overview__quick > button > span { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 11px; background: var(--sf-color-primary-soft); color: var(--sf-color-primary); }
.sf-overview__quick button div { display: flex; min-width: 0; flex-direction: column; }
.sf-overview__quick button strong { font-size: var(--sf-text-xs); }
.sf-overview__quick button small { margin-top: 3px; color: var(--sf-color-text-muted); font-size: 10px; }
.sf-overview__recent { margin-top: var(--sf-space-4); overflow: hidden; }
.sf-overview__recent > header { display: flex; min-height: 76px; padding: var(--sf-space-4) var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); }
.sf-overview__recent header a { display: flex; align-items: center; gap: 5px; color: var(--sf-color-primary); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-overview__row { display: grid; min-height: 58px; padding: 0 var(--sf-space-5); align-items: center; grid-template-columns: minmax(150px, 1fr) 80px minmax(180px, 1.1fr) 86px 90px 90px 120px 20px; gap: var(--sf-space-3); border-bottom: 1px solid var(--sf-color-border); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-overview__row:last-child { border-bottom: 0; }
.sf-overview__row:not(.sf-overview__row--head):hover { background: var(--sf-color-surface-subtle); }
.sf-overview__row--head { min-height: 42px; background: var(--sf-color-surface-subtle); color: var(--sf-color-text-muted); font-size: 10px; font-weight: 700; }
.sf-overview__row > span,
.sf-overview__row > strong { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

@media (max-width: 1199px) {
  .sf-overview__metrics { grid-template-columns: 1fr 1fr; }
  .sf-overview__middle { grid-template-columns: 1fr; }
  .sf-overview__quick { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--sf-space-2); }
  .sf-overview__quick header { grid-column: 1 / -1; }
  .sf-overview__quick > button { border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-control); }
  .sf-overview__row { grid-template-columns: minmax(130px, 1fr) 70px minmax(160px, 1fr) 80px 80px 100px 20px; }
  .sf-overview__row > :nth-child(5),
  .sf-overview__row--head > :nth-child(5) { display: none; }
}

@media (max-width: 767px) {
  .sf-overview__notice,
  .sf-overview__status { align-items: flex-start; flex-direction: column; }
  .sf-overview__status p { text-align: left; }
  .sf-overview__metrics { grid-template-columns: 1fr 1fr; }
  .sf-overview__quick { grid-template-columns: 1fr; }
  .sf-overview__row--head { display: none; }
  .sf-overview__row { position: relative; display: grid; min-height: 0; padding: var(--sf-space-4); grid-template-columns: 1fr auto; gap: var(--sf-space-2) var(--sf-space-4); }
  .sf-overview__row > span,
  .sf-overview__row > strong { display: block !important; grid-column: 1; }
  .sf-overview__row > span::before,
  .sf-overview__row > strong::before { content: attr(data-label) " · "; color: var(--sf-color-text-muted); font-weight: 500; }
  .sf-overview__row > .el-icon { position: absolute; right: var(--sf-space-4); top: 50%; transform: translateY(-50%); }
}

@media (max-width: 480px) {
  .sf-overview__metrics { grid-template-columns: 1fr; }
}
</style>
