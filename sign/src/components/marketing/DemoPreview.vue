<script setup>
import { Check, RefreshRight, VideoPlay } from '@element-plus/icons-vue'
import { onBeforeUnmount, ref } from 'vue'

import StatusBadge from '@/components/ui/StatusBadge.vue'
import sampleImage from '@/assets/demo/official-sample-hello.webp'

const state = ref('success')
const progress = ref(100)
let timer

function runDemo() {
  clearInterval(timer)
  state.value = 'processing'
  progress.value = 12
  timer = setInterval(() => {
    progress.value += 11
    if (progress.value >= 100) {
      clearInterval(timer)
      progress.value = 100
      state.value = 'success'
    }
  }, 110)
}

onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <article class="sf-demo-preview" aria-label="SignFlow AI 官方样例识别预览">
    <header class="sf-demo-preview__header">
      <div>
        <strong>SignFlow AI / 手语智译平台</strong>
        <span>官方样例 · 已获展示授权</span>
      </div>
      <label>
        <span>样例选择</span>
        <select aria-label="样例选择">
          <option>日常交流 · 问候</option>
          <option>公共服务 · 求助</option>
          <option>教育场景 · 课堂</option>
        </select>
      </label>
    </header>

    <div class="sf-demo-preview__body">
      <div class="sf-demo-preview__media">
        <img :src="sampleImage" alt="官方演示样例：一位女性正在展示双手手语动作" />
        <div class="sf-demo-preview__controls" aria-hidden="true">
          <el-icon><VideoPlay /></el-icon>
          <span>00:02 / 00:05</span>
          <span class="sf-demo-preview__scrub"><i /></span>
          <span>1.0×</span>
        </div>
      </div>
      <div class="sf-demo-preview__result">
        <div class="sf-demo-preview__result-heading">
          <strong>识别结果</strong>
          <StatusBadge
            :label="state === 'processing' ? '正在识别' : '识别完成'"
            :tone="state === 'processing' ? 'processing' : 'success'"
            :pulse="state === 'processing'"
          />
        </div>
        <div class="sf-demo-preview__sentence" :class="{ 'is-processing': state === 'processing' }">
          {{ state === 'processing' ? '正在解析手语动作…' : '你好，很高兴认识你。' }}
        </div>
        <div class="sf-demo-preview__confidence">
          <span>整体置信度</span><strong>{{ state === 'processing' ? '计算中' : '93.6%' }}</strong>
        </div>
        <div class="sf-demo-preview__progress"><i :style="{ width: `${progress}%` }" /></div>
        <div class="sf-demo-preview__labels">
          <span>你好</span><span>很高兴</span><span>认识</span><span>你</span>
        </div>
      </div>
    </div>

    <footer class="sf-demo-preview__footer">
      <span>模型：SignFlow Base 2.1</span>
      <span>输入：官方演示样例</span>
      <span>结果标注：演示数据</span>
      <button type="button" :disabled="state === 'processing'" @click="runDemo">
        <el-icon><component :is="state === 'success' ? RefreshRight : Check" /></el-icon>
        {{ state === 'processing' ? '识别中' : '重新识别' }}
      </button>
    </footer>
  </article>
</template>

<style scoped>
.sf-demo-preview {
  min-width: 0;
  border: 1px solid var(--sf-color-border);
  border-radius: 18px;
  background: var(--sf-color-surface);
  box-shadow: var(--sf-shadow-card);
}

.sf-demo-preview__header,
.sf-demo-preview__footer,
.sf-demo-preview__result-heading,
.sf-demo-preview__confidence {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sf-demo-preview__header {
  min-height: 66px;
  padding: var(--sf-space-3) var(--sf-space-5);
  gap: var(--sf-space-4);
  border-bottom: 1px solid var(--sf-color-border);
}

.sf-demo-preview__header > div {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.sf-demo-preview__header strong { font-size: var(--sf-text-sm); }
.sf-demo-preview__header > div span { margin-top: 2px; color: var(--sf-color-text-muted); font-size: 10px; }

.sf-demo-preview__header label {
  display: flex;
  align-items: center;
  gap: var(--sf-space-2);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-xs);
  white-space: nowrap;
}

.sf-demo-preview__header select {
  min-height: 36px;
  padding: 0 34px 0 12px;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-sm);
  background: white;
  color: var(--sf-color-text-secondary);
  font-size: var(--sf-text-xs);
}

.sf-demo-preview__body {
  display: grid;
  min-width: 0;
  padding: var(--sf-space-4);
  grid-template-columns: minmax(0, 1.45fr) minmax(230px, 0.8fr);
  gap: var(--sf-space-4);
}

.sf-demo-preview__media {
  position: relative;
  min-width: 0;
  overflow: hidden;
  border-radius: 12px;
  background: var(--sf-color-canvas);
}

.sf-demo-preview__media img {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
}

.sf-demo-preview__controls {
  position: absolute;
  inset: auto 0 0;
  display: flex;
  height: 42px;
  padding: 0 var(--sf-space-3);
  align-items: center;
  gap: var(--sf-space-2);
  background: linear-gradient(transparent, rgb(11 18 32 / 90%));
  color: white;
  font-size: 10px;
}

.sf-demo-preview__scrub {
  position: relative;
  height: 3px;
  flex: 1;
  border-radius: 3px;
  background: rgb(255 255 255 / 35%);
}

.sf-demo-preview__scrub i {
  display: block;
  width: 42%;
  height: 100%;
  border-radius: inherit;
  background: #8e8ef0;
}

.sf-demo-preview__result {
  min-width: 0;
  padding: var(--sf-space-4);
  border: 1px solid var(--sf-color-border);
  border-radius: 12px;
}

.sf-demo-preview__result-heading strong { font-size: var(--sf-text-sm); }

.sf-demo-preview__sentence {
  display: flex;
  min-height: 116px;
  padding: var(--sf-space-4);
  margin-top: var(--sf-space-4);
  align-items: center;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  color: var(--sf-color-text);
  font-size: clamp(18px, 2vw, 26px);
  font-weight: 650;
  line-height: 1.45;
}

.sf-demo-preview__sentence.is-processing { color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); }

.sf-demo-preview__confidence {
  margin-top: var(--sf-space-4);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-xs);
}

.sf-demo-preview__confidence strong { color: var(--sf-color-text-secondary); }

.sf-demo-preview__progress {
  height: 5px;
  margin-top: var(--sf-space-2);
  overflow: hidden;
  border-radius: 5px;
  background: var(--sf-color-border);
}

.sf-demo-preview__progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--sf-color-accent);
  transition: width var(--sf-motion-base) var(--sf-ease);
}

.sf-demo-preview__labels {
  display: flex;
  margin-top: var(--sf-space-4);
  flex-wrap: wrap;
  gap: var(--sf-space-2);
}

.sf-demo-preview__labels span {
  padding: 4px 8px;
  border: 1px solid #b8e5dd;
  border-radius: 7px;
  background: var(--sf-color-accent-soft);
  color: var(--sf-color-accent);
  font-size: 10px;
  font-weight: 700;
}

.sf-demo-preview__footer {
  min-height: 52px;
  padding: var(--sf-space-2) var(--sf-space-4);
  flex-wrap: wrap;
  gap: var(--sf-space-3);
  border-top: 1px solid var(--sf-color-border);
  color: var(--sf-color-text-muted);
  font-size: 10px;
}

.sf-demo-preview__footer button {
  display: inline-flex;
  min-height: 34px;
  padding: 0 var(--sf-space-3);
  align-items: center;
  gap: 6px;
  border: 1px solid var(--sf-color-primary);
  border-radius: var(--sf-radius-sm);
  background: white;
  color: var(--sf-color-primary);
  cursor: pointer;
  font-size: var(--sf-text-xs);
  font-weight: 700;
}

.sf-demo-preview__footer button:disabled { cursor: wait; opacity: 0.65; }

@media (max-width: 640px) {
  .sf-demo-preview__header label { display: none; }
  .sf-demo-preview__body { grid-template-columns: 1fr; padding: var(--sf-space-3); }
  .sf-demo-preview__media img { aspect-ratio: 16 / 11; }
  .sf-demo-preview__footer > span { display: none; }
  .sf-demo-preview__footer { justify-content: flex-end; }
}
</style>
