import api from './api'


export async function createCameraTicket() {
  const response = await api.post('/api/v1/camera/tickets/')
  return response.data?.data || response.data
}

export function buildCameraWebSocketUrl({
  ticket,
  sessionId,
  modelId,
  confidence,
  iou,
  pageLocation = window.location,
}) {
  const protocol = pageLocation.protocol === 'https:' ? 'wss:' : 'ws:'
  const configuredOrigin = import.meta.env.VITE_CAMERA_WS_ORIGIN
  const base = configuredOrigin || `${protocol}//${pageLocation.host}`
  const url = new URL(`/ws/camera/${encodeURIComponent(sessionId)}/`, base)
  url.protocol = protocol
  url.searchParams.set('ticket', ticket)
  url.searchParams.set('modelId', String(modelId))
  url.searchParams.set('confidence', String(confidence))
  url.searchParams.set('iou', String(iou))
  return url.toString()
}

export async function createCameraSocket({
  modelId,
  confidence,
  iou,
  WebSocketClass = window.WebSocket,
}) {
  const ticket = await createCameraTicket()
  const sessionId = globalThis.crypto?.randomUUID?.() || `camera-${Date.now()}`
  const url = buildCameraWebSocketUrl({
    ticket: ticket.ticket,
    sessionId,
    modelId,
    confidence,
    iou,
  })
  return {
    sessionId,
    socket: new WebSocketClass(url),
  }
}
