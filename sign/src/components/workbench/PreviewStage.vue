<script setup>
import { Check, Close, FullScreen, VideoPause, VideoPlay, Warning } from '@element-plus/icons-vue'
import { computed, nextTick, ref, watch } from 'vue'

import sampleImage from '@/assets/demo/official-sample-hello.webp'

const props = defineProps({
  mode: { type: String, required: true },
  source: { type: Object, default: null },
  status: { type: String, default: 'idle' },
  progress: { type: Number, default: 0 },
  stageLabel: { type: String, default: '' },
  error: { type: String, default: '' },
  result: { type: Object, default: null },
  stream: { type: Object, default: null },
})

defineEmits(['cancel', 'retry'])

const videoRef = ref()
const playing = ref(true)

const isBusy = computed(() => ['uploading', 'queued', 'running'].includes(props.status))
const sourceType = computed(() => {
  if (props.stream) return 'stream'
  if (props.source?.kind === 'official') return 'image'
  if (props.source?.file?.type?.startsWith('video/')) return 'video'
  if (props.source?.file?.type?.startsWith('image/')) return 'image'
  return 'image'
})

watch(
  () => props.stream,
  async (stream) => {
    await nextTick()
    if (videoRef.value && stream) {
      videoRef.value.srcObject = stream
      await videoRef.value.play().catch(() => {})
    }
  },
  { immediate: true },
)

function togglePlayback() {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
    playing.value = true
  } else {
    videoRef.value.pause()
    playing.value = false
  }
}
</script>

<template>
  <section class="sf-preview" aria-label="识别预览">
    <div class="sf-preview__canvas">
      <video
        v-if="sourceType === 'stream' || sourceType === 'video'"
        ref="videoRef"
        :src="sourceType === 'video' ? source?.previewUrl : undefined"
        :muted="sourceType === 'stream'"
        :autoplay="sourceType === 'stream'"
        playsinline
        controls
      />
      <img
        v-else-if="source"
        :src="source.previewUrl || sampleImage"
        :alt="`识别输入：${source.name || '官方手语样例'}`"
      />
      <div v-else class="sf-preview__empty">
        <el-icon :size="36"><VideoPlay /></el-icon>
        <strong>选择输入后开始识别</strong>
        <span>支持官方样例、本地文件与实时摄像头</span>
      </div>

      <div v-if="result?.confidence != null" class="sf-preview__detection-box" aria-hidden="true">
        <span>手语动作 · {{ Math.round(result.confidence * 100) }}%</span>
      </div>

      <Transition name="sf-result-reveal">
        <div v-if="isBusy" class="sf-preview__processing" role="status">
          <div class="sf-preview__spinner" />
          <strong>{{ stageLabel }}</strong>
          <span>{{ progress }}%</span>
          <div class="sf-preview__bar"><i :style="{ width: `${progress}%` }" /></div>
          <button type="button" @click="$emit('cancel')">
            <el-icon><Close /></el-icon>取消任务
          </button>
        </div>
      </Transition>

      <div v-if="status === 'failed'" class="sf-preview__message sf-preview__message--error">
        <el-icon :size="28"><Warning /></el-icon>
        <strong>识别未完成</strong>
        <span>{{ error }}</span>
        <button type="button" @click="$emit('retry')">重试任务</button>
      </div>

      <div v-if="status === 'cancelled'" class="sf-preview__message">
        <el-icon :size="28"><Close /></el-icon>
        <strong>任务已取消</strong>
        <span>输入和设置已保留，你可以随时重新开始。</span>
        <button type="button" @click="$emit('retry')">重新开始</button>
      </div>

      <div v-if="status === 'succeeded'" class="sf-preview__success">
        <el-icon><Check /></el-icon><span>识别完成</span>
      </div>
    </div>

    <div class="sf-preview__controls">
      <button class="sf-button-reset" type="button" :aria-label="playing ? '暂停预览' : '播放预览'" @click="togglePlayback">
        <el-icon :size="21"><component :is="playing ? VideoPause : VideoPlay" /></el-icon>
      </button>
      <span class="sf-preview__time">{{ result ? '00:04 / 00:04' : '00:00 / 00:04' }}</span>
      <div class="sf-preview__timeline" aria-label="媒体播放进度"><i :style="{ width: result ? '100%' : `${progress}%` }" /></div>
      <button class="sf-button-reset" type="button" aria-label="全屏预览"><el-icon><FullScreen /></el-icon></button>
    </div>

    <div class="sf-preview__frames" aria-label="关键帧时间轴">
      <div v-for="index in 8" :key="index" :class="{ 'is-active': result && index === 4 }">
        <img :src="source?.previewUrl || sampleImage" alt="" />
        <span>{{ index }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sf-preview { min-width: 0; }

.sf-preview__canvas {
  position: relative;
  display: grid;
  min-width: 0;
  overflow: hidden;
  aspect-ratio: 16 / 10;
  place-items: center;
  border-radius: var(--sf-radius-card);
  background: var(--sf-color-canvas);
  color: white;
}

.sf-preview__canvas > img,
.sf-preview__canvas > video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.sf-preview__empty {
  display: flex;
  padding: var(--sf-space-8);
  flex-direction: column;
  align-items: center;
  color: #98a2b3;
  text-align: center;
}
.sf-preview__empty strong { margin-top: var(--sf-space-4); color: white; font-size: var(--sf-text-md); }
.sf-preview__empty span { margin-top: var(--sf-space-2); font-size: var(--sf-text-xs); }

.sf-preview__detection-box {
  position: absolute;
  inset: 11% 23% 8%;
  border: 2px solid #21c7ad;
  border-radius: 4px;
  box-shadow: 0 0 0 1px rgb(11 18 32 / 30%);
}
.sf-preview__detection-box span {
  position: absolute;
  top: -29px;
  left: -2px;
  padding: 4px 8px;
  border-radius: 5px 5px 5px 0;
  background: var(--sf-color-accent);
  color: white;
  font-size: 10px;
  font-weight: 750;
}

.sf-preview__processing,
.sf-preview__message {
  position: absolute;
  inset: 0;
  display: flex;
  padding: var(--sf-space-8);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgb(11 18 32 / 86%);
  text-align: center;
}

.sf-preview__processing strong,
.sf-preview__message strong { margin-top: var(--sf-space-4); font-size: var(--sf-text-md); }
.sf-preview__processing > span,
.sf-preview__message > span { margin-top: var(--sf-space-2); color: #c7cfdf; font-size: var(--sf-text-xs); }
.sf-preview__spinner { width: 36px; height: 36px; border: 3px solid rgb(255 255 255 / 20%); border-top-color: #8e8ef0; border-radius: 50%; animation: sf-spin 0.8s linear infinite; }
.sf-preview__bar { width: min(320px, 80%); height: 5px; margin-top: var(--sf-space-4); overflow: hidden; border-radius: 5px; background: rgb(255 255 255 / 18%); }
.sf-preview__bar i { display: block; height: 100%; border-radius: inherit; background: #8e8ef0; transition: width var(--sf-motion-base) var(--sf-ease); }
.sf-preview__processing button,
.sf-preview__message button {
  display: inline-flex;
  min-height: 36px;
  padding: 0 var(--sf-space-4);
  margin-top: var(--sf-space-5);
  align-items: center;
  gap: 6px;
  border: 1px solid rgb(255 255 255 / 45%);
  border-radius: var(--sf-radius-sm);
  background: transparent;
  color: white;
  cursor: pointer;
  font-size: var(--sf-text-xs);
  font-weight: 700;
}
.sf-preview__message--error .el-icon { color: #f97066; }

.sf-preview__success {
  position: absolute;
  right: var(--sf-space-4);
  bottom: var(--sf-space-4);
  display: flex;
  min-height: 32px;
  padding: 0 var(--sf-space-3);
  align-items: center;
  gap: 7px;
  border-radius: var(--sf-radius-round);
  background: rgb(5 18 28 / 82%);
  color: #63d9c6;
  font-size: var(--sf-text-xs);
  font-weight: 750;
}

.sf-preview__controls {
  display: flex;
  min-height: 54px;
  padding: 0 var(--sf-space-3);
  align-items: center;
  gap: var(--sf-space-3);
  color: var(--sf-color-text-secondary);
}
.sf-preview__controls button { display: grid; width: 36px; height: 36px; place-items: center; border-radius: var(--sf-radius-sm); }
.sf-preview__controls button:hover { background: var(--sf-color-surface-subtle); }
.sf-preview__time { color: var(--sf-color-text-muted); font-family: var(--sf-font-mono); font-size: 10px; }
.sf-preview__timeline { height: 4px; flex: 1; overflow: hidden; border-radius: 4px; background: var(--sf-color-border); }
.sf-preview__timeline i { display: block; height: 100%; border-radius: inherit; background: var(--sf-color-primary); transition: width var(--sf-motion-base) var(--sf-ease); }

.sf-preview__frames {
  display: grid;
  min-width: 0;
  padding: var(--sf-space-3);
  grid-template-columns: repeat(8, minmax(48px, 1fr));
  gap: 5px;
  overflow-x: auto;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  background: var(--sf-color-surface);
}
.sf-preview__frames > div { position: relative; min-width: 48px; overflow: hidden; aspect-ratio: 1.25; border: 2px solid transparent; border-radius: 6px; }
.sf-preview__frames > div.is-active { border-color: var(--sf-color-primary); }
.sf-preview__frames img { width: 100%; height: 100%; object-fit: cover; }
.sf-preview__frames span { position: absolute; inset: auto 3px 2px auto; color: white; font-size: 8px; text-shadow: 0 1px 3px #000; }

@keyframes sf-spin { to { transform: rotate(360deg); } }
.sf-result-reveal-enter-active,
.sf-result-reveal-leave-active { transition: opacity var(--sf-motion-base) var(--sf-ease); }
.sf-result-reveal-enter-from,
.sf-result-reveal-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) { .sf-preview__spinner { animation-duration: 2s; } }
@media (max-width: 640px) {
  .sf-preview__canvas { aspect-ratio: 16 / 11; border-radius: 12px; }
  .sf-preview__frames { grid-template-columns: repeat(8, 62px); }
  .sf-preview__detection-box { inset: 13% 17% 7%; }
}
</style>
