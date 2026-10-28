<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import PublicFooter from '@/components/marketing/PublicFooter.vue'
import PublicHeader from '@/components/marketing/PublicHeader.vue'
import RecognitionWorkbench from './RecognitionWorkbench.vue'

const route = useRoute()
const initialMode = computed(() => (
  ['live', 'image', 'video'].includes(route.query.mode) ? route.query.mode : 'video'
))
</script>

<template>
  <div class="sf-public-demo">
    <PublicHeader />
    <main>
      <RecognitionWorkbench :initial-mode="initialMode" guest />
    </main>
    <PublicFooter />
  </div>
</template>

<style scoped>
.sf-public-demo { min-height: 100vh; background: var(--sf-color-bg); }
.sf-public-demo main { padding-block: var(--sf-space-6) var(--sf-space-16); }
</style>

