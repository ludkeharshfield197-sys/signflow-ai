<script setup>
import { Camera, Picture, VideoCamera } from '@element-plus/icons-vue'

defineProps({
  modelValue: {
    type: String,
    required: true,
    validator: (value) => ['live', 'image', 'video'].includes(value),
  },
})

defineEmits(['update:modelValue'])

const modes = [
  { id: 'live', label: '实时摄像头', shortLabel: '实时', icon: Camera },
  { id: 'image', label: '图片', shortLabel: '图片', icon: Picture },
  { id: 'video', label: '视频', shortLabel: '视频', icon: VideoCamera },
]
</script>

<template>
  <div class="sf-mode-switcher" role="tablist" aria-label="识别输入模式">
    <button
      v-for="mode in modes"
      :key="mode.id"
      class="sf-mode-switcher__item"
      :class="{ 'is-active': modelValue === mode.id }"
      type="button"
      role="tab"
      :aria-selected="modelValue === mode.id"
      @click="$emit('update:modelValue', mode.id)"
    >
      <el-icon :size="18"><component :is="mode.icon" /></el-icon>
      <span class="sf-mode-switcher__desktop-label">{{ mode.label }}</span>
      <span class="sf-mode-switcher__mobile-label">{{ mode.shortLabel }}</span>
    </button>
  </div>
</template>

<style scoped>
.sf-mode-switcher {
  display: grid;
  width: min(100%, 470px);
  grid-template-columns: repeat(3, 1fr);
  overflow: hidden;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  background: var(--sf-color-surface);
}

.sf-mode-switcher__item {
  display: flex;
  min-height: 44px;
  padding: 0 var(--sf-space-4);
  align-items: center;
  justify-content: center;
  gap: var(--sf-space-2);
  border: 0;
  border-right: 1px solid var(--sf-color-border);
  background: transparent;
  color: var(--sf-color-text-muted);
  cursor: pointer;
  font-size: var(--sf-text-sm);
  font-weight: 700;
  transition:
    color var(--sf-motion-fast) var(--sf-ease),
    background var(--sf-motion-fast) var(--sf-ease);
}

.sf-mode-switcher__item:last-child { border-right: 0; }
.sf-mode-switcher__item:hover { background: var(--sf-color-surface-subtle); color: var(--sf-color-text); }
.sf-mode-switcher__item.is-active { background: var(--sf-color-primary); color: white; }
.sf-mode-switcher__mobile-label { display: none; }

@media (max-width: 520px) {
  .sf-mode-switcher { width: 100%; }
  .sf-mode-switcher__item { padding-inline: var(--sf-space-2); }
  .sf-mode-switcher__desktop-label { display: none; }
  .sf-mode-switcher__mobile-label { display: inline; }
}
</style>

