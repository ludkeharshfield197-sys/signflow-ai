<script setup>
import { computed, onMounted, ref, watch } from 'vue'

import BaseChart from '@/components/charts/BaseChart.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getAnalytics } from '@/services/analytics'

const range = ref('7d')
const loading = ref(true)
const data = ref(null)

const source = computed(() => data.value?.source || '')
const totalTasks = computed(() => data.value?.metrics?.tasks ?? data.value?.daily?.reduce((sum, item) => sum + item.tasks, 0) ?? 0)
const averageLatency = computed(() => {
  if (data.value?.metrics?.averageLatencyMs != null) return data.value.metrics.averageLatencyMs
  const values = data.value?.daily?.map((item) => item.latencyMs) || []
  if (!values.length) return null
  return values.reduce((sum, value) => sum + value, 0) / values.length
})
const averageSuccess = computed(() => {
  if (data.value?.metrics?.successRate != null) return data.value.metrics.successRate
  const values = data.value?.daily?.map((item) => item.successRate) || []
  if (!values.length) return null
  return values.reduce((sum, value) => sum + value, 0) / values.length
})

const taskOption = computed(() => ({
  color: ['#5b5bd6'],
  tooltip: { trigger: 'axis' },
  grid: { left: 46, right: 24, top: 28, bottom: 36 },
  xAxis: { type: 'category', data: data.value?.daily?.map((item) => item.date) || [], axisLine: { lineStyle: { color: '#e6eaf2' } }, axisLabel: { color: '#667085' } },
  yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#eef1f6' } }, axisLabel: { color: '#667085' } },
  series: [{ name: '识别任务', type: 'bar', barMaxWidth: 34, data: data.value?.daily?.map((item) => item.tasks) || [], itemStyle: { borderRadius: [5, 5, 0, 0] } }],
}))

const latencyOption = computed(() => ({
  color: ['#0e9384'],
  tooltip: { trigger: 'axis', valueFormatter: (value) => `${value} ms` },
  grid: { left: 54, right: 24, top: 28, bottom: 36 },
  xAxis: { type: 'category', boundaryGap: false, data: data.value?.daily?.map((item) => item.date) || [], axisLine: { lineStyle: { color: '#e6eaf2' } }, axisLabel: { color: '#667085' } },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: '#eef1f6' } }, axisLabel: { color: '#667085' } },
  series: [{ name: '处理时长', type: 'line', smooth: 0.3, symbolSize: 7, data: data.value?.daily?.map((item) => item.latencyMs) || [], lineStyle: { width: 3 }, areaStyle: { color: 'rgba(14,147,132,0.10)' } }],
}))

const modeOption = computed(() => ({
  color: ['#5b5bd6', '#0e9384', '#98a2b3'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 4, textStyle: { color: '#667085', fontSize: 11 } },
  series: [{
    name: '输入类型',
    type: 'pie',
    radius: ['44%', '66%'],
    center: ['50%', '45%'],
    avoidLabelOverlap: true,
    label: { formatter: '{b} {d}%', color: '#344054', fontSize: 11 },
    data: data.value?.modes || [],
  }],
}))

async function load() {
  loading.value = true
  data.value = await getAnalytics(range.value)
  loading.value = false
}

watch(range, load)
onMounted(load)
</script>

<template>
  <section class="sf-analytics sf-page">
    <PageHeader title="数据洞察" description="使用可解释的时间范围、单位与数据来源，观察任务量、延迟和输入分布。">
      <template #actions>
        <el-select v-model="range" aria-label="分析时间范围" style="width: 140px">
          <el-option label="近 7 天" value="7d" />
          <el-option label="近 30 天" value="30d" />
          <el-option label="近 90 天" value="90d" />
        </el-select>
      </template>
    </PageHeader>

    <div v-if="data?.dataKind === 'demo'" class="sf-analytics__notice">
      <StatusBadge label="演示数据" tone="processing" />
      <span>以下图表来自官方样例任务，仅用于展示分析体验，不代表真实业务规模。</span>
    </div>

    <div class="sf-analytics__metrics">
      <MetricCard label="识别任务" :value="loading ? '—' : totalTasks" helper="当前时间范围内" :source="source" />
      <MetricCard label="成功率" :value="loading || averageSuccess == null ? '—' : `${averageSuccess.toFixed(1)}%`" helper="成功任务 / 已结束任务" tone="positive" :source="source" />
      <MetricCard label="平均处理时长" :value="loading || averageLatency == null ? '—' : `${(averageLatency / 1000).toFixed(2)} 秒`" helper="成功任务平均值" :source="source" />
      <MetricCard label="数据保留" value="30 天" helper="当前部署默认策略" :source="'部署配置'" />
    </div>

    <div class="sf-analytics__charts">
      <BaseChart
        title="每日识别任务"
        description="按创建日期统计全部输入类型"
        :option="taskOption"
        :loading="loading"
        :empty="!loading && !data?.daily?.length"
        :source="source"
        :range="data?.range || '当前范围'"
        unit="任务数"
      />
      <BaseChart
        title="平均处理时长"
        description="仅统计成功完成的任务"
        :option="latencyOption"
        :loading="loading"
        :empty="!loading && !data?.daily?.length"
        :source="source"
        :range="data?.range || '当前范围'"
        unit="毫秒"
      />
      <BaseChart
        title="输入类型分布"
        description="图片、视频与实时任务占比"
        :option="modeOption"
        :loading="loading"
        :empty="!loading && !data?.modes?.length"
        :source="source"
        :range="data?.range || '当前范围'"
        unit="任务占比"
      />
      <section class="sf-analytics__method sf-panel">
        <h2>指标口径</h2>
        <dl>
          <div><dt>识别任务</dt><dd>在时间范围内创建且未删除的任务。</dd></div>
          <div><dt>成功率</dt><dd>成功完成任务 ÷ 已结束任务；排队和处理中任务不进入分母。</dd></div>
          <div><dt>处理时长</dt><dd>从任务开始处理到结果生成，不包含用户上传耗时。</dd></div>
          <div><dt>更新时间</dt><dd>{{ data?.updatedAt ? new Date(data.updatedAt).toLocaleString('zh-CN') : '—' }}</dd></div>
        </dl>
      </section>
    </div>
  </section>
</template>

<style scoped>
.sf-analytics__notice { display: flex; min-height: 48px; padding: var(--sf-space-3) var(--sf-space-4); margin-bottom: var(--sf-space-4); align-items: center; gap: var(--sf-space-3); border: 1px solid #c9c9f4; border-radius: var(--sf-radius-control); background: var(--sf-color-primary-soft); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-analytics__metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sf-space-4); }
.sf-analytics__charts { display: grid; margin-top: var(--sf-space-4); grid-template-columns: 1fr 1fr; gap: var(--sf-space-4); }
.sf-analytics__method { padding: var(--sf-space-5); }
.sf-analytics__method h2 { margin: 0; font-size: var(--sf-text-sm); }
.sf-analytics__method dl { margin: var(--sf-space-4) 0 0; }
.sf-analytics__method dl div { display: grid; padding: var(--sf-space-3) 0; grid-template-columns: 110px 1fr; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); font-size: var(--sf-text-xs); }
.sf-analytics__method dl div:last-child { border-bottom: 0; }
.sf-analytics__method dt { color: var(--sf-color-text-secondary); font-weight: 700; }
.sf-analytics__method dd { margin: 0; color: var(--sf-color-text-muted); line-height: 1.6; }
@media (max-width: 1100px) {
  .sf-analytics__metrics { grid-template-columns: 1fr 1fr; }
  .sf-analytics__charts { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .sf-analytics__notice { align-items: flex-start; }
  .sf-analytics__metrics { grid-template-columns: 1fr; }
  .sf-analytics__method dl div { grid-template-columns: 1fr; gap: var(--sf-space-1); }
}
</style>
