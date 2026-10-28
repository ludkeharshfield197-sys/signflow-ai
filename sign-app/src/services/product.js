import { apiRequest, downloadProtectedFile } from './request.js'

export function getHealth() {
  return apiRequest('/health/ready', { skipAuth: true })
}

export function getOverview() {
  return apiRequest('/api/v1/overview/')
}

export async function getModels() {
  const data = await apiRequest('/api/v1/models/')
  return data?.items || []
}

export function getResults({ page = 1, pageSize = 20, mode = 'all' } = {}) {
  const query = [
    `page=${encodeURIComponent(page)}`,
    `pageSize=${encodeURIComponent(pageSize)}`,
    `mode=${encodeURIComponent(mode)}`,
  ].join('&')
  return apiRequest(`/api/v1/results/?${query}`)
}

export function getResult(resultId) {
  return apiRequest(`/api/v1/results/${encodeURIComponent(resultId)}/`)
}

export function getResultVersions(resultId) {
  return apiRequest(`/api/v1/results/${encodeURIComponent(resultId)}/versions/`)
}

export function confirmResult(resultId) {
  return apiRequest(`/api/v1/results/${encodeURIComponent(resultId)}/confirm/`, {
    method: 'POST',
  })
}

export function rerunResult(resultId) {
  return apiRequest(`/api/v1/results/${encodeURIComponent(resultId)}/rerun/`, {
    method: 'POST',
  })
}

export function getResultMedia(resultId) {
  return downloadProtectedFile(`/api/v1/results/${encodeURIComponent(resultId)}/media/`)
}
