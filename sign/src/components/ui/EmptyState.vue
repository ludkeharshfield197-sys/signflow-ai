<script setup>
const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
})

const emit = defineEmits(['action'])

function activate() {
  if (props.actionLabel) emit('action')
}
</script>

<template>
  <section class="sf-empty" role="status">
    <div v-if="$slots.icon" class="sf-empty__icon" aria-hidden="true">
      <slot name="icon" />
    </div>
    <h3 class="sf-empty__title">{{ title }}</h3>
    <p v-if="description" class="sf-empty__description">{{ description }}</p>
    <button
      v-if="actionLabel"
      class="sf-empty__action"
      type="button"
      @click="activate"
      @keydown.enter.prevent="activate"
      @keydown.space.prevent="activate"
    >
      {{ actionLabel }}
    </button>
  </section>
</template>

<style scoped>
.sf-empty {
  display: flex;
  min-height: 260px;
  padding: var(--sf-space-8);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.sf-empty__icon {
  display: grid;
  width: 52px;
  height: 52px;
  margin-bottom: var(--sf-space-4);
  place-items: center;
  border-radius: 14px;
  background: var(--sf-color-primary-soft);
  color: var(--sf-color-primary);
}

.sf-empty__title {
  margin: 0;
  color: var(--sf-color-text);
  font-size: var(--sf-text-lg);
  font-weight: 700;
}

.sf-empty__description {
  max-width: 440px;
  margin: var(--sf-space-2) 0 0;
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
  line-height: 1.65;
}

.sf-empty__action {
  min-height: 40px;
  margin-top: var(--sf-space-5);
  padding: 0 var(--sf-space-4);
  border: 1px solid var(--sf-color-primary);
  border-radius: var(--sf-radius-control);
  background: var(--sf-color-primary);
  color: white;
  cursor: pointer;
  font-size: var(--sf-text-sm);
  font-weight: 700;
  transition:
    background var(--sf-motion-fast) var(--sf-ease),
    transform var(--sf-motion-fast) var(--sf-ease);
}

.sf-empty__action:hover { background: var(--sf-color-primary-hover); }
.sf-empty__action:active { transform: translateY(1px); }
</style>

