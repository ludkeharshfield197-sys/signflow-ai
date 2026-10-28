import { demoModel } from '@/data/demoData'
import api from './api'

export async function getModels() {
  try {
    const response = await api.get('/api/v1/models/')
    const payload = response.data?.data || response.data
    if (!Array.isArray(payload) && !Array.isArray(payload?.items)) {
      throw new Error('INVALID_MODELS_RESPONSE')
    }
    return {
      items: Array.isArray(payload) ? payload : payload.items || [],
      source: 'api',
    }
  } catch {
    return { items: [demoModel], source: 'demo' }
  }
}

export async function getPublicModelMetrics() {
  const response = await api.get('/api/v1/public/model-metrics/', {
    skipAuth: true,
    skipRefresh: true,
  })
  return response.data?.data || response.data
}
