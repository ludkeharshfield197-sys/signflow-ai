import { describe, expect, it } from 'vitest'

import { buildCameraWebSocketUrl } from '@/services/camera'


describe('camera websocket transport', () => {
  it('uses a short-lived ticket and never puts the access token in the websocket URL', () => {
    const url = new URL(buildCameraWebSocketUrl({
      ticket: 'signed ticket value',
      sessionId: 'camera-session-01',
      modelId: 41,
      confidence: 0.45,
      iou: 0.5,
      pageLocation: {
        protocol: 'https:',
        host: 'demo.signflow.example',
      },
    }))

    expect(url.protocol).toBe('wss:')
    expect(url.pathname).toBe('/ws/camera/camera-session-01/')
    expect(url.searchParams.get('ticket')).toBe('signed ticket value')
    expect(url.searchParams.get('modelId')).toBe('41')
    expect(url.searchParams.has('access')).toBe(false)
    expect(url.searchParams.has('token')).toBe(false)
  })
})
