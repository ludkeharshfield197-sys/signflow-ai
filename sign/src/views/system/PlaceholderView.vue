<script setup>
import { useRoute } from 'vue-router'

import EmptyState from '@/components/ui/EmptyState.vue'
import PageHeader from '@/components/ui/PageHeader.vue'

const route = useRoute()
</script>

<template>
  <section class="sf-page">
    <PageHeader :title="route.meta.title || 'SignFlow AI'" description="该产品模块正在接入统一商业版体验。" />
    <div class="sf-panel">
      <EmptyState title="模块正在升级" description="页面框架已就绪，业务内容会在本次改造中完成。" />
    </div>
  </section>
</template>

