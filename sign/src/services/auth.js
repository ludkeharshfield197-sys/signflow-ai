import api from './api'
import { clearSession, getSession, setSession } from './session'

let refreshPromise = null

function normalizeUser(user, roles) {
  const roleText = Array.isArray(roles) ? roles.join(',') : roles || ''
  const role = /super|超级/i.test(roleText)
    ? 'superadmin'
    : /admin|管理/i.test(roleText)
      ? 'admin'
      : user?.role || 'user'

  return {
    id: user?.id,
    username: user?.username,
    displayName: user?.displayName || user?.username || 'SignFlow 用户',
    email: user?.email || '',
    avatar: user?.avatar || '',
    role,
  }
}

export async function login(credentials) {
  const response = await api.post('/api/v1/auth/login/', credentials, {
    skipAuth: true,
    skipRefresh: true,
  })
  const body = response.data?.data || response.data
  const user = normalizeUser(body.user, body.roles)
  const accessToken = body.access || body.token

  if (!accessToken || !user.username) {
    throw new Error('INVALID_AUTH_RESPONSE')
  }

  setSession({ accessToken, user })
  return user
}

export async function registerAccount(payload) {
  const response = await api.post('/api/v1/auth/register/', payload, {
    skipAuth: true,
    skipRefresh: true,
  })
  return response.data?.data || response.data
}

export async function renewSession() {
  refreshPromise ||= api
    .post('/api/v1/auth/refresh/', {}, {
      skipAuth: true,
      skipRefresh: true,
    })
    .then((response) => {
      const body = response.data?.data || response.data
      const user = normalizeUser(body.user, body.roles)
      if (!body.access || !user.username) throw new Error('INVALID_AUTH_RESPONSE')
      setSession({ accessToken: body.access, user })
      return true
    })
    .catch(() => {
      clearSession()
      return false
    })
    .finally(() => {
      refreshPromise = null
    })

  return refreshPromise
}

export async function restoreSession() {
  const current = getSession()
  if (current.accessToken && current.user) return true
  return renewSession()
}

export async function logout() {
  try {
    await api.post('/api/v1/auth/logout/', {}, { skipRefresh: true })
  } finally {
    clearSession()
  }
}
