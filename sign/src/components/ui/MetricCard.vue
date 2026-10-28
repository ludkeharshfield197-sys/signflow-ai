<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  helper: { type: String, default: '' },
  trend: { type: String, default: '' },
  source: { type: String, default: '' },
  tone: {
    type: String,
    default: 'neutral',
    validator: (value) => ['neutral', 'positive', 'warning', 'danger'].includes(value),
  },
})
</script>

<template>
  <article class="sf-metric" :data-tone="tone">
    <div class="sf-metric__topline">
      <span class="sf-metric__label">{{ label }}</span>
      <slot name="icon" />
    </div>
    <div class="sf-metric__value">{{ value }}</div>
    <div v-if="helper || trend" class="sf-metric__meta">
      <span v-if="trend" class="sf-metric__trend">{{ trend }}</span>
      <span v-if="helper">{{ helper }}</span>
    </div>
    <div class="sf-metric__source" :class="{ 'is-missing': !source }">
      {{ source || '数据来源未配置' }}
    </div>
  </article>
</template>

<style scoped>
.sf-metric {
  min-width: 0;
  padding: var(--sf-space-5);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-card);
  background: var(--sf-color-surface);
}

.sf-metric__topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sf-space-3);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
  font-weight: 600;
}

.sf-metric__value {
  margin-top: var(--sf-space-3);
  color: var(--sf-color-text);
  font-size: 30px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.sf-metric__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sf-space-2);
  margin-top: var(--sf-space-2);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-xs);
}

.sf-metric__trend {
  color: var(--sf-color-text-secondary);
  font-weight: 700;
}

.sf-metric__source {
  margin-top: var(--sf-space-3);
  color: var(--sf-color-text-disabled);
  font-size: 10px;
  line-height: 1.45;
}

.sf-metric__source.is-missing {
  color: var(--sf-color-warning);
}

.sf-metric[data-tone="positive"] .sf-metric__trend {
  color: var(--sf-color-accent);
}

.sf-metric[data-tone="warning"] .sf-metric__trend {
  color: var(--sf-color-warning);
}

.sf-metric[data-tone="danger"] .sf-metric__trend {
  color: var(--sf-color-danger);
}
</style>
