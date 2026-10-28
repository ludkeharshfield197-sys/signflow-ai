import { effectScope } from 'vue'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { createCameraSocket } from '@/services/camera'
import { createDetectionJob } from '@/services/detections'
import { useDetectionJob } from '@/composables/useDetectionJob'


vi.mock('@/services/camera', () => ({
  createCameraSocket: vi.fn(),
}))

vi.mock('@/services/detections', () => ({
  cancelDetectionJob: vi.fn(),
  createDetectionJob: vi.fn(),
  getDetectionJob: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  getApiError: vi.fn((error, fallback) => error?.message || fallback),
}))


describe('live camera detection job', () => {
  let scope
  let socket

  beforeEach(() => {
    socket = {
      OPEN: 1,
      readyState: 1,
      send: vi.fn(),
      close: vi.fn(),
      onmessage: null,
      onerror: null,
      onclose: null,
    }
    createCameraSocket.mockResolvedValue({ sessionId: 'camera-session', socket })
  })

  afterEach(() => {
    scope?.stop()
    vi.clearAllMocks()
  })

  it('uses the ticketed websocket path and accepts the persisted session result', async () => {
    scope = effectScope()
    const job = scope.run(() => useDetectionJob())

    await job.start({
      mode: 'live',
      stream: { getVideoTracks: () => [] },
      source: { kind: 'camera', name: '实时摄像头' },
      modelId: 41,
      preset: 'balanced',
      advanced: { confidence: 0.45, iou: 0.5 },
    })
    socket.onmessage({
      data: JSON.stringify({
        type: 'session.ready',
        jobId: 'det-camera-01',
        limits: { maxFps: 5 },
      }),
    })
    socket.onmessage({
      data: JSON.stringify({
        type: 'session.result',
        result: {
          id: 'det-camera-01',
          mode: 'live',
          status: 'succeeded',
          sentence: '你好',
          labels: [],
          confidence: 0.95,
          model: { id: 41, name: 'SignFlow', version: '2.1' },
        },
      }),
    })

    expect(createCameraSocket).toHaveBeenCalledWith({
      modelId: 41,
      confidence: 0.45,
      iou: 0.5,
    })
    expect(createDetectionJob).not.toHaveBeenCalled()
    expect(job.status.value).toBe('succeeded')
    expect(job.jobId.value).toBe('det-camera-01')
    expect(job.result.value.sentence).toBe('你好')
  })
})
