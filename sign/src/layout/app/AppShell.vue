<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { logout as logoutSession } from '@/services/auth'
import { useSession } from '@/services/session'
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
import MobileNavDrawer from './MobileNavDrawer.vue'

const route = useRoute()
const router = useRouter()
const { state } = useSession()

const collapsed = ref(false)
const drawerOpen = ref(false)
let tabletQuery

const title = computed(() => route.meta.title || 'SignFlow AI')
const role = computed(() => state.user?.role || 'user')
const user = computed(() => state.user || { displayName: '演示用户', role: 'user' })

function syncResponsive(event) {
  if (event.matches) collapsed.value = true
  if (!event.matches) drawerOpen.value = false
}

async function logout() {
  await logoutSession().catch(() => {})
  await router.replace({ path: '/auth/login', query: { loggedOut: '1' } })
}

onMounted(() => {
  tabletQuery = window.matchMedia('(max-width: 1279px)')
  syncResponsive(tabletQuery)
  tabletQuery.addEventListener('change', syncResponsive)
})

onBeforeUnmount(() => {
  tabletQuery?.removeEventListener('change', syncResponsive)
})
</script>

<template>
  <div class="sf-app-shell" :class="{ 'sf-app-shell--collapsed': collapsed }">
    <a class="sf-skip-link" href="#main-content">跳到主要内容</a>
    <AppSidebar :role="role" :collapsed="collapsed" @toggle="collapsed = !collapsed" />
    <div class="sf-app-shell__body">
      <AppTopbar :title="title" :user="user" @menu="drawerOpen = true" @logout="logout" />
      <main id="main-content" class="sf-app-shell__content" tabindex="-1">
        <RouterView />
      </main>
    </div>
    <MobileNavDrawer :open="drawerOpen" :role="role" @close="drawerOpen = false" />
  </div>
</template>

<style scoped>
.sf-app-shell {
  min-height: 100vh;
  background: var(--sf-color-bg);
}

.sf-app-shell__body {
  min-width: 0;
  min-height: 100vh;
  margin-left: var(--sf-sidebar-width);
  transition: margin-left var(--sf-motion-base) var(--sf-ease);
}

.sf-app-shell--collapsed .sf-app-shell__body {
  margin-left: var(--sf-sidebar-collapsed-width);
}

.sf-app-shell__content {
  min-width: 0;
  outline: none;
}

.sf-skip-link {
  position: fixed;
  z-index: 2000;
  top: var(--sf-space-3);
  left: var(--sf-space-3);
  padding: var(--sf-space-2) var(--sf-space-4);
  border-radius: var(--sf-radius-control);
  background: var(--sf-color-primary);
  color: white;
  font-size: var(--sf-text-sm);
  font-weight: 700;
  transform: translateY(-160%);
  transition: transform var(--sf-motion-fast) var(--sf-ease);
}

.sf-skip-link:focus { transform: translateY(0); }

@media (max-width: 1023px) {
  .sf-app-shell__body,
  .sf-app-shell--collapsed .sf-app-shell__body {
    margin-left: 0;
  }
}
</style>
