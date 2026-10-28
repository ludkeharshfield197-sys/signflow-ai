import api from './api'

export async function createDetectionJob(payload, onUploadProgress) {
  const body = new FormData()
  body.append('mode', payload.mode)
  body.append('modelId', payload.modelId)
  body.append('preset', payload.preset)
  body.append('iou', String(payload.advanced.iou))
  body.append('confidence', String(payload.advanced.confidence))
  if (payload.source?.file) body.append('file', payload.source.file)
  if (payload.source?.sampleId) body.append('sampleId', payload.source.sampleId)

  const response = await api.post('/api/v1/detections/jobs/', body, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 5 * 60_000,
    onUploadProgress,
  })
  return response.data?.data || response.data
}

export async function getDetectionJob(jobId) {
  const response = await api.get(`/api/v1/detections/jobs/${jobId}/`)
  return response.data?.data || response.data
}

export async function cancelDetectionJob(jobId) {
  const response = await api.post(`/api/v1/detections/jobs/${jobId}/cancel/`)
  return response.data?.data || response.data
}

export async function saveDetectionResult(jobId) {
  const response = await api.post(`/api/v1/detections/jobs/${jobId}/save/`)
  return response.data?.data || response.data
}

