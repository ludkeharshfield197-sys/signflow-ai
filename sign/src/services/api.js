import axios from 'axios'

import { clearSession, getSession } from './session'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30_000,
  withCredentials: true,
  headers: {
    Accept: 'application/json',
  },
})

let refreshPromise = null

function requestId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID()
  return `sf-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

api.interceptors.request.use((config) => {
  const session = getSession()
  config.headers['X-Request-ID'] = config.headers['X-Request-ID'] || requestId()
  if (session.accessToken && !config.skipAuth) {
    config.headers.Authorization = `Bearer ${session.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (
      error.response?.status === 401 &&
      !original?._retried &&
      !original?.skipRefresh
    ) {
      original._retried = true
      refreshPromise ||= import('./auth')
        .then(({ renewSession }) => renewSession())
        .then((renewed) => {
          const accessToken = getSession().accessToken
          if (!renewed || !accessToken) throw new Error('SESSION_REFRESH_FAILED')
          return accessToken
        })
        .finally(() => {
          refreshPromise = null
        })

      try {
        const accessToken = await refreshPromise
        original.headers.Authorization = `Bearer ${accessToken}`
        return api(original)
      } catch {
        clearSession()
      }
    }

    return Promise.reject(error)
  },
)

export function getApiError(error, fallback = '服务暂时不可用，请稍后重试。') {
  const body = error?.response?.data
  if (typeof body?.error?.message === 'string') return body.error.message
  if (typeof body?.message === 'string') return body.message
  if (typeof body?.detail === 'string') return body.detail
  if (typeof body?.info === 'string') return body.info
  if (error?.code === 'ECONNABORTED') return '请求超时，请检查网络后重试。'
  if (!error?.response) return '无法连接识别服务，请确认服务已启动。'
  return fallback
}

export default api
