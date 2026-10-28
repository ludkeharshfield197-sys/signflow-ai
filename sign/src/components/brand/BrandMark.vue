<script setup>
defineProps({
  compact: { type: Boolean, default: false },
  inverse: { type: Boolean, default: false },
})
</script>

<template>
  <span class="sf-brand" :class="{ 'sf-brand--compact': compact, 'sf-brand--inverse': inverse }">
    <svg class="sf-brand__mark" viewBox="0 0 40 40" aria-hidden="true">
      <path d="M11 18.2V8.8a2.4 2.4 0 0 1 4.8 0v7.1" />
      <path d="M15.8 15.9V6.4a2.4 2.4 0 0 1 4.8 0v9" />
      <path d="M20.6 15.4V7.8a2.4 2.4 0 0 1 4.8 0v9.1" />
      <path d="M25.4 16.9v-5.1a2.4 2.4 0 0 1 4.8 0v10.5c0 7.1-4.5 11.7-11.2 11.7-6.2 0-10.3-3.7-10.3-9.5v-6.3a2.4 2.4 0 0 1 4.8 0v4.4" />
      <path d="m13.5 21.1 3.6-3.7a2.8 2.8 0 0 1 4 4l-4.2 4.2" />
    </svg>
    <span v-if="!compact" class="sf-brand__copy">
      <strong>无界手语 SignFlow AI</strong>
      <small>多模态手语沟通平台</small>
    </span>
  </span>
</template>

<style scoped>
.sf-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--sf-color-text);
}

.sf-brand__mark {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  color: var(--sf-color-primary);
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.2;
}

.sf-brand__copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  line-height: 1.2;
}

.sf-brand__copy strong {
  font-size: 16px;
  font-weight: 750;
  letter-spacing: -0.02em;
  white-space: nowrap;
}

.sf-brand__copy small {
  margin-top: 3px;
  color: var(--sf-color-text-muted);
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.sf-brand--inverse,
.sf-brand--inverse .sf-brand__copy small {
  color: white;
}

.sf-brand--inverse .sf-brand__mark {
  color: #8e8ef0;
}
</style>
