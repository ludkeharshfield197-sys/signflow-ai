import { createOfficialDemoResult } from '@/data/demoData'
import api from './api'

function localResults() {
  try {
    return JSON.parse(window.localStorage.getItem('signflow.savedResults') || '[]')
  } catch {
    return []
  }
}

function normalizePage(payload, page, pageSize) {
  if (Array.isArray(payload)) {
    return { items: payload, page, pageSize, total: payload.length }
  }
  return {
    items: payload.items || [],
    page: payload.page || page,
    pageSize: payload.pageSize || pageSize,
    total: payload.total ?? payload.items?.length ?? 0,
  }
}

export async function getResults(params = {}) {
  const page = Number(params.page || 1)
  const pageSize = Number(params.pageSize || 10)
  try {
    const response = await api.get('/api/v1/results/', { params })
    const payload = response.data?.data || response.data
    if (!Array.isArray(payload) && !Array.isArray(payload?.items)) {
      throw new Error('INVALID_RESULTS_RESPONSE')
    }
    return {
      ...normalizePage(payload, page, pageSize),
      source: 'api',
    }
  } catch {
    let items = [...localResults(), createOfficialDemoResult()]
    const unique = new Map(items.map((item) => [item.id, item]))
    items = [...unique.values()]

    if (params.mode && params.mode !== 'all') items = items.filter((item) => item.mode === params.mode)
    if (params.status && params.status !== 'all') items = items.filter((item) => item.status === params.status)
    if (params.query) {
      const query = String(params.query).toLowerCase()
      items = items.filter((item) => (
        item.sentence?.toLowerCase().includes(query) ||
        item.sourceName?.toLowerCase().includes(query) ||
        item.id?.toLowerCase().includes(query)
      ))
    }

    items.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    const start = (page - 1) * pageSize
    return {
      items: items.slice(start, start + pageSize),
      page,
      pageSize,
      total: items.length,
      source: 'demo',
    }
  }
}

export async function getResult(resultId) {
  try {
    const response = await api.get(`/api/v1/results/${resultId}/`)
    const item = response.data?.data || response.data
    if (!item?.id || !item?.model) throw new Error('INVALID_RESULT_RESPONSE')
    return { item, source: 'api' }
  } catch {
    const item = [...localResults(), createOfficialDemoResult()].find((result) => result.id === resultId)
    if (!item) throw new Error('RESULT_NOT_FOUND')
    return { item, source: 'demo' }
  }
}

export async function getResultMedia(resultId) {
  const response = await api.get(`/api/v1/results/${resultId}/media/`, {
    responseType: 'blob',
  })
  return response.data
}

export async function confirmResult(resultId) {
  const response = await api.post(`/api/v1/results/${resultId}/confirm/`, {})
  return response.data?.data || response.data
}

export async function rerunResult(resultId) {
  const response = await api.post(`/api/v1/results/${resultId}/rerun/`, {})
  return response.data?.data || response.data
}

export async function getResultVersions(resultId) {
  const response = await api.get(`/api/v1/results/${resultId}/versions/`)
  const payload = response.data?.data || response.data
  return payload?.items || []
}

export function exportResultFile(result) {
  const report = {
    product: 'SignFlow AI',
    exportedAt: new Date().toISOString(),
    dataKind: result.dataKind,
    disclaimer: result.dataKind === 'demo'
      ? '本报告来自官方样例演示，不代表公开模型准确率。'
      : '本报告来自真实识别任务。',
    result,
  }
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(report, null, 2)], { type: 'application/json;charset=utf-8' }),
  )
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `signflow-result-${result.id}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}
