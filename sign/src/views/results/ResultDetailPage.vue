<script setup>
import { ArrowLeft, Check, Download, Lock, RefreshRight, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import EmptyState from '@/components/ui/EmptyState.vue'
import PublicHeader from '@/components/marketing/PublicHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getOfficialSample } from '@/demo/sample-manifest'
import {
  confirmResult,
  exportResultFile,
  getResult,
  getResultMedia,
  getResultVersions,
  rerunResult,
} from '@/services/results'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const result = ref(null)
const notFound = ref(false)
const source = ref('')
const protectedMediaUrl = ref('')
const mediaError = ref(false)
const versions = ref([])
const confirming = ref(false)
const rerunning = ref(false)
const isPublicDemo = computed(() => route.name === 'public-product-result')
const demoPreviewUrl = computed(() => {
  if (!result.value || result.value.dataKind !== 'demo') return ''
  return result.value.previewUrl || getOfficialSample(result.value.sampleId).image
})
const previewUrl = computed(() => demoPreviewUrl.value || protectedMediaUrl.value)
const isVideo = computed(() => result.value?.media?.contentType?.startsWith('video/'))
const isConfirmed = computed(
  () => result.value?.confirmation?.status === 'both_confirmed',
)

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'medium',
  }).format(new Date(value))
}

function formatPercent(value) {
  const numeric = Number(value)
  return value != null && Number.isFinite(numeric) ? `${(numeric * 100).toFixed(1)}%` : '—'
}

function releaseProtectedMedia() {
  if (protectedMediaUrl.value) URL.revokeObjectURL(protectedMediaUrl.value)
  protectedMediaUrl.value = ''
}

async function loadProtectedMedia() {
  releaseProtectedMedia()
  mediaError.value = false
  if (
    isPublicDemo.value ||
    source.value !== 'api' ||
    !result.value?.media?.available
  ) return
  try {
    const blob = await getResultMedia(result.value.id)
    protectedMediaUrl.value = URL.createObjectURL(blob)
  } catch {
    mediaError.value = true
  }
}

async function loadResult(resultId) {
  loading.value = true
  notFound.value = false
  result.value = null
  versions.value = []
  try {
    const payload = await getResult(resultId)
    result.value = payload.item
    source.value = payload.source
    await loadProtectedMedia()
    if (payload.source === 'api') {
      try {
        versions.value = await getResultVersions(resultId)
      } catch {
        versions.value = [payload.item]
      }
    } else {
      versions.value = [payload.item]
    }
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

async function persistConfirmation() {
  if (isConfirmed.value || source.value !== 'api') return
  confirming.value = true
  try {
    result.value = await confirmResult(result.value.id)
    versions.value = versions.value.map((item) => (
      item.id === result.value.id ? result.value : item
    ))
    ElMessage.success('确认状态已保存：双方已确认')
  } catch {
    ElMessage.error('确认状态保存失败，请稍后重试')
  } finally {
    confirming.value = false
  }
}

async function createRevision() {
  rerunning.value = true
  try {
    const replacement = await rerunResult(result.value.id)
    ElMessage.success(`已创建第 ${replacement.revision} 版重新识别任务`)
    await router.push(`/app/results/${replacement.id}`)
  } catch {
    ElMessage.error('重新识别未能创建，请确认原始媒体仍在保留期内')
  } finally {
    rerunning.value = false
  }
}

function openVersion(version) {
  if (version.id === result.value.id) return
  router.push(`/app/results/${version.id}`)
}

function exportReport() {
  exportResultFile(result.value)
  ElMessage.success('结果报告已导出')
}

function goBack() {
  router.push(isPublicDemo.value ? '/product-tour' : '/app/results')
}

watch(
  () => route.params.id,
  (resultId) => loadResult(resultId),
  { immediate: true },
)

onBeforeUnmount(releaseProtectedMedia)
</script>

<template>
  <PublicHeader v-if="isPublicDemo" />
  <section class="sf-result-detail sf-page">
    <button class="sf-result-detail__back sf-button-reset" type="button" @click="goBack">
      <el-icon><ArrowLeft /></el-icon>{{ isPublicDemo ? '返回产品导览' : '返回结果中心' }}
    </button>

    <div v-if="loading" class="sf-result-detail__loading">正在加载结果详情…</div>
    <EmptyState
      v-else-if="notFound"
      class="sf-panel"
      title="没有找到这个识别结果"
      description="结果可能已被清理，或当前账号没有访问权限。"
      action-label="返回结果中心"
      @action="router.push('/app/results')"
    />
    <template v-else-if="result">
      <header class="sf-result-detail__header">
        <div>
          <div><StatusBadge label="已完成" tone="success" /><StatusBadge v-if="result.dataKind === 'demo'" label="演示数据" tone="processing" /></div>
          <h1>{{ result.sentence }}</h1>
          <p>{{ result.sourceName }} · {{ result.id }}</p>
        </div>
        <div class="sf-result-detail__actions">
          <el-button
            v-if="!isPublicDemo"
            :loading="confirming"
            :disabled="isConfirmed || result.status !== 'succeeded'"
            size="large"
            @click="persistConfirmation"
          >
            <el-icon><Check /></el-icon>{{ isConfirmed ? '双方已确认' : '确认识别结果' }}
          </el-button>
          <el-button
            v-if="!isPublicDemo"
            :loading="rerunning"
            :disabled="result.status !== 'succeeded'"
            size="large"
            @click="createRevision"
          >
            <el-icon><RefreshRight /></el-icon>重新识别
          </el-button>
          <el-button type="primary" size="large" @click="exportReport">
            <el-icon><Download /></el-icon>导出结果
          </el-button>
        </div>
      </header>

      <div v-if="result.dataKind === 'demo'" class="sf-result-detail__notice">
        此结果来自策划的官方样例，仅用于展示产品闭环，不作为公开模型准确率证明。
      </div>

      <div class="sf-result-detail__grid">
        <section class="sf-result-detail__media sf-panel">
          <header><h2>原始媒体与标注</h2><span>授权：{{ result.authorization || '任务所有者上传' }}</span></header>
          <div v-if="previewUrl">
            <video
              v-if="isVideo"
              :src="previewUrl"
              :aria-label="`${result.sourceName}原始授权视频`"
              controls
              playsinline
              preload="metadata"
            />
            <img v-else :src="previewUrl" :alt="`${result.sourceName}原始授权画面`" />
            <span v-if="result.confidence != null" class="sf-result-detail__box">手语动作 · {{ formatPercent(result.confidence) }}</span>
            <span v-if="result.dataKind === 'demo'" class="sf-result-detail__play"><el-icon><VideoPlay /></el-icon>官方样例</span>
          </div>
          <div v-else class="sf-result-detail__protected">
            <el-icon :size="32"><Lock /></el-icon>
            <strong>{{ mediaError ? '原始媒体读取失败' : '原始媒体已清理或不可用' }}</strong>
            <span>媒体仅向任务所有者授权提供，不会用样例内容替代真实输入。</span>
          </div>
        </section>

        <aside class="sf-result-detail__summary sf-panel">
          <header><h2>结果摘要</h2></header>
          <dl>
            <div><dt>整体置信度</dt><dd>{{ formatPercent(result.confidence) }}</dd></div>
            <div><dt>识别耗时</dt><dd>{{ (result.durationMs / 1000).toFixed(2) }} 秒</dd></div>
            <div><dt>输入类型</dt><dd>{{ { live: '实时', image: '图片', video: '视频' }[result.mode] }}</dd></div>
            <div><dt>模型版本</dt><dd>{{ result.model.name }} {{ result.model.version }}</dd></div>
            <div><dt>识别预设</dt><dd>{{ result.preset || 'balanced' }}</dd></div>
            <div><dt>创建时间</dt><dd>{{ formatDate(result.createdAt) }}</dd></div>
            <div><dt>结果版本</dt><dd>第 {{ result.revision || 1 }} 版</dd></div>
            <div><dt>确认状态</dt><dd>{{ result.confirmation?.label || '待确认' }}</dd></div>
            <div><dt>数据来源</dt><dd>{{ source === 'api' ? '识别结果接口' : '本地官方样例' }}</dd></div>
          </dl>
        </aside>
      </div>

      <section class="sf-result-detail__timeline sf-panel">
        <header><h2>标签与时间轴</h2><p>每个标签保留置信度和出现区间，便于复查连续表达。</p></header>
        <div class="sf-result-detail__track">
          <span
            v-for="label in result.labels"
            :key="`${label.text}-${label.startMs}`"
            :style="{
              left: `${(label.startMs / result.inputDurationMs) * 100}%`,
              width: `${((label.endMs - label.startMs) / result.inputDurationMs) * 100}%`,
            }"
          >
            <strong>{{ label.text }}</strong><small>{{ Math.round(label.confidence * 100) }}%</small>
          </span>
        </div>
        <div class="sf-result-detail__ticks"><span>0 秒</span><span>1 秒</span><span>2 秒</span><span>3 秒</span><span>4.1 秒</span></div>
      </section>

      <section class="sf-result-detail__audit sf-panel">
        <header><h2>参数与追溯</h2></header>
        <div>
          <span>置信度阈值 <strong>{{ result.advanced?.confidence ?? 0.45 }}</strong></span>
          <span>IoU 阈值 <strong>{{ result.advanced?.iou ?? 0.5 }}</strong></span>
          <span>模型快照 <strong>{{ result.trace?.modelSnapshot?.name || result.model.name }} {{ result.trace?.modelSnapshot?.version || result.model.version }}</strong></span>
          <span>文件 SHA-256 <strong class="sf-result-detail__hash">{{ result.trace?.fileSha256 || '历史任务未记录' }}</strong></span>
        </div>
        <p><el-icon><Lock /></el-icon>原始媒体、文件哈希、模型版本、识别参数与确认记录均按账号权限隔离并持久保存。</p>
      </section>

      <section v-if="versions.length" class="sf-result-detail__versions sf-panel">
        <header>
          <div><h2>结果版本对比</h2><p>重新识别会创建新版本，旧结果保持不变。</p></div>
          <span>{{ versions.length }} 个版本</span>
        </header>
        <div class="sf-result-detail__version-list">
          <button
            v-for="version in versions"
            :key="version.id"
            type="button"
            :class="{ 'is-current': version.id === result.id }"
            @click="openVersion(version)"
          >
            <span>第 {{ version.revision || 1 }} 版</span>
            <strong>{{ version.sentence || ({ queued: '等待识别', running: '正在识别' }[version.status] || '暂无识别文本') }}</strong>
            <small>{{ version.model?.version || '—' }} · {{ formatPercent(version.confidence) }} · {{ formatDate(version.createdAt) }}</small>
          </button>
        </div>
      </section>
    </template>
  </section>
</template>

<style scoped>
.sf-result-detail__back { display: inline-flex; min-height: 40px; margin-bottom: var(--sf-space-5); align-items: center; gap: var(--sf-space-2); border-radius: var(--sf-radius-sm); color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); font-weight: 650; }
.sf-result-detail__back:hover { color: var(--sf-color-primary); }
.sf-result-detail__loading { display: grid; min-height: 420px; place-items: center; color: var(--sf-color-text-muted); }
.sf-result-detail__header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--sf-space-6); }
.sf-result-detail__header > div > div { display: flex; gap: var(--sf-space-2); }
.sf-result-detail__header h1 { margin: var(--sf-space-4) 0 0; font-size: var(--sf-text-3xl); line-height: 1.25; }
.sf-result-detail__header p { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-result-detail__actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: var(--sf-space-2); }
.sf-result-detail__actions .el-button + .el-button { margin-left: 0; }
.sf-result-detail__notice { padding: var(--sf-space-3) var(--sf-space-4); margin-top: var(--sf-space-5); border: 1px solid #c9c9f4; border-radius: var(--sf-radius-control); background: var(--sf-color-primary-soft); color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-result-detail__grid { display: grid; margin-top: var(--sf-space-5); grid-template-columns: minmax(0, 1.55fr) minmax(280px, 0.7fr); gap: var(--sf-space-4); }
.sf-result-detail__media,
.sf-result-detail__summary,
.sf-result-detail__timeline,
.sf-result-detail__audit { overflow: hidden; }
.sf-result-detail__media > header,
.sf-result-detail__summary > header,
.sf-result-detail__timeline > header,
.sf-result-detail__audit > header { display: flex; min-height: 62px; padding: 0 var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); }
.sf-result-detail h2 { margin: 0; font-size: var(--sf-text-sm); }
.sf-result-detail__media header span,
.sf-result-detail__timeline header p { margin: 0; color: var(--sf-color-text-muted); font-size: 10px; }
.sf-result-detail__media > div { position: relative; overflow: hidden; aspect-ratio: 16 / 9; background: var(--sf-color-canvas); }
.sf-result-detail__media > div.sf-result-detail__protected { display: flex; align-items: center; justify-content: center; flex-direction: column; gap: var(--sf-space-3); color: #c7cfdf; text-align: center; }
.sf-result-detail__protected strong { color: white; font-size: var(--sf-text-sm); }
.sf-result-detail__protected span { max-width: 420px; padding-inline: var(--sf-space-5); color: #98a2b3; font-size: var(--sf-text-xs); line-height: 1.6; }
.sf-result-detail__media img,
.sf-result-detail__media video { width: 100%; height: 100%; object-fit: contain; }
.sf-result-detail__box { position: absolute; inset: 10% 23% 8%; border: 2px solid var(--sf-color-accent); color: white; font-size: 10px; }
.sf-result-detail__box::first-line { background: var(--sf-color-accent); }
.sf-result-detail__play { position: absolute; right: var(--sf-space-4); bottom: var(--sf-space-3); display: flex; align-items: center; gap: 6px; color: white; font-size: 10px; }
.sf-result-detail__summary dl { padding: var(--sf-space-2) var(--sf-space-5); margin: 0; }
.sf-result-detail__summary dl div { display: flex; min-height: 46px; align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); font-size: var(--sf-text-xs); }
.sf-result-detail__summary dl div:last-child { border-bottom: 0; }
.sf-result-detail__summary dt { color: var(--sf-color-text-muted); }
.sf-result-detail__summary dd { margin: 0; color: var(--sf-color-text-secondary); font-weight: 650; text-align: right; }
.sf-result-detail__timeline,
.sf-result-detail__audit,
.sf-result-detail__versions { margin-top: var(--sf-space-4); }
.sf-result-detail__track { position: relative; height: 72px; margin: var(--sf-space-8) var(--sf-space-6) 0; border-radius: var(--sf-radius-sm); background: var(--sf-color-surface-subtle); }
.sf-result-detail__track > span { position: absolute; top: 10px; bottom: 10px; display: flex; min-width: 40px; padding: 0 var(--sf-space-2); align-items: center; justify-content: center; flex-direction: column; overflow: hidden; border: 1px solid #b8e5dd; border-radius: 7px; background: var(--sf-color-accent-soft); color: var(--sf-color-accent); }
.sf-result-detail__track strong { font-size: var(--sf-text-xs); }
.sf-result-detail__track small { font-size: 8px; }
.sf-result-detail__ticks { display: flex; padding: var(--sf-space-2) var(--sf-space-6) var(--sf-space-5); justify-content: space-between; color: var(--sf-color-text-disabled); font-size: 9px; }
.sf-result-detail__audit > div { display: grid; padding: var(--sf-space-5); grid-template-columns: repeat(4, 1fr); gap: var(--sf-space-3); }
.sf-result-detail__audit > div span { padding: var(--sf-space-3); border-right: 1px solid var(--sf-color-border); color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-result-detail__audit > div span:last-child { border-right: 0; }
.sf-result-detail__audit strong { display: block; margin-top: var(--sf-space-2); color: var(--sf-color-text-secondary); }
.sf-result-detail__hash { overflow-wrap: anywhere; font-family: var(--sf-font-mono); font-size: 10px; line-height: 1.5; }
.sf-result-detail__audit > p { display: flex; padding: 0 var(--sf-space-5) var(--sf-space-5); margin: 0; align-items: center; gap: var(--sf-space-2); color: var(--sf-color-text-muted); font-size: 10px; }
.sf-result-detail__audit > p .el-icon { color: var(--sf-color-primary); }
.sf-result-detail__versions > header { display: flex; min-height: 68px; padding: 0 var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); }
.sf-result-detail__versions header p { margin: 4px 0 0; color: var(--sf-color-text-muted); font-size: 10px; }
.sf-result-detail__versions header > span { color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-result-detail__version-list { display: grid; padding: var(--sf-space-4); grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: var(--sf-space-3); }
.sf-result-detail__version-list button { display: flex; min-height: 112px; padding: var(--sf-space-4); align-items: flex-start; flex-direction: column; gap: var(--sf-space-2); border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-control); background: #fff; color: var(--sf-color-text); text-align: left; cursor: pointer; }
.sf-result-detail__version-list button:hover,
.sf-result-detail__version-list button.is-current { border-color: var(--sf-color-primary); background: var(--sf-color-primary-soft); }
.sf-result-detail__version-list button > span { color: var(--sf-color-primary); font-size: 10px; font-weight: 750; }
.sf-result-detail__version-list button > strong { font-size: var(--sf-text-sm); }
.sf-result-detail__version-list button > small { margin-top: auto; color: var(--sf-color-text-muted); font-size: 9px; line-height: 1.5; }

@media (max-width: 960px) {
  .sf-result-detail__grid { grid-template-columns: 1fr; }
  .sf-result-detail__audit > div { grid-template-columns: 1fr 1fr; }
  .sf-result-detail__audit > div span:nth-child(2) { border-right: 0; }
}
@media (max-width: 640px) {
  .sf-result-detail__header { flex-direction: column; }
  .sf-result-detail__actions { width: 100%; }
  .sf-result-detail__actions .el-button { width: 100%; }
  .sf-result-detail__media > header { align-items: flex-start; padding-block: var(--sf-space-3); flex-direction: column; }
  .sf-result-detail__track { margin-inline: var(--sf-space-4); }
  .sf-result-detail__ticks { padding-inline: var(--sf-space-4); }
  .sf-result-detail__audit > div { grid-template-columns: 1fr; }
  .sf-result-detail__audit > div span { border-right: 0; border-bottom: 1px solid var(--sf-color-border); }
}
</style>
