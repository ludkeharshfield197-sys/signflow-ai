import { apiRequest } from './request.js'
import { clearSession, saveLoginSession } from './session.js'

export async function login(credentials) {
  const data = await apiRequest('/api/v1/auth/login/', {
    method: 'POST',
    data: credentials,
    skipAuth: true,
  })
  if (!data?.access || !data?.refresh || !data?.user?.username) {
    throw new Error('登录响应不完整。')
  }
  saveLoginSession(data)
  return data.user
}

export function registerAccount(payload) {
  return apiRequest('/api/v1/auth/register/', {
    method: 'POST',
    data: payload,
    skipAuth: true,
  })
}

export async function logout() {
  try {
    await apiRequest('/api/v1/auth/logout/', { method: 'POST' })
  } finally {
    clearSession()
  }
}
