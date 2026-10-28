<script setup>
import { View, ZoomIn } from '@element-plus/icons-vue'

import { serviceScenarios } from '@/data/serviceScenarios'

const props = defineProps({
  scenario: { type: String, default: 'government' },
  largeText: { type: Boolean, default: false },
  highContrast: { type: Boolean, default: false },
})

const emit = defineEmits(['update:scenario', 'update:largeText', 'update:highContrast'])
</script>

<template>
  <section class="sf-context-bar" aria-labelledby="service-context-title">
    <div class="sf-context-bar__intro">
      <span>场景策略</span>
      <div>
        <h2 id="service-context-title">选择服务场景</h2>
        <p>识别结果会结合场景生成可直接使用的沟通建议。</p>
      </div>
    </div>

    <div class="sf-context-bar__scenarios" aria-label="服务场景">
      <button
        v-for="item in serviceScenarios"
        :key="item.id"
        :data-testid="`scenario-${item.id}`"
        :class="{ 'is-active': props.scenario === item.id }"
        type="button"
        :aria-pressed="props.scenario === item.id"
        @click="emit('update:scenario', item.id)"
      >
        <el-icon :size="19"><component :is="item.icon" /></el-icon>
        <span>
          <strong>{{ item.name }}</strong>
          <small>{{ item.caption }}</small>
        </span>
      </button>
    </div>

    <div class="sf-context-bar__accessibility" aria-label="无障碍显示设置">
      <span>辅助显示</span>
      <div>
        <button
          data-testid="toggle-large-text"
          type="button"
          :class="{ 'is-active': props.largeText }"
          :aria-pressed="props.largeText"
          @click="emit('update:largeText', !props.largeText)"
        >
          <el-icon><ZoomIn /></el-icon>大字
        </button>
        <button
          data-testid="toggle-high-contrast"
          type="button"
          :class="{ 'is-active': props.highContrast }"
          :aria-pressed="props.highContrast"
          @click="emit('update:highContrast', !props.highContrast)"
        >
          <el-icon><View /></el-icon>高对比
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sf-context-bar {
  display: grid;
  padding: var(--sf-space-4);
  margin-bottom: var(--sf-space-4);
  align-items: center;
  grid-template-columns: minmax(190px, 0.68fr) minmax(560px, 2fr) auto;
  gap: var(--sf-space-4);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-card);
  background: linear-gradient(110deg, white 0%, #fafaff 58%, #f5f5ff 100%);
  box-shadow: var(--sf-shadow-xs);
}

.sf-context-bar__intro {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: var(--sf-space-3);
}

.sf-context-bar__intro > span {
  display: grid;
  min-width: 54px;
  min-height: 54px;
  padding: 6px;
  place-items: center;
  border-radius: 15px;
  background: var(--sf-color-primary);
  color: white;
  font-size: 9px;
  font-weight: 800;
  line-height: 1.25;
  text-align: center;
}

.sf-context-bar h2 {
  margin: 0;
  font-size: var(--sf-text-sm);
}

.sf-context-bar p {
  margin: 3px 0 0;
  color: var(--sf-color-text-muted);
  font-size: 10px;
  line-height: 1.5;
}

.sf-context-bar__scenarios {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--sf-space-2);
}

.sf-context-bar__scenarios button {
  display: flex;
  min-width: 0;
  min-height: 58px;
  padding: 8px 10px;
  align-items: center;
  gap: 9px;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
  background: white;
  color: var(--sf-color-text-muted);
  cursor: pointer;
  text-align: left;
  transition:
    border-color var(--sf-motion-fast) var(--sf-ease),
    background var(--sf-motion-fast) var(--sf-ease),
    color var(--sf-motion-fast) var(--sf-ease);
}

.sf-context-bar__scenarios button:hover {
  border-color: #b7b7ec;
  color: var(--sf-color-text);
}

.sf-context-bar__scenarios button.is-active {
  border-color: var(--sf-color-primary);
  background: var(--sf-color-primary-soft);
  color: var(--sf-color-primary);
  box-shadow: inset 0 0 0 1px rgb(91 91 214 / 8%);
}

.sf-context-bar__scenarios button > span {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.sf-context-bar__scenarios strong {
  color: var(--sf-color-text);
  font-size: var(--sf-text-xs);
}

.sf-context-bar__scenarios small {
  margin-top: 2px;
  overflow: hidden;
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sf-context-bar__accessibility {
  display: flex;
  min-width: 142px;
  flex-direction: column;
  gap: 6px;
}

.sf-context-bar__accessibility > span {
  color: var(--sf-color-text-muted);
  font-size: 9px;
  font-weight: 750;
  letter-spacing: 0.04em;
}

.sf-context-bar__accessibility > div {
  display: flex;
  gap: 6px;
}

.sf-context-bar__accessibility button {
  display: flex;
  min-height: 34px;
  padding: 0 9px;
  align-items: center;
  gap: 5px;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-sm);
  background: white;
  color: var(--sf-color-text-muted);
  cursor: pointer;
  font-size: 10px;
  font-weight: 700;
}

.sf-context-bar__accessibility button.is-active {
  border-color: var(--sf-color-primary);
  background: var(--sf-color-primary);
  color: white;
}

@media (max-width: 1180px) {
  .sf-context-bar { grid-template-columns: minmax(190px, 0.7fr) minmax(520px, 2fr); }
  .sf-context-bar__accessibility { grid-column: 1 / -1; align-items: center; flex-direction: row; justify-content: flex-end; }
}

@media (max-width: 820px) {
  .sf-context-bar { grid-template-columns: 1fr; }
  .sf-context-bar__scenarios { grid-template-columns: 1fr; }
  .sf-context-bar__scenarios small { white-space: normal; }
  .sf-context-bar__accessibility { grid-column: auto; justify-content: flex-start; }
}
</style>
