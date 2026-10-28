<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  headingLevel: {
    type: Number,
    default: 1,
    validator: (value) => value >= 1 && value <= 3,
  },
})
</script>

<template>
  <header class="sf-page-header">
    <div class="sf-page-header__copy">
      <component :is="`h${headingLevel}`" class="sf-page-header__title">
        {{ title }}
      </component>
      <p v-if="description" class="sf-page-header__description">
        {{ description }}
      </p>
    </div>
    <div v-if="$slots.actions" class="sf-page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.sf-page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sf-space-6);
  margin-bottom: var(--sf-space-8);
}

.sf-page-header__copy {
  min-width: 0;
}

.sf-page-header__title {
  margin: 0;
  color: var(--sf-color-text);
  font-size: var(--sf-text-2xl);
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.02em;
}

.sf-page-header__description {
  max-width: 720px;
  margin: var(--sf-space-2) 0 0;
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
  line-height: 1.65;
}

.sf-page-header__actions {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: var(--sf-space-3);
}

@media (max-width: 640px) {
  .sf-page-header {
    flex-direction: column;
    gap: var(--sf-space-4);
    margin-bottom: var(--sf-space-6);
  }

  .sf-page-header__actions {
    width: 100%;
  }

  .sf-page-header__actions :deep(.el-button) {
    flex: 1;
  }
}
</style>

