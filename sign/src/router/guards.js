import { restoreSession } from '@/services/auth'
import { getSession } from '@/services/session'

export function installRouterGuards(router) {
  router.beforeEach(async (to) => {
    let session = getSession()
    let authenticated = Boolean(session.accessToken && session.user)
    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

    if (!authenticated && requiresAuth) {
      await restoreSession()
      session = getSession()
      authenticated = Boolean(session.accessToken && session.user)
    }
    const roles = to.matched.flatMap((record) => record.meta.roles || [])

    if (requiresAuth && !authenticated) {
      return {
        path: '/auth/login',
        query: { redirect: to.fullPath },
      }
    }

    if (to.meta.publicOnly && authenticated) {
      return '/app/overview'
    }

    if (roles.length && !roles.includes(session.user?.role)) {
      return '/app/overview'
    }

    return true
  })

  router.afterEach((to) => {
    document.title = to.meta.title || 'SignFlow AI'
  })
}
