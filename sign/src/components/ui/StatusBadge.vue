<script setup>
defineProps({
  label: { type: String, required: true },
  tone: {
    type: String,
    default: 'neutral',
    validator: (value) => ['neutral', 'success', 'processing', 'warning', 'danger'].includes(value),
  },
  pulse: { type: Boolean, default: false },
})
</script>

<template>
  <span class="sf-status" :data-tone="tone" role="status">
    <span class="sf-status__dot" :class="{ 'sf-status__dot--pulse': pulse }" aria-hidden="true" />
    <span>{{ label }}</span>
  </span>
</template>

<style scoped>
.sf-status {
  --status-color: var(--sf-color-text-muted);
  --status-bg: var(--sf-color-surface-subtle);
  display: inline-flex;
  align-items: center;
  gap: 7px;
  width: fit-content;
  min-height: 26px;
  padding: 3px 9px;
  border-radius: var(--sf-radius-round);
  background: var(--status-bg);
  color: var(--status-color);
  font-size: var(--sf-text-xs);
  font-weight: 700;
  line-height: 1.3;
}

.sf-status[data-tone="success"] {
  --status-color: var(--sf-color-accent);
  --status-bg: var(--sf-color-accent-soft);
}

.sf-status[data-tone="processing"] {
  --status-color: var(--sf-color-primary);
  --status-bg: var(--sf-color-primary-soft);
}

.sf-status[data-tone="warning"] {
  --status-color: var(--sf-color-warning);
  --status-bg: var(--sf-color-warning-soft);
}

.sf-status[data-tone="danger"] {
  --status-color: var(--sf-color-danger);
  --status-bg: var(--sf-color-danger-soft);
}

.sf-status__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.sf-status__dot--pulse {
  animation: sf-status-pulse 1.8s ease-out infinite;
}

@keyframes sf-status-pulse {
  0% { box-shadow: 0 0 0 0 currentColor; }
  70% { box-shadow: 0 0 0 5px transparent; }
  100% { box-shadow: 0 0 0 0 transparent; }
}

@media (prefers-reduced-motion: reduce) {
  .sf-status__dot--pulse { animation: none; }
}
</style>

