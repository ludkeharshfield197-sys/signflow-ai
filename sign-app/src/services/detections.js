import { apiRequest, uploadFile } from './request.js'

export const TERMINAL_STATUSES = new Set([
  'succeeded',
  'failed',
  'timed_out',
  'cancelled',
])

export function isTerminalStatus(status) {
  return TERMINAL_STATUSES.has(status)
}

export function confidencePercent(value) {
  if (value === null || value === undefined || value === '') return '—'
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return '—'
  return `${(numeric * 100).toFixed(1)}%`
}

export function createDetectionJob(
  { filePath, mode, modelId, preset = 'balanced', iou = 0.5, confidence = 0.45 },
  onProgress,
) {
  return uploadFile(
    '/api/v1/detections/jobs/',
    filePath,
    {
      mode,
      modelId: String(modelId),
      preset,
      iou: String(iou),
      confidence: String(confidence),
    },
    onProgress,
  )
}

export function getDetectionJob(jobId) {
  return apiRequest(`/api/v1/detections/jobs/${encodeURIComponent(jobId)}/`)
}

export function cancelDetectionJob(jobId) {
  return apiRequest(`/api/v1/detections/jobs/${encodeURIComponent(jobId)}/cancel/`, {
    method: 'POST',
  })
}

export function saveDetectionJob(jobId) {
  return apiRequest(`/api/v1/detections/jobs/${encodeURIComponent(jobId)}/save/`, {
    method: 'POST',
  })
}

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds))
}

export async function pollDetectionJob(
  jobId,
  { intervalMs = 900, timeoutMs = 5 * 60 * 1000, onUpdate = () => {}, signal } = {},
) {
  const startedAt = Date.now()
  while (Date.now() - startedAt < timeoutMs) {
    if (signal?.cancelled) throw new Error('任务轮询已取消。')
    const job = await getDetectionJob(jobId)
    onUpdate(job)
    if (isTerminalStatus(job.status)) return job
    await delay(intervalMs)
  }
  throw new Error('识别等待超时，请稍后在结果中心查看。')
}
