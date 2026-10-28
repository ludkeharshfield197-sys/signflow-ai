<script setup>
import {
  Check,
  Clock,
  CopyDocument,
  Download,
  Headset,
  Microphone,
  RefreshRight,
  Warning,
} from '@element-plus/icons-vue'
import { computed } from 'vue'

import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getServiceScenario } from '@/data/serviceScenarios'

const props = defineProps({
  status: { type: String, default: 'idle' },
  progress: { type: Number, default: 0 },
  result: { type: Object, default: null },
  error: { type: String, default: '' },
  stageLabel: { type: String, default: '' },
  scenarioId: { type: String, default: 'government' },
})

defineEmits([
  'start',
  'retry',
  'save',
  'export',
  'speak',
  'copy',
  'assist',
  'confirm',
  'rephrase',
])

const scenario = computed(() => getServiceScenario(props.scenarioId))
</script>

<template>
  <aside class="sf-inspector sf-panel" aria-label="识别结果">
    <header class="sf-inspector__header">
      <h2>识别结果</h2>
      <StatusBadge
        v-if="status === 'succeeded'"
        label="识别完成"
        tone="success"
      />
      <StatusBadge
        v-else-if="['uploading', 'queued', 'running'].includes(status)"
        :label="stageLabel || '正在识别'"
        tone="processing"
        pulse
      />
    </header>

    <div v-if="status === 'idle'" class="sf-inspector__empty">
      <div><el-icon :size="25"><RefreshRight /></el-icon></div>
      <strong>准备开始识别</strong>
      <p>选择输入与识别预设后，结果会在这里实时出现。</p>
      <button type="button" @click="$emit('start')">开始识别</button>
    </div>

    <div v-else-if="['uploading', 'queued', 'running'].includes(status)" class="sf-inspector__empty">
      <div class="is-processing"><span /></div>
      <strong>{{ stageLabel }}</strong>
      <p>任务会在后台继续处理，请保持当前页面打开。</p>
      <span class="sf-inspector__progress">{{ progress }}%</span>
    </div>

    <div v-else-if="status === 'failed'" class="sf-inspector__empty">
      <div class="is-error"><el-icon :size="25"><Warning /></el-icon></div>
      <strong>识别未完成</strong>
      <p>{{ error }}</p>
      <button type="button" @click="$emit('retry')">重试任务</button>
    </div>

    <div v-else-if="status === 'cancelled'" class="sf-inspector__empty">
      <div><el-icon :size="25"><Clock /></el-icon></div>
      <strong>任务已取消</strong>
      <p>输入和参数仍然保留，你可以重新开始。</p>
      <button type="button" @click="$emit('retry')">重新开始</button>
    </div>

    <template v-else-if="result">
      <section class="sf-inspector__success">
        <div class="sf-inspector__success-title">
          <span><el-icon><Check /></el-icon>生成句子</span>
          <button
            v-if="result.sentence"
            class="sf-button-reset"
            type="button"
            aria-label="复制识别句子"
            @click="$emit('copy', result.sentence)"
          >
            <el-icon><CopyDocument /></el-icon>
          </button>
        </div>
        <p>{{ result.sentence || '未检出可识别的手语动作' }}</p>
        <small v-if="result.dataKind === 'demo'">官方样例演示结果，不作为公开模型准确率证明</small>
      </section>

      <section class="sf-inspector__assistant">
        <div class="sf-inspector__assistant-heading">
          <span>场景沟通助手</span>
          <strong>{{ scenario.assistantTitle }}</strong>
        </div>
        <p>{{ scenario.guidance }}</p>
        <div>
          <button
            data-testid="speak-result"
            type="button"
            :disabled="!result.sentence"
            @click="$emit('speak', result.sentence)"
          >
            <el-icon><Microphone /></el-icon>朗读识别结果
          </button>
          <button
            data-testid="copy-result"
            type="button"
            :disabled="!result.sentence"
            @click="$emit('copy', result.sentence)"
          >
            <el-icon><CopyDocument /></el-icon>复制结果
          </button>
          <button
            data-testid="create-assistance"
            type="button"
            @click="$emit('assist', scenario.id)"
          >
            <el-icon><Headset /></el-icon>生成协助卡
          </button>
        </div>
      </section>

      <section class="sf-inspector__confirmation">
        <div>
          <span>双向确认</span>
          <p>结果由沟通双方确认后再进入后续服务，避免把模型输出直接当作最终结论。</p>
        </div>
        <div>
          <button
            data-testid="confirm-result"
            type="button"
            :disabled="!result.sentence"
            @click="$emit('confirm', {
              resultId: result.id,
              sentence: result.sentence,
              scenarioId: scenario.id,
            })"
          >
            <el-icon><Check /></el-icon>确认含义一致
          </button>
          <button
            data-testid="request-rephrase"
            type="button"
            @click="$emit('rephrase', {
              scenarioId: scenario.id,
              prompt: scenario.rephrasePrompt,
            })"
          >
            <el-icon><RefreshRight /></el-icon>请求重新表达
          </button>
        </div>
      </section>

      <section class="sf-inspector__labels">
        <h3>分词与标签</h3>
        <div v-if="result.labels?.length">
          <span v-for="label in result.labels" :key="`${label.text}-${label.startMs}`">
            {{ label.text }} <small>{{ Math.round(label.confidence * 100) }}%</small>
          </span>
        </div>
        <p v-else class="sf-inspector__labels-empty">当前画面未达到识别阈值，请调整角度、距离或使用测试素材重试。</p>
      </section>

      <dl class="sf-inspector__meta">
        <div><dt>整体置信度</dt><dd>{{ result.confidence != null ? `${(result.confidence * 100).toFixed(1)}%` : '—' }}</dd></div>
        <div><dt>识别耗时</dt><dd>{{ (result.durationMs / 1000).toFixed(2) }} 秒</dd></div>
        <div><dt>模型版本</dt><dd>{{ result.model.name }} {{ result.model.version }}</dd></div>
        <div><dt>输入类型</dt><dd>{{ { live: '实时', image: '图片', video: '视频' }[result.mode] }}</dd></div>
        <div><dt>数据类型</dt><dd>{{ result.dataKind === 'demo' ? '演示数据' : '真实任务' }}</dd></div>
      </dl>

      <div class="sf-inspector__actions">
        <button class="sf-inspector__save" type="button" @click="$emit('save')">
          <el-icon><Check /></el-icon>保存到结果中心
        </button>
        <button class="sf-inspector__export" type="button" @click="$emit('export')">
          <el-icon><Download /></el-icon>导出报告
        </button>
      </div>
    </template>
  </aside>
</template>

<style scoped>
.sf-inspector { align-self: start; overflow: hidden; }
.sf-inspector__header { display: flex; min-height: 60px; padding: 0 var(--sf-space-5); align-items: center; justify-content: space-between; gap: var(--sf-space-3); border-bottom: 1px solid var(--sf-color-border); }
.sf-inspector__header h2 { margin: 0; font-size: var(--sf-text-sm); font-weight: 750; }

.sf-inspector__empty {
  display: flex;
  min-height: 430px;
  padding: var(--sf-space-8);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.sf-inspector__empty > div { display: grid; width: 52px; height: 52px; place-items: center; border-radius: 14px; background: var(--sf-color-primary-soft); color: var(--sf-color-primary); }
.sf-inspector__empty > div.is-error { background: var(--sf-color-danger-soft); color: var(--sf-color-danger); }
.sf-inspector__empty > div.is-processing span { width: 24px; height: 24px; border: 2px solid #c9c9f4; border-top-color: var(--sf-color-primary); border-radius: 50%; animation: sf-inspector-spin 0.8s linear infinite; }
.sf-inspector__empty strong { margin-top: var(--sf-space-4); font-size: var(--sf-text-md); }
.sf-inspector__empty p { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.6; }
.sf-inspector__empty button { min-height: 40px; padding: 0 var(--sf-space-4); margin-top: var(--sf-space-5); border: 0; border-radius: var(--sf-radius-control); background: var(--sf-color-primary); color: white; cursor: pointer; font-size: var(--sf-text-xs); font-weight: 750; }
.sf-inspector__progress { margin-top: var(--sf-space-4); color: var(--sf-color-primary); font-family: var(--sf-font-mono); font-size: var(--sf-text-sm); font-weight: 700; }

.sf-inspector__success,
.sf-inspector__labels,
.sf-inspector__assistant,
.sf-inspector__confirmation { padding: var(--sf-space-5); border-bottom: 1px solid var(--sf-color-border); }
.sf-inspector__success-title { display: flex; align-items: center; justify-content: space-between; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-inspector__success-title span { display: flex; align-items: center; gap: 6px; }
.sf-inspector__success-title span .el-icon { color: var(--sf-color-accent); }
.sf-inspector__success-title button { display: grid; width: 34px; height: 34px; place-items: center; border-radius: var(--sf-radius-sm); color: var(--sf-color-primary); }
.sf-inspector__success p { margin: var(--sf-space-4) 0 0; font-size: var(--sf-text-xl); font-weight: 650; line-height: 1.55; }
.sf-inspector__success small { display: block; margin-top: var(--sf-space-3); color: var(--sf-color-warning); font-size: 10px; line-height: 1.5; }

.sf-inspector__assistant { background: linear-gradient(135deg, #f8f8ff, white); }
.sf-inspector__assistant-heading { display: flex; align-items: center; justify-content: space-between; gap: var(--sf-space-3); }
.sf-inspector__assistant-heading span { color: var(--sf-color-primary); font-size: 9px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; }
.sf-inspector__assistant-heading strong { color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); }
.sf-inspector__assistant > p { margin: var(--sf-space-3) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.65; }
.sf-inspector__assistant > div:last-child { display: grid; margin-top: var(--sf-space-3); grid-template-columns: 1fr 1fr; gap: var(--sf-space-2); }
.sf-inspector__assistant button { display: flex; min-height: 36px; padding: 0 9px; align-items: center; justify-content: center; gap: 5px; border: 1px solid #c9c9f4; border-radius: var(--sf-radius-sm); background: white; color: var(--sf-color-primary); cursor: pointer; font-size: 10px; font-weight: 750; }
.sf-inspector__assistant button:last-child { grid-column: 1 / -1; border-color: var(--sf-color-primary); background: var(--sf-color-primary); color: white; }
.sf-inspector__assistant button:disabled { cursor: not-allowed; opacity: 0.48; }

.sf-inspector__confirmation { background: var(--sf-color-surface); }
.sf-inspector__confirmation > div:first-child > span { color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); font-weight: 800; }
.sf-inspector__confirmation p { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: 10px; line-height: 1.6; }
.sf-inspector__confirmation > div:last-child { display: grid; margin-top: var(--sf-space-3); grid-template-columns: 1fr 1fr; gap: var(--sf-space-2); }
.sf-inspector__confirmation button { display: flex; min-height: 38px; padding: 0 8px; align-items: center; justify-content: center; gap: 5px; border: 1px solid var(--sf-color-border-strong); border-radius: var(--sf-radius-sm); background: white; color: var(--sf-color-text-secondary); cursor: pointer; font-size: 10px; font-weight: 750; }
.sf-inspector__confirmation button:first-child { border-color: #9bd5cc; background: var(--sf-color-accent-soft); color: var(--sf-color-accent); }
.sf-inspector__confirmation button:disabled { cursor: not-allowed; opacity: 0.48; }

.sf-inspector__labels h3 { margin: 0; font-size: var(--sf-text-xs); }
.sf-inspector__labels > div { display: flex; margin-top: var(--sf-space-3); flex-wrap: wrap; gap: var(--sf-space-2); }
.sf-inspector__labels span { padding: 5px 8px; border: 1px solid #b8e5dd; border-radius: 7px; background: var(--sf-color-accent-soft); color: var(--sf-color-accent); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-inspector__labels small { margin-left: 3px; font-size: 9px; opacity: 0.8; }
.sf-inspector__labels-empty { margin: var(--sf-space-3) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.6; }

.sf-inspector__meta { padding: var(--sf-space-3) var(--sf-space-5); margin: 0; }
.sf-inspector__meta div { display: flex; min-height: 42px; align-items: center; justify-content: space-between; gap: var(--sf-space-4); border-bottom: 1px solid var(--sf-color-border); font-size: var(--sf-text-xs); }
.sf-inspector__meta div:last-child { border-bottom: 0; }
.sf-inspector__meta dt { color: var(--sf-color-text-muted); }
.sf-inspector__meta dd { margin: 0; color: var(--sf-color-text-secondary); font-weight: 650; text-align: right; }

.sf-inspector__actions { display: grid; padding: var(--sf-space-5); gap: var(--sf-space-3); border-top: 1px solid var(--sf-color-border); }
.sf-inspector__actions button { display: flex; min-height: 44px; align-items: center; justify-content: center; gap: var(--sf-space-2); border-radius: var(--sf-radius-control); cursor: pointer; font-size: var(--sf-text-xs); font-weight: 750; }
.sf-inspector__save { border: 1px solid var(--sf-color-primary); background: var(--sf-color-primary); color: white; }
.sf-inspector__export { border: 1px solid var(--sf-color-border-strong); background: white; color: var(--sf-color-text-secondary); }
.sf-inspector__save:hover { background: var(--sf-color-primary-hover); }
.sf-inspector__export:hover { border-color: var(--sf-color-primary); color: var(--sf-color-primary); }

@keyframes sf-inspector-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .sf-inspector__empty > div.is-processing span { animation-duration: 2s; } }
</style>
