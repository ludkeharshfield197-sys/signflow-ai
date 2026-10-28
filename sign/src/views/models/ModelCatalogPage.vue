<script setup>
import { Box, Clock, DataAnalysis, Location, RefreshRight } from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'

import EmptyState from '@/components/ui/EmptyState.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getModels } from '@/services/models'
import { useSession } from '@/services/session'

const { isAdmin } = useSession()
const loading = ref(true)
const models = ref([])
const source = ref('')

function formatTime(value) {
  if (!value) return '尚未使用'
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatPercent(value) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? `${(numeric * 100).toFixed(1)}%` : '—'
}

function formatMeasure(value, unit) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? `${numeric.toFixed(2)} ${unit}` : '—'
}

async function load() {
  loading.value = true
  const response = await getModels()
  models.value = response.items
  source.value = response.source
  loading.value = false
}

onMounted(load)
</script>

<template>
  <section class="sf-models sf-page">
    <PageHeader title="模型中心" description="查看当前部署版本、评测来源、运行状态与部署位置；模型治理操作仅对管理员开放。">
      <template #actions>
        <el-button :loading="loading" @click="load"><el-icon><RefreshRight /></el-icon>刷新状态</el-button>
        <el-button v-if="isAdmin" type="primary">管理部署</el-button>
      </template>
    </PageHeader>

    <div v-if="source === 'demo'" class="sf-models__notice">
      <StatusBadge label="演示配置" tone="processing" />
      <span>尚未连接模型治理接口，不会展示臆测的准确率、类别数或文件大小。</span>
    </div>

    <div class="sf-models__summary">
      <span><strong>{{ models.length }}</strong> 个可见版本</span>
      <span>数据来源：{{ source === 'api' ? '模型治理接口' : '本地演示适配器' }}</span>
      <span>上传、启停与回滚：{{ isAdmin ? '管理员可用' : '仅管理员' }}</span>
    </div>

    <div v-if="loading" class="sf-models__loading sf-panel">正在读取模型目录…</div>
    <EmptyState
      v-else-if="!models.length"
      class="sf-panel"
      title="尚未部署模型"
      description="由管理员在部署环境中注册模型版本后，这里会显示治理信息。"
    />
    <div v-else class="sf-models__list">
      <article v-for="model in models" :key="model.id" class="sf-model sf-panel">
        <header class="sf-model__header">
          <div class="sf-model__identity">
            <span><el-icon :size="24"><Box /></el-icon></span>
            <div>
              <h2>{{ model.name }}</h2>
              <p>版本 {{ model.version }} · {{ model.id }}</p>
            </div>
          </div>
          <StatusBadge
            :label="model.statusLabel || (model.status === 'active' ? '运行中' : '未启用')"
            :tone="model.status === 'active' ? 'success' : model.status === 'demo' ? 'processing' : 'neutral'"
          />
        </header>

        <p class="sf-model__description">{{ model.description }}</p>

        <div class="sf-model__facts">
          <div><el-icon><Location /></el-icon><span>适用语言<strong>{{ model.language || '未配置' }}</strong></span></div>
          <div><el-icon><DataAnalysis /></el-icon><span>类别数<strong>{{ model.classes || '未配置' }}</strong></span></div>
          <div><el-icon><Box /></el-icon><span>文件大小<strong>{{ model.fileSize || '未配置' }}</strong></span></div>
          <div><el-icon><Clock /></el-icon><span>最近使用<strong>{{ formatTime(model.lastUsedAt) }}</strong></span></div>
          <div><el-icon><Location /></el-icon><span>部署位置<strong>{{ model.deployment || '未配置' }}</strong></span></div>
        </div>

        <section class="sf-model__metric">
          <div>
            <span>{{ model.metric?.name || '模型指标' }}</span>
            <strong>{{ model.metric?.value != null ? model.metric.value : '—' }}</strong>
          </div>
          <dl>
            <div><dt>数据集</dt><dd>{{ model.metric?.dataset || '未配置' }}</dd></div>
            <div><dt>样本量</dt><dd>{{ model.metric?.sampleCount || '未配置' }}</dd></div>
            <div><dt>评测日期</dt><dd>{{ model.metric?.evaluatedAt || '未配置' }}</dd></div>
            <div><dt>数据来源</dt><dd :class="{ 'is-missing': !model.metric?.source }">{{ model.metric?.source || '数据来源未配置' }}</dd></div>
          </dl>
        </section>

        <section v-if="model.evaluation?.status === 'evaluated'" class="sf-model__evidence" aria-label="完整模型评测卡">
          <div class="sf-model__evidence-header">
            <div>
              <span class="sf-model__eyebrow">可复核评测</span>
              <h3>完整模型评测卡</h3>
            </div>
            <StatusBadge label="已实测" tone="success" />
          </div>

          <dl class="sf-model__scores">
            <div><dt>Precision</dt><dd>{{ formatPercent(model.evaluation.metrics?.precision) }}</dd></div>
            <div><dt>Recall</dt><dd>{{ formatPercent(model.evaluation.metrics?.recall) }}</dd></div>
            <div><dt>mAP50</dt><dd>{{ formatPercent(model.evaluation.metrics?.map50) }}</dd></div>
            <div><dt>mAP50-95</dt><dd>{{ formatPercent(model.evaluation.metrics?.map5095) }}</dd></div>
          </dl>

          <div class="sf-model__evidence-grid">
            <dl>
              <div><dt>评测数据集</dt><dd>{{ model.evaluation.dataset?.name || '未配置' }}</dd></div>
              <div><dt>测试样本量</dt><dd>{{ model.evaluation.dataset?.sampleCount ?? '未配置' }}</dd></div>
              <div><dt>数据集说明</dt><dd>{{ model.evaluation.dataset?.independence || '未配置' }}</dd></div>
            </dl>
            <dl>
              <div><dt>单张平均延迟</dt><dd>{{ formatMeasure(model.evaluation.performance?.averageImageLatencyMs, 'ms') }}</dd></div>
              <div><dt>视频处理速度</dt><dd>{{ formatMeasure(model.evaluation.performance?.videoFps, 'FPS') }}</dd></div>
              <div><dt>测试硬件</dt><dd>{{ model.evaluation.performance?.hardware || '未配置' }}</dd></div>
            </dl>
          </div>

          <div class="sf-model__limitations">
            <h4>已知能力边界</h4>
            <ul>
              <li v-for="item in model.evaluation.limitations || []" :key="item">{{ item }}</li>
            </ul>
          </div>
        </section>

        <footer class="sf-model__footer">
          <p>只有同时提供数据集、样本量、日期和来源的指标才会作为公开证据。</p>
          <div v-if="isAdmin">
            <el-button size="small" disabled>回滚</el-button>
            <el-button size="small" disabled>停用</el-button>
          </div>
        </footer>
      </article>
    </div>
  </section>
</template>

<style scoped>
.sf-models__notice { display: flex; min-height: 48px; padding: var(--sf-space-3) var(--sf-space-4); align-items: center; gap: var(--sf-space-3); border: 1px solid #c9c9f4; border-radius: var(--sf-radius-control); background: var(--sf-color-primary-soft); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-models__summary { display: flex; min-height: 54px; padding: 0 var(--sf-space-2); align-items: center; flex-wrap: wrap; gap: var(--sf-space-8); color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-models__summary strong { color: var(--sf-color-text); font-size: var(--sf-text-lg); }
.sf-models__loading { display: grid; min-height: 300px; place-items: center; color: var(--sf-color-text-muted); }
.sf-models__list { display: grid; gap: var(--sf-space-4); }
.sf-model { overflow: hidden; }
.sf-model__header { display: flex; min-height: 84px; padding: var(--sf-space-4) var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); }
.sf-model__identity { display: flex; min-width: 0; align-items: center; gap: var(--sf-space-3); }
.sf-model__identity > span { display: grid; width: 48px; height: 48px; flex: 0 0 48px; place-items: center; border-radius: 13px; background: var(--sf-color-primary-soft); color: var(--sf-color-primary); }
.sf-model__identity h2 { margin: 0; font-size: var(--sf-text-md); }
.sf-model__identity p { margin: 3px 0 0; color: var(--sf-color-text-muted); font-family: var(--sf-font-mono); font-size: 10px; }
.sf-model__description { padding: var(--sf-space-4) var(--sf-space-5) 0; margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-model__facts { display: grid; padding: var(--sf-space-5); grid-template-columns: repeat(5, 1fr); gap: var(--sf-space-3); }
.sf-model__facts > div { display: flex; min-width: 0; padding: var(--sf-space-3); align-items: center; gap: var(--sf-space-3); border-right: 1px solid var(--sf-color-border); color: var(--sf-color-primary); }
.sf-model__facts > div:last-child { border-right: 0; }
.sf-model__facts span { display: flex; min-width: 0; flex-direction: column; color: var(--sf-color-text-muted); font-size: 10px; }
.sf-model__facts strong { overflow: hidden; margin-top: 4px; color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); text-overflow: ellipsis; white-space: nowrap; }
.sf-model__metric { display: grid; margin: 0 var(--sf-space-5) var(--sf-space-5); grid-template-columns: minmax(150px, 0.45fr) 1.55fr; border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-control); }
.sf-model__metric > div { display: flex; padding: var(--sf-space-5); flex-direction: column; justify-content: center; border-right: 1px solid var(--sf-color-border); }
.sf-model__metric > div span { color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-model__metric > div strong { margin-top: var(--sf-space-2); font-size: 28px; }
.sf-model__metric dl { display: grid; padding: var(--sf-space-3); margin: 0; grid-template-columns: 1fr 1fr; gap: var(--sf-space-2); }
.sf-model__metric dl div { display: flex; padding: var(--sf-space-2); justify-content: space-between; gap: var(--sf-space-3); font-size: var(--sf-text-xs); }
.sf-model__metric dt { color: var(--sf-color-text-muted); }
.sf-model__metric dd { margin: 0; color: var(--sf-color-text-secondary); font-weight: 650; text-align: right; }
.sf-model__metric dd.is-missing { color: var(--sf-color-warning); }
.sf-model__evidence { margin: 0 var(--sf-space-5) var(--sf-space-5); overflow: hidden; border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-control); background: linear-gradient(180deg, #fbfbff 0%, #fff 100%); }
.sf-model__evidence-header { display: flex; padding: var(--sf-space-4); align-items: center; justify-content: space-between; gap: var(--sf-space-3); border-bottom: 1px solid var(--sf-color-border); }
.sf-model__evidence-header h3 { margin: 4px 0 0; font-size: var(--sf-text-sm); }
.sf-model__eyebrow { color: var(--sf-color-primary); font-size: 10px; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
.sf-model__scores { display: grid; padding: var(--sf-space-4); margin: 0; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--sf-space-3); }
.sf-model__scores div { padding: var(--sf-space-3); border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-control); background: #fff; }
.sf-model__scores dt { color: var(--sf-color-text-muted); font-size: 10px; }
.sf-model__scores dd { margin: 6px 0 0; color: var(--sf-color-text); font-size: var(--sf-text-lg); font-weight: 760; }
.sf-model__evidence-grid { display: grid; padding: 0 var(--sf-space-4) var(--sf-space-4); grid-template-columns: 1fr 1fr; gap: var(--sf-space-4); }
.sf-model__evidence-grid dl { padding: var(--sf-space-2) var(--sf-space-3); margin: 0; border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-control); background: #fff; }
.sf-model__evidence-grid dl div { display: grid; padding: var(--sf-space-2) 0; grid-template-columns: minmax(92px, .45fr) 1fr; gap: var(--sf-space-3); border-bottom: 1px solid var(--sf-color-border); font-size: var(--sf-text-xs); }
.sf-model__evidence-grid dl div:last-child { border-bottom: 0; }
.sf-model__evidence-grid dt { color: var(--sf-color-text-muted); }
.sf-model__evidence-grid dd { margin: 0; color: var(--sf-color-text-secondary); font-weight: 650; }
.sf-model__limitations { padding: var(--sf-space-4); border-top: 1px solid var(--sf-color-border); background: var(--sf-color-surface-subtle); }
.sf-model__limitations h4 { margin: 0; font-size: var(--sf-text-xs); }
.sf-model__limitations ul { padding-left: 18px; margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.7; }
.sf-model__footer { display: flex; min-height: 56px; padding: var(--sf-space-3) var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-top: 1px solid var(--sf-color-border); background: var(--sf-color-surface-subtle); }
.sf-model__footer p { margin: 0; color: var(--sf-color-text-muted); font-size: 10px; }

@media (max-width: 900px) {
  .sf-model__facts { grid-template-columns: 1fr 1fr; }
  .sf-model__facts > div:nth-child(even) { border-right: 0; }
  .sf-model__metric { grid-template-columns: 1fr; }
  .sf-model__metric > div { border-right: 0; border-bottom: 1px solid var(--sf-color-border); }
  .sf-model__evidence-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .sf-models__notice { align-items: flex-start; }
  .sf-model__header,
  .sf-model__footer { align-items: flex-start; flex-direction: column; }
  .sf-model__facts,
  .sf-model__metric dl { grid-template-columns: 1fr; }
  .sf-model__facts > div { border-right: 0; border-bottom: 1px solid var(--sf-color-border); }
  .sf-model__facts > div:last-child { border-bottom: 0; }
  .sf-model__metric dl div { flex-direction: column; }
  .sf-model__metric dd { text-align: left; }
  .sf-model__scores { grid-template-columns: 1fr 1fr; }
  .sf-model__evidence-grid dl div { grid-template-columns: 1fr; }
}
</style>
