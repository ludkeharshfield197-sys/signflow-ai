import {
  buildCameraSocketUrl,
  createSessionId,
  getServerOrigin,
} from './config.js'
import { apiRequest } from './request.js'

export async function createCameraConnectionOptions({ modelId, confidence, iou }) {
  const data = await apiRequest('/api/v1/camera/tickets/', { method: 'POST' })
  const sessionId = createSessionId()
  return {
    sessionId,
    url: buildCameraSocketUrl({
      serverOrigin: getServerOrigin(),
      sessionId,
      ticket: data.ticket,
      modelId,
      confidence,
      iou,
    }),
  }
}
