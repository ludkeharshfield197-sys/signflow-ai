<script setup>
import { Camera, InfoFilled, Setting, UploadFilled } from '@element-plus/icons-vue'
import { computed } from 'vue'

import { officialSamples } from '@/demo/sample-manifest'

const props = defineProps({
  mode: { type: String, required: true },
  source: { type: Object, default: null },
  preset: { type: String, default: 'balanced' },
  modelId: { type: String, default: '' },
  presets: { type: Array, default: () => [] },
  models: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update:source',
  'update:preset',
  'update:modelId',
  'open-advanced',
  'request-camera',
])

const languageOptions = computed(() => [
  {
    code: 'csl',
    label: '中文手语',
    abbreviation: 'CSL',
    description: '37 类中文手语词汇',
    model: props.models.find((item) => item.languageCode === 'csl'),
  },
  {
    code: 'asl',
    label: '英文手语',
    abbreviation: 'ASL',
    description: '80 类英文手语词汇',
    model: props.models.find((item) => item.languageCode === 'asl'),
  },
].filter((item) => item.model))

function chooseLanguage(option) {
  emit('update:modelId', String(option.model.id))
}

function chooseSample(sample) {
  emit('update:source', {
    kind: 'official',
    sampleId: sample.id,
    name: sample.name,
    previewUrl: sample.image,
    authorization: sample.authorization,
  })
}

function chooseFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  emit('update:source', {
    kind: 'upload',
    file,
    name: file.name,
    previewUrl: URL.createObjectURL(file),
  })
  event.target.value = ''
}
</script>

<template>
  <aside class="sf-source-panel sf-panel" aria-label="输入来源与识别预设">
    <div v-if="languageOptions.length" class="sf-source-panel__section sf-source-panel__language">
      <div class="sf-source-panel__heading">
        <h2>手语识别类型</h2>
        <span>选择后立即生效</span>
      </div>
      <div class="sf-source-panel__language-options" role="group" aria-label="手语识别类型">
        <button
          v-for="option in languageOptions"
          :key="option.code"
          :data-testid="`language-${option.code}`"
          type="button"
          :class="{ 'is-selected': String(option.model.id) === modelId }"
          :aria-pressed="String(option.model.id) === modelId"
          :disabled="disabled"
          @click="chooseLanguage(option)"
        >
          <span>
            <strong>{{ option.label }}</strong>
            <small>{{ option.description }}</small>
          </span>
          <b>{{ option.abbreviation }}</b>
        </button>
      </div>
    </div>

    <div class="sf-source-panel__section">
      <div class="sf-source-panel__heading">
        <h2>输入来源</h2>
        <el-tooltip content="官方样例结果会明确标记为演示数据">
          <el-icon><InfoFilled /></el-icon>
        </el-tooltip>
      </div>

      <template v-if="mode === 'live'">
        <button
          class="sf-source-panel__camera"
          type="button"
          :disabled="disabled"
          @click="$emit('request-camera')"
        >
          <el-icon :size="20"><Camera /></el-icon>
          打开摄像头
        </button>
        <p class="sf-source-panel__hint">仅在授权后访问摄像头；拒绝权限时会显示恢复步骤。</p>
      </template>

      <label v-else class="sf-source-panel__upload" :class="{ 'is-disabled': disabled }">
        <input
          type="file"
          :accept="mode === 'image' ? 'image/png,image/jpeg,image/webp' : 'video/mp4,video/webm,video/quicktime'"
          :disabled="disabled"
          @change="chooseFile"
        />
        <el-icon :size="24"><UploadFilled /></el-icon>
        <strong>{{ mode === 'image' ? '上传手语图片' : '上传手语视频' }}</strong>
        <span>{{ mode === 'image' ? 'PNG、JPG、WebP，最大 20MB' : 'MP4、WebM、MOV，最大 500MB' }}</span>
      </label>
    </div>

    <div class="sf-source-panel__section">
      <h3>官方样例</h3>
      <div class="sf-source-panel__samples">
        <button
          v-for="sample in officialSamples"
          :key="sample.id"
          type="button"
          :class="{ 'is-selected': source?.sampleId === sample.id }"
          :disabled="disabled"
          @click="chooseSample(sample)"
        >
          <img :src="sample.image" alt="" />
          <span><strong>{{ sample.name }}</strong><small>{{ sample.meta }}</small></span>
          <i aria-hidden="true" />
        </button>
      </div>
    </div>

    <div class="sf-source-panel__section">
      <h3>识别预设</h3>
      <div class="sf-source-panel__presets">
        <label v-for="item in presets" :key="item.id" :class="{ 'is-selected': preset === item.id }">
          <input
            type="radio"
            name="detection-preset"
            :value="item.id"
            :checked="preset === item.id"
            :disabled="disabled"
            @change="$emit('update:preset', item.id)"
          />
          <span><strong>{{ item.name }}</strong><small>{{ item.description }}</small></span>
        </label>
      </div>
    </div>

    <button
      class="sf-source-panel__advanced"
      data-testid="open-advanced"
      type="button"
      :disabled="disabled"
      @click="$emit('open-advanced')"
    >
      <el-icon><Setting /></el-icon>
      <span>高级设置</span>
      <small>{{ models.find((item) => item.id === modelId)?.version || '默认模型' }}</small>
    </button>
  </aside>
</template>

<style scoped>
.sf-source-panel {
  align-self: start;
  overflow: hidden;
}

.sf-source-panel__section { padding: var(--sf-space-5); border-bottom: 1px solid var(--sf-color-border); }
.sf-source-panel__heading { display: flex; align-items: center; justify-content: space-between; }
.sf-source-panel h2,
.sf-source-panel h3 { margin: 0; color: var(--sf-color-text); font-size: var(--sf-text-sm); font-weight: 750; }
.sf-source-panel__heading .el-icon { color: var(--sf-color-text-disabled); }
.sf-source-panel__heading > span { color: var(--sf-color-text-muted); font-size: 10px; }

.sf-source-panel__language { background: linear-gradient(180deg, #fff 0%, #fafaff 100%); }
.sf-source-panel__language-options {
  display: grid;
  margin-top: var(--sf-space-4);
  gap: var(--sf-space-2);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.sf-source-panel__language-options button {
  display: flex;
  min-width: 0;
  min-height: 76px;
  padding: 12px;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  background: #fff;
  color: var(--sf-color-text);
  cursor: pointer;
  text-align: left;
  transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}
.sf-source-panel__language-options button:hover:not(:disabled) {
  border-color: var(--sf-color-primary);
  transform: translateY(-1px);
}
.sf-source-panel__language-options button.is-selected {
  border-color: var(--sf-color-primary);
  background: var(--sf-color-primary-soft);
  box-shadow: 0 0 0 2px rgb(91 87 216 / 10%);
}
.sf-source-panel__language-options button:disabled { cursor: not-allowed; opacity: 0.6; }
.sf-source-panel__language-options span { display: grid; min-width: 0; gap: 4px; }
.sf-source-panel__language-options strong { font-size: var(--sf-text-xs); font-weight: 750; }
.sf-source-panel__language-options small {
  color: var(--sf-color-text-muted);
  font-size: 9px;
  line-height: 1.35;
}
.sf-source-panel__language-options b {
  padding: 2px 5px;
  border-radius: 5px;
  background: rgb(91 87 216 / 9%);
  color: var(--sf-color-primary);
  font-size: 9px;
  letter-spacing: 0.04em;
}

.sf-source-panel__camera,
.sf-source-panel__upload {
  display: flex;
  width: 100%;
  min-height: 96px;
  margin-top: var(--sf-space-4);
  align-items: center;
  justify-content: center;
  gap: var(--sf-space-2);
  border: 1px dashed #b6b6ec;
  border-radius: var(--sf-radius-control);
  background: var(--sf-color-primary-soft);
  color: var(--sf-color-primary);
  cursor: pointer;
  font-size: var(--sf-text-sm);
  font-weight: 750;
}

.sf-source-panel__camera { min-height: 48px; }
.sf-source-panel__upload { flex-direction: column; text-align: center; }
.sf-source-panel__upload input { position: absolute; width: 1px; height: 1px; opacity: 0; }
.sf-source-panel__upload span { color: var(--sf-color-text-muted); font-size: 10px; font-weight: 500; }
.sf-source-panel__upload:hover,
.sf-source-panel__camera:hover { border-color: var(--sf-color-primary); background: #e5e5fb; }
.sf-source-panel__camera:disabled,
.sf-source-panel__upload.is-disabled { cursor: not-allowed; opacity: 0.6; }

.sf-source-panel__hint { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: 10px; line-height: 1.5; }
.sf-source-panel__samples,
.sf-source-panel__presets { display: grid; margin-top: var(--sf-space-3); gap: var(--sf-space-2); }

.sf-source-panel__samples button {
  display: grid;
  min-height: 54px;
  padding: 6px;
  align-items: center;
  grid-template-columns: 48px 1fr 10px;
  gap: var(--sf-space-2);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-sm);
  background: white;
  color: var(--sf-color-text-secondary);
  cursor: pointer;
  text-align: left;
}

.sf-source-panel__samples button:hover { border-color: #b6b6ec; }
.sf-source-panel__samples button.is-selected { border-color: var(--sf-color-primary); background: var(--sf-color-primary-soft); }
.sf-source-panel__samples img { width: 48px; height: 36px; border-radius: 6px; object-fit: cover; }
.sf-source-panel__samples button span,
.sf-source-panel__presets label span { display: flex; min-width: 0; flex-direction: column; }
.sf-source-panel__samples strong,
.sf-source-panel__presets strong { overflow: hidden; font-size: var(--sf-text-xs); text-overflow: ellipsis; white-space: nowrap; }
.sf-source-panel__samples small,
.sf-source-panel__presets small { margin-top: 2px; color: var(--sf-color-text-muted); font-size: 9px; line-height: 1.45; }
.sf-source-panel__samples i { width: 8px; height: 8px; border: 1px solid var(--sf-color-border-strong); border-radius: 50%; }
.sf-source-panel__samples .is-selected i { border: 2px solid white; background: var(--sf-color-primary); box-shadow: 0 0 0 1px var(--sf-color-primary); }

.sf-source-panel__presets label {
  display: flex;
  min-height: 58px;
  padding: var(--sf-space-3);
  align-items: flex-start;
  gap: var(--sf-space-3);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-sm);
  cursor: pointer;
}

.sf-source-panel__presets label.is-selected { border-color: var(--sf-color-primary); background: var(--sf-color-primary-soft); }
.sf-source-panel__presets input { margin-top: 3px; accent-color: var(--sf-color-primary); }

.sf-source-panel__advanced {
  display: grid;
  width: 100%;
  min-height: 52px;
  padding: 0 var(--sf-space-5);
  align-items: center;
  grid-template-columns: auto 1fr auto;
  gap: var(--sf-space-3);
  border: 0;
  background: white;
  color: var(--sf-color-text-secondary);
  cursor: pointer;
  text-align: left;
}

.sf-source-panel__advanced:hover { background: var(--sf-color-surface-subtle); }
.sf-source-panel__advanced span { font-size: var(--sf-text-xs); font-weight: 750; }
.sf-source-panel__advanced small { color: var(--sf-color-text-muted); font-size: 9px; }

@media (max-width: 1100px) {
  .sf-source-panel { order: 3; }
}
</style>
