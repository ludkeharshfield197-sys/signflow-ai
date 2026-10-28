import { beforeEach, describe, expect, it, vi } from 'vitest'

import { installRouterGuards } from '@/router/guards'
import { clearSession, setSession } from '@/services/session'


const restoreSession = vi.hoisted(() => vi.fn())

vi.mock('@/services/auth', () => ({ restoreSession }))

describe('authenticated router guard', () => {
  beforeEach(() => {
    clearSession()
    restoreSession.mockReset()
  })

  it('restores a cookie-backed session before redirecting to login', async () => {
    let beforeGuard
    const router = {
      beforeEach(callback) {
        beforeGuard = callback
      },
      afterEach() {},
    }
    restoreSession.mockImplementation(async () => {
      setSession({
        accessToken: 'restored-access-token',
        user: { id: 1, username: 'platform_admin', role: 'superadmin' },
      })
      return true
    })
    installRouterGuards(router)

    const result = await beforeGuard({
      fullPath: '/app/overview',
      meta: {},
      matched: [{ meta: { requiresAuth: true } }],
    })

    expect(restoreSession).toHaveBeenCalledOnce()
    expect(result).toBe(true)
  })

  it('does not probe refresh cookies on a public-only authentication page', async () => {
    let beforeGuard
    const router = {
      beforeEach(callback) {
        beforeGuard = callback
      },
      afterEach() {},
    }
    installRouterGuards(router)

    const result = await beforeGuard({
      fullPath: '/auth/login',
      meta: { publicOnly: true },
      matched: [{ meta: { publicOnly: true } }],
    })

    expect(restoreSession).not.toHaveBeenCalled()
    expect(result).toBe(true)
  })
})
