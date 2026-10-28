const ORIGIN_STORAGE_KEY = 'signflow.serverOrigin'

const envOrigin =
  typeof import.meta !== 'undefined' && import.meta.env
    ? import.meta.env.VITE_SIGNFLOW_API_ORIGIN
    : ''

export const DEFAULT_SERVER_ORIGIN = envOrigin || 'http://127.0.0.1:8001'

export function normalizeServerOrigin(value) {
  const source = String(value || '').trim()
  const match = source.match(/^(https?):\/\/([^/?#\s]+)\/?$/i)
  if (!match || match[2].includes('@')) {
    throw new Error('服务地址应为完整的 http:// 或 https:// 地址，且不能包含路径。')
  }
  return `${match[1].toLowerCase()}://${match[2]}`
}

export function toWebSocketOrigin(serverOrigin) {
  const normalized = normalizeServerOrigin(serverOrigin)
  return normalized.startsWith('https://')
    ? normalized.replace(/^https:/, 'wss:')
    : normalized.replace(/^http:/, 'ws:')
}

export function buildCameraSocketUrl({
  serverOrigin,
  sessionId,
  ticket,
  modelId,
  confidence = 0.45,
  iou = 0.5,
}) {
  const query = [
    `ticket=${encodeURIComponent(ticket)}`,
    `modelId=${encodeURIComponent(String(modelId))}`,
    `confidence=${encodeURIComponent(String(confidence))}`,
    `iou=${encodeURIComponent(String(iou))}`,
  ].join('&')
  return `${toWebSocketOrigin(serverOrigin)}/ws/camera/${encodeURIComponent(sessionId)}/?${query}`
}

export function createSessionId(now = Date.now, random = Math.random) {
  const seed = `${now().toString(16)}${random().toString(16).slice(2)}${random()
    .toString(16)
    .slice(2)}`
    .padEnd(32, '0')
    .slice(0, 32)
  return `${seed.slice(0, 8)}-${seed.slice(8, 12)}-${seed.slice(12, 16)}-${seed.slice(
    16,
    20,
  )}-${seed.slice(20, 32)}`
}

export function getServerOrigin() {
  const stored = uni.getStorageSync(ORIGIN_STORAGE_KEY)
  try {
    return normalizeServerOrigin(stored || DEFAULT_SERVER_ORIGIN)
  } catch {
    return normalizeServerOrigin(DEFAULT_SERVER_ORIGIN)
  }
}

export function saveServerOrigin(value) {
  const normalized = normalizeServerOrigin(value)
  uni.setStorageSync(ORIGIN_STORAGE_KEY, normalized)
  return normalized
}
