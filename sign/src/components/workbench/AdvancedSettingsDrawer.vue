<script setup>
import { Close } from '@element-plus/icons-vue'

defineProps({
  open: { type: Boolean, default: false },
  modelId: { type: String, default: '' },
  models: { type: Array, default: () => [] },
  confidence: { type: Number, default: 0.45 },
  iou: { type: Number, default: 0.5 },
})

defineEmits(['close', 'update:modelId', 'update:confidence', 'update:iou'])
</script>

<template>
  <Teleport to="body">
    <div
      v-show="open"
      class="sf-settings-drawer"
      data-testid="advanced-settings"
      role="dialog"
      aria-modal="true"
      aria-labelledby="advanced-settings-title"
    >
      <button class="sf-settings-drawer__backdrop" type="button" aria-label="关闭高级设置" @click="$emit('close')" />
      <aside class="sf-settings-drawer__panel">
        <header>
          <div>
            <h2 id="advanced-settings-title">高级设置</h2>
            <p>仅在需要复现实验或专业调优时修改。</p>
          </div>
          <button class="sf-button-reset" type="button" aria-label="关闭高级设置" @click="$emit('close')">
            <el-icon :size="20"><Close /></el-icon>
          </button>
        </header>

        <div class="sf-settings-drawer__field">
          <label for="advanced-model">模型版本</label>
          <select id="advanced-model" :value="modelId" @change="$emit('update:modelId', $event.target.value)">
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }} {{ model.version }}
            </option>
          </select>
          <small>模型上传、部署与回滚请前往模型中心。</small>
        </div>

        <div class="sf-settings-drawer__field">
          <label for="advanced-confidence">
            置信度阈值 <strong>{{ Number(confidence).toFixed(2) }}</strong>
          </label>
          <input
            id="advanced-confidence"
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            :value="confidence"
            @input="$emit('update:confidence', Number($event.target.value))"
          />
          <small>降低阈值会返回更多候选，也可能增加误检。</small>
        </div>

        <div class="sf-settings-drawer__field">
          <label for="advanced-iou">
            IoU 阈值 <strong>{{ Number(iou).toFixed(2) }}</strong>
          </label>
          <input
            id="advanced-iou"
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            :value="iou"
            @input="$emit('update:iou', Number($event.target.value))"
          />
          <small>控制重叠检测框的合并强度。</small>
        </div>

        <div class="sf-settings-drawer__note">
          更改高级参数只影响当前任务，不会训练或修改模型权重。
        </div>

        <button class="sf-settings-drawer__done" type="button" @click="$emit('close')">完成</button>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.sf-settings-drawer { position: fixed; z-index: 1100; inset: 0; }
.sf-settings-drawer__backdrop { position: absolute; inset: 0; width: 100%; border: 0; background: rgb(11 18 32 / 42%); }
.sf-settings-drawer__panel { position: absolute; inset: 0 0 0 auto; width: min(92vw, 420px); padding: var(--sf-space-6); overflow-y: auto; background: white; box-shadow: var(--sf-shadow-overlay); }
.sf-settings-drawer header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--sf-space-4); }
.sf-settings-drawer header h2 { margin: 0; font-size: var(--sf-text-xl); }
.sf-settings-drawer header p { margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-settings-drawer header button { display: grid; width: 44px; height: 44px; place-items: center; border-radius: var(--sf-radius-control); }
.sf-settings-drawer__field { display: grid; margin-top: var(--sf-space-8); gap: var(--sf-space-3); }
.sf-settings-drawer__field label { display: flex; justify-content: space-between; gap: var(--sf-space-3); color: var(--sf-color-text-secondary); font-size: var(--sf-text-sm); font-weight: 700; }
.sf-settings-drawer__field label strong { font-family: var(--sf-font-mono); color: var(--sf-color-primary); }
.sf-settings-drawer__field select { min-height: 44px; padding: 0 var(--sf-space-3); border: 1px solid var(--sf-color-border-strong); border-radius: var(--sf-radius-control); background: white; color: var(--sf-color-text-secondary); font-size: var(--sf-text-sm); }
.sf-settings-drawer__field input[type="range"] { width: 100%; accent-color: var(--sf-color-primary); }
.sf-settings-drawer__field small { color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.6; }
.sf-settings-drawer__note { padding: var(--sf-space-4); margin-top: var(--sf-space-8); border-radius: var(--sf-radius-control); background: var(--sf-color-info-soft); color: #1d4ed8; font-size: var(--sf-text-xs); line-height: 1.6; }
.sf-settings-drawer__done { width: 100%; min-height: 44px; margin-top: var(--sf-space-8); border: 0; border-radius: var(--sf-radius-control); background: var(--sf-color-primary); color: white; cursor: pointer; font-size: var(--sf-text-sm); font-weight: 750; }

@media (max-width: 640px) {
  .sf-settings-drawer__panel { inset: auto 0 0; width: 100%; max-height: 84vh; border-radius: 18px 18px 0 0; }
}
</style>

