<script setup>
import { Compass } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

import BrandMark from '@/components/brand/BrandMark.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const router = useRouter()
</script>

<template>
  <main class="sf-not-found">
    <BrandMark />
    <div class="sf-not-found__panel sf-panel">
      <EmptyState
        title="没有找到这个页面"
        description="链接可能已更新，返回产品首页继续体验 SignFlow AI。"
        action-label="返回首页"
        @action="router.push('/')"
      >
        <template #icon><el-icon :size="28"><Compass /></el-icon></template>
      </EmptyState>
    </div>
  </main>
</template>

<style scoped>
.sf-not-found {
  display: grid;
  min-height: 100vh;
  padding: var(--sf-space-8);
  place-content: center;
  justify-items: center;
  gap: var(--sf-space-8);
}

.sf-not-found__panel { width: min(540px, calc(100vw - 32px)); }
</style>

