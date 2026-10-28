import { computed, reactive } from 'vue'


const LEGACY_STORAGE_KEY = 'signflow.session'

function purgeLegacyStoredSession() {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(LEGACY_STORAGE_KEY)
  window.sessionStorage.removeItem(LEGACY_STORAGE_KEY)
}

purgeLegacyStoredSession()

const state = reactive({
  accessToken: '',
  user: null,
})

export function setSession(payload) {
  state.accessToken = payload.accessToken || payload.access || ''
  state.user = payload.user || null
  purgeLegacyStoredSession()
}

export function clearSession() {
  state.accessToken = ''
  state.user = null
  purgeLegacyStoredSession()
}

export function getSession() {
  return {
    accessToken: state.accessToken,
    user: state.user,
  }
}

export function useSession() {
  return {
    state,
    isAuthenticated: computed(() => Boolean(state.accessToken && state.user)),
    isAdmin: computed(() => ['admin', 'superadmin'].includes(state.user?.role)),
    setSession,
    clearSession,
  }
}

