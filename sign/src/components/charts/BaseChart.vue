<script setup>
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  AriaComponent,
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import EmptyState from '@/components/ui/EmptyState.vue'

echarts.use([
  AriaComponent,
  BarChart,
  CanvasRenderer,
  DatasetComponent,
  GridComponent,
  LegendComponent,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
])

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  option: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  empty: { type: Boolean, default: false },
  source: { type: String, default: '' },
  range: { type: String, default: '' },
  unit: { type: String, default: '' },
  height: { type: Number, default: 300 },
})

const chartRoot = ref()
let chart
let observer

const metadata = computed(() => [
  props.range && `范围：${props.range}`,
  props.unit && `单位：${props.unit}`,
  props.source ? `来源：${props.source}` : '来源：未配置',
].filter(Boolean))

function render() {
  if (!chart || props.empty || props.loading) return
  chart.setOption(
    {
      animationDuration: 500,
      textStyle: {
        fontFamily: 'Inter, "PingFang SC", "Microsoft YaHei", sans-serif',
        color: '#667085',
      },
      aria: {
        enabled: true,
        description: `${props.title}。${props.description}`,
      },
      ...props.option,
    },
    { notMerge: true },
  )
}

function initializeChart() {
  if (chart || !chartRoot.value || props.empty || props.loading) return
  chart = echarts.init(chartRoot.value, null, { renderer: 'canvas' })
  observer = new ResizeObserver(() => chart?.resize())
  observer.observe(chartRoot.value)
}

function disposeChart() {
  observer?.disconnect()
  observer = undefined
  chart?.dispose()
  chart = undefined
}

onMounted(() => {
  initializeChart()
  render()
})

watch(
  () => props.option,
  () => {
    initializeChart()
    render()
  },
  { deep: true, flush: 'post' },
)
watch(
  () => [props.empty, props.loading],
  ([empty, loading]) => {
    if (empty || loading) {
      disposeChart()
      return
    }
    initializeChart()
    render()
  },
  { flush: 'post' },
)

onBeforeUnmount(disposeChart)
</script>

<template>
  <article class="sf-chart sf-panel">
    <header class="sf-chart__header">
      <div>
        <h3>{{ title }}</h3>
        <p v-if="description">{{ description }}</p>
      </div>
      <slot name="actions" />
    </header>
    <div v-if="loading" class="sf-chart__loading" role="status">
      <span /><span /><span />
      <p>正在加载图表数据</p>
    </div>
    <EmptyState
      v-else-if="empty"
      class="sf-chart__empty"
      title="暂无可绘制数据"
      description="调整时间范围，或在完成识别任务后再查看。"
    />
    <div
      v-else
      ref="chartRoot"
      class="sf-chart__canvas"
      :style="{ height: `${height}px` }"
      role="img"
      :aria-label="`${title}。${description}`"
    />
    <footer class="sf-chart__meta">
      <span v-for="item in metadata" :key="item" :class="{ 'is-missing': item === '来源：未配置' }">
        {{ item }}
      </span>
    </footer>
  </article>
</template>

<style scoped>
.sf-chart { min-width: 0; overflow: hidden; }
.sf-chart__header { display: flex; min-height: 72px; padding: var(--sf-space-4) var(--sf-space-5); align-items: flex-start; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); }
.sf-chart__header h3 { margin: 0; font-size: var(--sf-text-sm); font-weight: 750; }
.sf-chart__header p { margin: var(--sf-space-1) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-chart__canvas { width: 100%; min-height: 220px; }
.sf-chart__meta { display: flex; min-height: 42px; padding: var(--sf-space-2) var(--sf-space-5); align-items: center; flex-wrap: wrap; gap: var(--sf-space-4); border-top: 1px solid var(--sf-color-border); color: var(--sf-color-text-disabled); font-size: 10px; }
.sf-chart__meta .is-missing { color: var(--sf-color-warning); }
.sf-chart__loading { display: flex; min-height: 260px; align-items: center; justify-content: center; gap: 6px; color: var(--sf-color-text-muted); }
.sf-chart__loading span { width: 8px; height: 8px; border-radius: 50%; background: var(--sf-color-primary); animation: sf-chart-loading 1s ease-in-out infinite; }
.sf-chart__loading span:nth-child(2) { animation-delay: 120ms; }
.sf-chart__loading span:nth-child(3) { animation-delay: 240ms; }
.sf-chart__loading p { margin: 0 0 0 var(--sf-space-2); font-size: var(--sf-text-xs); }
.sf-chart__empty { min-height: 260px; }
@keyframes sf-chart-loading { 0%, 100% { opacity: 0.3; transform: translateY(0); } 50% { opacity: 1; transform: translateY(-3px); } }
@media (prefers-reduced-motion: reduce) { .sf-chart__loading span { animation: none; } }
</style>
