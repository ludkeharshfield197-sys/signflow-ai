import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useModelCatalog } from '@/composables/useModelCatalog'
import ModelCatalogPage from '@/views/models/ModelCatalogPage.vue'
import api from '@/services/api'

const { getModelsMock } = vi.hoisted(() => ({
  getModelsMock: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

vi.mock('@/services/models', () => ({
  getModels: getModelsMock,
}))

vi.mock('@/services/session', () => ({
  useSession: () => ({ isAdmin: false }),
}))

const deployedModel = {
  id: 1,
  name: 'SignFlow Base',
  version: '2.1-local',
  classes: null,
  fileSize: '6.3 MB',
  status: 'active',
  statusLabel: '可用',
  lastUsedAt: null,
  metric: {
    value: null,
    name: '验证集 mAP50',
    source: '',
    dataset: '',
    sampleCount: null,
    evaluatedAt: '',
  },
  deployment: '本地推理服务',
  description: 'ASL-v8.pt',
}

function mountCatalog() {
  let catalog
  const Probe = defineComponent({
    setup() {
      catalog = useModelCatalog()
      return () => h('div')
    },
  })
  const wrapper = mount(Probe)
  return { catalog, wrapper }
}

describe('model catalog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the deployed model ID from the real product catalog response', async () => {
    api.get.mockResolvedValue({
      data: {
        code: 0,
        message: 'ok',
        data: { items: [deployedModel] },
        requestId: 'req-model-catalog',
      },
    })

    const { catalog, wrapper } = mountCatalog()
    await flushPromises()

    expect(api.get).toHaveBeenCalledWith('/api/v1/models/', { timeout: 5000 })
    expect(catalog.models.value).toEqual([{ ...deployedModel, id: '1' }])
    expect(catalog.defaultModelId.value).toBe('1')
    expect(catalog.source.value).toBe('api')
    wrapper.unmount()
  })

  it('does not expose a fake model ID when the authenticated catalog is unavailable', async () => {
    api.get.mockRejectedValue(new Error('catalog offline'))

    const { catalog, wrapper } = mountCatalog()
    await flushPromises()

    expect(catalog.models.value).toEqual([])
    expect(catalog.defaultModelId.value).toBe('')
    expect(catalog.source.value).toBe('unavailable')
    wrapper.unmount()
  })

  it('renders the complete measured model card and its declared limitations', async () => {
    getModelsMock.mockResolvedValue({
      source: 'api',
      items: [
        {
          ...deployedModel,
          language: '美国手语',
          classes: 80,
          metric: {
            value: '98.9%',
            name: '验证集 mAP50',
            source: '本地 YOLO.val 复测',
            dataset: 'ASL-80 带框保留验证集',
            sampleCount: 2053,
            evaluatedAt: '2026-07-30',
          },
          evaluation: {
            status: 'evaluated',
            metrics: {
              precision: 0.976252,
              recall: 0.988073,
              map50: 0.989351,
              map5095: 0.76944,
            },
            dataset: {
              name: 'ASL-80 带框保留验证集',
              sampleCount: 2053,
              independence: '训练期间使用的验证集，不等同于外部独立盲测',
            },
            performance: {
              averageImageLatencyMs: 83.15,
              videoFps: 11.75,
              hardware: 'Intel Core i7-13700H CPU',
            },
            evaluatedAt: '2026-07-30',
            limitations: ['仅覆盖 80 个 ASL 词汇，不支持开放词汇。'],
          },
        },
      ],
    })

    const wrapper = mount(ModelCatalogPage)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('美国手语')
    expect(text).toContain('Precision')
    expect(text).toContain('97.6%')
    expect(text).toContain('Recall')
    expect(text).toContain('98.8%')
    expect(text).toContain('mAP50-95')
    expect(text).toContain('76.9%')
    expect(text).toContain('83.15 ms')
    expect(text).toContain('11.75 FPS')
    expect(text).toContain('Intel Core i7-13700H CPU')
    expect(text).toContain('训练期间使用的验证集，不等同于外部独立盲测')
    expect(text).toContain('仅覆盖 80 个 ASL 词汇，不支持开放词汇。')
    wrapper.unmount()
  })
})
