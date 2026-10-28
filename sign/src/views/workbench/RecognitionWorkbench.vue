<script setup>
import { Check, Lock, RefreshRight, VideoPlay, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { onBeforeUnmount, ref, watch } from 'vue'

import AdvancedSettingsDrawer from '@/components/workbench/AdvancedSettingsDrawer.vue'
import ModeSwitcher from '@/components/workbench/ModeSwitcher.vue'
import PreviewStage from '@/components/workbench/PreviewStage.vue'
import ResultInspector from '@/components/workbench/ResultInspector.vue'
import ServiceContextBar from '@/components/workbench/ServiceContextBar.vue'
import SourcePanel from '@/components/workbench/SourcePanel.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { useDetectionJob } from '@/composables/useDetectionJob'
import { useModelCatalog } from '@/composables/useModelCatalog'
import { getServiceScenario } from '@/data/serviceScenarios'
import { getOfficialSample } from '@/demo/sample-manifest'

const props = defineProps({
  initialMode: {
    type: String,
    default: 'live',
    validator: (value) => ['live', 'image', 'video'].includes(value),
  },
  initialSampleId: { type: String, default: 'official-hello-01' },
  guest: { type: Boolean, default: false },
})
const emit = defineEmits(['complete'])

const mode = ref(props.initialMode)
const preset = ref('balanced')
const initialSample = getOfficialSample(props.initialSampleId)
const source = ref({
  kind: 'official',
  sampleId: initialSample.id,
  name: initialSample.name,
  previewUrl: initialSample.image,
  authorization: initialSample.authorization,
})
const modelId = ref('')
const confidence = ref(0.45)
const iou = ref(0.5)
const advancedOpen = ref(false)
const scenarioId = ref('government')
const largeText = ref(false)
const highContrast = ref(false)
const assistanceNotice = ref('')
const cameraStream = ref(null)
const cameraError = ref('')
let previousObjectUrl = ''

const catalog = useModelCatalog()
const job = useDetectionJob()
let lastCompletedId = ''

watch(
  catalog.defaultModelId,
  (value) => {
    if (!modelId.value && value) modelId.value = value
  },
  { immediate: true },
)

watch(preset, (value) => {
  const selected = catalog.presets.find((item) => item.id === value)
  if (selected) {
    confidence.value = selected.confidence
    iou.value = selected.iou
  }
})

watch(mode, () => {
  job.reset()
  cameraError.value = ''
  if (mode.value !== 'live') stopCamera()
})

watch(
  () => job.status.value,
  (value) => {
    if (
      value === 'succeeded'
      && job.result.value?.id
      && job.result.value.id !== lastCompletedId
    ) {
      lastCompletedId = job.result.value.id
      emit('complete', job.result.value)
    }
  },
)

function updateSource(nextSource) {
  if (previousObjectUrl) URL.revokeObjectURL(previousObjectUrl)
  previousObjectUrl = nextSource?.kind === 'upload' ? nextSource.previewUrl : ''
  source.value = nextSource
  job.reset()
}

async function requestCamera() {
  cameraError.value = ''
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = '当前浏览器不支持摄像头访问，请改用图片、视频或官方样例。'
    return
  }
  stopCamera()
  try {
    cameraStream.value = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
      audio: false,
    })
    updateSource({ kind: 'camera', name: '实时摄像头' })
  } catch {
    cameraError.value = '摄像头权限未开启。请在浏览器地址栏的权限设置中允许摄像头，然后点击“重新授权”。'
  }
}

function stopCamera() {
  cameraStream.value?.getTracks?.().forEach((track) => track.stop())
  cameraStream.value = null
}

async function start() {
  if (!source.value) {
    ElMessage.warning('请先选择官方样例或上传输入')
    return
  }
  if (source.value.kind !== 'official' && !modelId.value) {
    ElMessage.warning(
      catalog.loading.value
        ? '识别模型正在加载，请稍后再试。'
        : '当前没有可用的识别模型，请检查模型服务后重试。',
    )
    return
  }
  if (mode.value === 'live' && source.value.kind === 'camera' && !cameraStream.value) {
    await requestCamera()
    if (!cameraStream.value) return
  }

  await job.start({
    mode: mode.value,
    stream: cameraStream.value,
    source: source.value,
    modelId: modelId.value,
    preset: preset.value,
    advanced: { confidence: confidence.value, iou: iou.value },
  })
}

function saveResult() {
  if (!job.result.value) return
  const existing = JSON.parse(window.localStorage.getItem('signflow.savedResults') || '[]')
  const withoutDuplicate = existing.filter((item) => item.id !== job.result.value.id)
  window.localStorage.setItem(
    'signflow.savedResults',
    JSON.stringify([job.result.value, ...withoutDuplicate].slice(0, 50)),
  )
  ElMessage.success('结果已保存到结果中心')
}

function exportResult() {
  if (!job.result.value) return
  const report = {
    product: 'SignFlow AI',
    exportedAt: new Date().toISOString(),
    disclaimer: job.result.value.dataKind === 'demo'
      ? '本报告来自官方样例演示，不代表公开模型准确率。'
      : '本报告来自真实识别任务。',
    result: job.result.value,
  }
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(report, null, 2)], { type: 'application/json;charset=utf-8' }),
  )
  const link = document.createElement('a')
  link.href = url
  link.download = `signflow-result-${job.result.value.id}.json`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('结果报告已导出')
}

async function copyResult(sentence) {
  if (!sentence) return
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(sentence)
  } else {
    const field = document.createElement('textarea')
    field.value = sentence
    field.setAttribute('readonly', '')
    field.style.position = 'fixed'
    field.style.opacity = '0'
    document.body.appendChild(field)
    field.select()
    document.execCommand('copy')
    field.remove()
  }
  ElMessage.success('识别结果已复制')
}

function speakResult(sentence) {
  if (!sentence) return
  if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
    ElMessage.warning('当前浏览器不支持语音朗读')
    return
  }
  window.speechSynthesis.cancel()
  const utterance = new window.SpeechSynthesisUtterance(sentence)
  utterance.lang = 'zh-CN'
  utterance.rate = 0.92
  window.speechSynthesis.speak(utterance)
  ElMessage.success('正在朗读识别结果')
}

function createAssistanceCard(selectedScenarioId) {
  const selectedScenario = getServiceScenario(selectedScenarioId)
  const card = {
    id: `assist-${Date.now()}`,
    scenarioId: selectedScenario.id,
    scenario: selectedScenario.name,
    title: selectedScenario.assistanceLabel,
    sentence: job.result.value?.sentence || '尚未生成识别句子',
    guidance: selectedScenario.guidance,
    createdAt: new Date().toISOString(),
    delivery: 'local-only',
  }
  let existing = []
  try {
    existing = JSON.parse(window.localStorage.getItem('signflow.assistanceCards') || '[]')
  } catch {
    existing = []
  }
  window.localStorage.setItem(
    'signflow.assistanceCards',
    JSON.stringify([card, ...existing].slice(0, 20)),
  )
  assistanceNotice.value = `${selectedScenario.assistanceLabel}已生成并保存在本机；尚未发送给外部人员。`
  ElMessage.success('协助卡已生成')
}

function confirmResult(payload) {
  let existing = []
  try {
    existing = JSON.parse(window.localStorage.getItem('signflow.confirmations') || '[]')
  } catch {
    existing = []
  }
  const confirmation = {
    ...payload,
    status: 'confirmed',
    confirmedAt: new Date().toISOString(),
  }
  window.localStorage.setItem(
    'signflow.confirmations',
    JSON.stringify([confirmation, ...existing].slice(0, 50)),
  )
  assistanceNotice.value = '双方确认已记录在本机；识别结果可以继续用于当前服务流程。'
  ElMessage.success('已记录双向确认')
}

function requestRephrase(payload) {
  assistanceNotice.value = payload.prompt
  ElMessage.info('已生成重新表达提示')
}

onBeforeUnmount(() => {
  stopCamera()
  if (previousObjectUrl) URL.revokeObjectURL(previousObjectUrl)
})
</script>

<template>
  <section
    class="sf-workbench"
    :class="{
      'sf-workbench--guest': guest,
      'sf-workbench--large-text': largeText,
      'sf-workbench--high-contrast': highContrast,
    }"
  >
    <PageHeader
      :title="guest ? '手语沟通在线体验' : '智能手语沟通工作台'"
      :description="guest
        ? '无需账号，体验从手语识别到双向确认的完整沟通流程。'
        : '选择服务场景与输入来源，生成可朗读、可复制、可确认的沟通结果。'"
    >
      <template #actions>
        <ModeSwitcher v-model="mode" />
      </template>
    </PageHeader>

    <div v-if="guest" class="sf-workbench__demo-notice">
      <StatusBadge label="演示模式" tone="processing" />
      <span>所有结果均为策划的官方样例数据，并非实时模型准确率证明。</span>
    </div>

    <div v-if="cameraError" class="sf-workbench__camera-error" role="alert">
      <el-icon :size="20"><Warning /></el-icon>
      <div>
        <strong>无法使用摄像头</strong>
        <p>{{ cameraError }}</p>
      </div>
      <button type="button" @click="requestCamera">重新授权</button>
    </div>

    <ServiceContextBar
      v-model:scenario="scenarioId"
      v-model:large-text="largeText"
      v-model:high-contrast="highContrast"
    />

    <div v-if="assistanceNotice" class="sf-workbench__assistance-notice" role="status">
      <el-icon><Check /></el-icon>
      <span>{{ assistanceNotice }}</span>
      <button type="button" @click="assistanceNotice = ''">知道了</button>
    </div>

    <div class="sf-workbench__grid">
      <SourcePanel
        :mode="mode"
        :source="source"
        :preset="preset"
        :model-id="modelId"
        :presets="catalog.presets"
        :models="catalog.models.value"
        :disabled="job.isBusy.value"
        @update:source="updateSource"
        @update:preset="preset = $event"
        @update:model-id="modelId = $event"
        @open-advanced="advancedOpen = true"
        @request-camera="requestCamera"
      />

      <div class="sf-workbench__center">
        <PreviewStage
          :mode="mode"
          :source="source"
          :stream="cameraStream"
          :status="job.status.value"
          :progress="job.progress.value"
          :stage-label="job.stageLabel.value"
          :result="job.result.value"
          :error="job.error.value"
          @cancel="job.cancel"
          @retry="start"
        />
        <div class="sf-workbench__taskbar">
          <div>
            <el-icon :class="{ 'is-success': job.status.value === 'succeeded' }">
              <component :is="job.status.value === 'succeeded' ? Check : Lock" />
            </el-icon>
            <span>任务状态：<strong>{{ job.stageLabel.value }}</strong></span>
          </div>
          <div class="sf-workbench__task-actions">
            <button
              v-if="job.canCancel.value"
              class="sf-workbench__cancel"
              type="button"
              @click="job.cancel"
            >
              取消任务
            </button>
            <button
              class="sf-workbench__start"
              type="button"
              :disabled="job.isBusy.value"
              @click="start"
            >
              <el-icon><component :is="job.status.value === 'idle' ? VideoPlay : RefreshRight" /></el-icon>
              {{ job.status.value === 'idle' ? '开始识别' : '重新识别' }}
            </button>
          </div>
        </div>
      </div>

      <ResultInspector
        :status="job.status.value"
        :progress="job.progress.value"
        :stage-label="job.stageLabel.value"
        :result="job.result.value"
        :error="job.error.value"
        :scenario-id="scenarioId"
        @start="start"
        @retry="start"
        @save="saveResult"
        @export="exportResult"
        @speak="speakResult"
        @copy="copyResult"
        @assist="createAssistanceCard"
        @confirm="confirmResult"
        @rephrase="requestRephrase"
      />
    </div>

    <footer class="sf-workbench__privacy">
      <el-icon><Lock /></el-icon>
      <span>输入内容仅用于生成当前识别结果，不会默认进入训练集；官方样例会单独标注。</span>
    </footer>

    <AdvancedSettingsDrawer
      :open="advancedOpen"
      :model-id="modelId"
      :models="catalog.models.value"
      :confidence="confidence"
      :iou="iou"
      @close="advancedOpen = false"
      @update:model-id="modelId = $event"
      @update:confidence="confidence = $event"
      @update:iou="iou = $event"
    />
  </section>
</template>

<style scoped>
.sf-workbench {
  width: min(100%, 1580px);
  padding: var(--sf-space-8);
  margin: 0 auto;
}

.sf-workbench--large-text {
  --sf-text-xs: 14px;
  --sf-text-sm: 16px;
  --sf-text-md: 18px;
  --sf-text-lg: 20px;
  --sf-text-xl: 23px;
}

.sf-workbench--high-contrast {
  --sf-color-text: #080b12;
  --sf-color-text-secondary: #111827;
  --sf-color-text-muted: #344054;
  --sf-color-border: #98a2b3;
  --sf-color-border-strong: #475467;
  --sf-color-primary: #3730a3;
  --sf-color-primary-hover: #29226f;
  --sf-color-primary-soft: #e8e7ff;
}

.sf-workbench__demo-notice,
.sf-workbench__camera-error,
.sf-workbench__assistance-notice {
  display: flex;
  min-height: 48px;
  padding: var(--sf-space-3) var(--sf-space-4);
  margin-bottom: var(--sf-space-5);
  align-items: center;
  gap: var(--sf-space-3);
  border: 1px solid #c9c9f4;
  border-radius: var(--sf-radius-control);
  background: var(--sf-color-primary-soft);
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-xs);
}

.sf-workbench__camera-error { border-color: #fedf89; background: var(--sf-color-warning-soft); }
.sf-workbench__camera-error > .el-icon { flex: 0 0 auto; color: var(--sf-color-warning); }
.sf-workbench__camera-error div { min-width: 0; flex: 1; }
.sf-workbench__camera-error strong { font-size: var(--sf-text-xs); }
.sf-workbench__camera-error p { margin: 2px 0 0; color: var(--sf-color-text-muted); font-size: 10px; }
.sf-workbench__camera-error button { min-height: 36px; padding: 0 var(--sf-space-3); border: 1px solid var(--sf-color-warning); border-radius: var(--sf-radius-sm); background: white; color: var(--sf-color-warning); cursor: pointer; font-size: var(--sf-text-xs); font-weight: 700; }
.sf-workbench__assistance-notice { border-color: #9bd5cc; background: var(--sf-color-accent-soft); color: var(--sf-color-text-secondary); }
.sf-workbench__assistance-notice .el-icon { color: var(--sf-color-accent); }
.sf-workbench__assistance-notice span { min-width: 0; flex: 1; }
.sf-workbench__assistance-notice button { min-height: 32px; padding: 0 var(--sf-space-3); border: 1px solid var(--sf-color-accent); border-radius: var(--sf-radius-sm); background: white; color: var(--sf-color-accent); cursor: pointer; font-size: 10px; font-weight: 750; }

.sf-workbench__grid {
  display: grid;
  min-width: 0;
  align-items: start;
  grid-template-columns: minmax(240px, 280px) minmax(420px, 1fr) minmax(280px, 330px);
  gap: var(--sf-space-4);
}

.sf-workbench__center { min-width: 0; }

.sf-workbench__taskbar {
  display: flex;
  min-height: 58px;
  padding: var(--sf-space-2) var(--sf-space-3);
  margin-top: var(--sf-space-3);
  align-items: center;
  justify-content: space-between;
  gap: var(--sf-space-3);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  background: white;
}

.sf-workbench__taskbar > div,
.sf-workbench__task-actions,
.sf-workbench__taskbar button {
  display: flex;
  align-items: center;
}

.sf-workbench__taskbar > div { min-width: 0; gap: var(--sf-space-2); color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-workbench__taskbar .el-icon.is-success { color: var(--sf-color-accent); }
.sf-workbench__taskbar strong { color: var(--sf-color-text-secondary); }
.sf-workbench__task-actions { flex: 0 0 auto; gap: var(--sf-space-2); }
.sf-workbench__taskbar button { min-height: 38px; padding: 0 var(--sf-space-3); justify-content: center; gap: 6px; border-radius: var(--sf-radius-sm); cursor: pointer; font-size: var(--sf-text-xs); font-weight: 700; }
.sf-workbench__start { border: 1px solid var(--sf-color-primary); background: var(--sf-color-primary); color: white; }
.sf-workbench__start:disabled { cursor: wait; opacity: 0.65; }
.sf-workbench__cancel { border: 1px solid var(--sf-color-danger); background: white; color: var(--sf-color-danger); }

.sf-workbench__privacy {
  display: flex;
  min-height: 46px;
  margin-top: var(--sf-space-4);
  align-items: center;
  justify-content: center;
  gap: var(--sf-space-2);
  color: var(--sf-color-text-muted);
  font-size: 10px;
  text-align: center;
}
.sf-workbench__privacy .el-icon { color: var(--sf-color-primary); }

@media (max-width: 1279px) {
  .sf-workbench__grid { grid-template-columns: minmax(230px, 0.72fr) minmax(440px, 1.55fr); }
  .sf-workbench__grid :deep(.sf-inspector) { grid-column: 1 / -1; }
  .sf-workbench__grid :deep(.sf-inspector__empty) { min-height: 260px; }
}

@media (max-width: 820px) {
  .sf-workbench { padding: var(--sf-space-4); }
  .sf-workbench :deep(.sf-page-header) { flex-direction: column; gap: var(--sf-space-4); }
  .sf-workbench :deep(.sf-page-header__actions) { width: 100%; }
  .sf-workbench__grid { display: flex; flex-direction: column; }
  .sf-workbench__center { order: 1; width: 100%; }
  .sf-workbench__grid :deep(.sf-inspector) { order: 2; width: 100%; }
  .sf-workbench__grid :deep(.sf-source-panel) { order: 3; width: 100%; }
}

@media (max-width: 560px) {
  .sf-workbench__taskbar { align-items: stretch; flex-direction: column; }
  .sf-workbench__task-actions { display: grid; grid-template-columns: 1fr 1fr; }
  .sf-workbench__taskbar button { min-height: 44px; }
  .sf-workbench__camera-error { align-items: flex-start; flex-wrap: wrap; }
}
</style>
