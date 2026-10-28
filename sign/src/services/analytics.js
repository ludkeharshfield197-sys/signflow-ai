import { createDemoAnalytics, createOfficialDemoResult } from '@/data/demoData'
import api from './api'

export async function getAnalytics(range = '7d') {
  try {
    const response = await api.get('/api/v1/analytics/', { params: { range } })
    const payload = response.data?.data || response.data
    if (!Array.isArray(payload?.daily)) throw new Error('INVALID_ANALYTICS_RESPONSE')
    return { ...payload, dataKind: 'live' }
  } catch {
    return { ...createDemoAnalytics(), dataKind: 'demo' }
  }
}

export async function getOverview() {
  try {
    const response = await api.get('/api/v1/overview/')
    const payload = response.data?.data || response.data
    if (!payload?.metrics || !Array.isArray(payload?.recentResults)) {
      throw new Error('INVALID_OVERVIEW_RESPONSE')
    }
    let serviceStatus = 'degraded'
    try {
      const health = await api.get('/health/ready', {
        skipAuth: true,
        skipRefresh: true,
      })
      if (health.data?.status === 'ready') serviceStatus = 'healthy'
    } catch {
      serviceStatus = 'degraded'
    }
    return { ...payload, serviceStatus, dataKind: 'live' }
  } catch {
    const analytics = createDemoAnalytics()
    const result = createOfficialDemoResult()
    return {
      dataKind: 'demo',
      source: analytics.source,
      serviceStatus: 'degraded',
      metrics: {
        completed: 1,
        successRate: 100,
        averageLatencyMs: result.durationMs,
        pending: 0,
      },
      recentResults: [result],
      daily: analytics.daily,
    }
  }
}
