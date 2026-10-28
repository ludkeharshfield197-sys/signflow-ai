import { beforeEach, describe, expect, it, vi } from 'vitest'

import api from '@/services/api'
import {
  confirmResult,
  exportResultFile,
  getResultMedia,
  getResultVersions,
  rerunResult,
} from '@/services/results'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('result traceability service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads protected media as an authenticated blob', async () => {
    const media = new Blob(['gesture'], { type: 'image/jpeg' })
    api.get.mockResolvedValue({ data: media })

    const result = await getResultMedia('det_123')

    expect(api.get).toHaveBeenCalledWith('/api/v1/results/det_123/media/', {
      responseType: 'blob',
    })
    expect(result).toBe(media)
  })

  it('persists confirmation, creates reruns and retrieves comparable revisions', async () => {
    api.post
      .mockResolvedValueOnce({ data: { data: { id: 'det_1', confirmation: { status: 'both_confirmed' } } } })
      .mockResolvedValueOnce({ data: { data: { id: 'det_2', revision: 2 } } })
    api.get.mockResolvedValue({
      data: {
        data: {
          items: [
            { id: 'det_1', revision: 1 },
            { id: 'det_2', revision: 2 },
          ],
        },
      },
    })

    const confirmed = await confirmResult('det_1')
    const rerun = await rerunResult('det_1')
    const versions = await getResultVersions('det_2')

    expect(api.post).toHaveBeenNthCalledWith(1, '/api/v1/results/det_1/confirm/', {})
    expect(api.post).toHaveBeenNthCalledWith(2, '/api/v1/results/det_1/rerun/', {})
    expect(api.get).toHaveBeenCalledWith('/api/v1/results/det_2/versions/')
    expect(confirmed.confirmation.status).toBe('both_confirmed')
    expect(rerun).toEqual({ id: 'det_2', revision: 2 })
    expect(versions.map((item) => item.revision)).toEqual([1, 2])
  })

  it('exports a UTF-8 JSON trace report with a deterministic filename', async () => {
    const createObjectURL = vi.fn(() => 'blob:signflow-result')
    const revokeObjectURL = vi.fn()
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, 'click')
      .mockImplementation(function captureAnchor() {
        this.dataset.exportClicked = 'true'
      })
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL,
      revokeObjectURL,
    })

    exportResultFile({
      id: 'det_1',
      dataKind: 'inference',
      outputText: '你好',
      trace: { inputSha256: 'abc123' },
    })

    const [blob] = createObjectURL.mock.calls[0]
    expect(blob).toBeInstanceOf(Blob)
    expect(blob.type).toBe('application/json;charset=utf-8')
    const report = JSON.parse(await blob.text())
    expect(report.product).toBe('SignFlow AI')
    expect(report.result.trace.inputSha256).toBe('abc123')
    expect(click).toHaveBeenCalledOnce()
    const anchor = click.mock.instances[0]
    expect(anchor.download).toBe('signflow-result-det_1.json')
    expect(anchor.href).toBe('blob:signflow-result')
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:signflow-result')

    click.mockRestore()
    vi.unstubAllGlobals()
  })
})
