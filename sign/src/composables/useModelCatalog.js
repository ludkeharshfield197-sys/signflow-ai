import { computed, onMounted, ref } from 'vue'

import api from '@/services/api'

export const detectionPresets = [
  {
    id: 'balanced',
    name: '标准',
    description: '平衡精度与速度，推荐使用',
    confidence: 0.45,
    iou: 0.5,
  },
  {
    id: 'quality',
    name: '高精度',
    description: '提高识别稳定性，处理较慢',
    confidence: 0.35,
    iou: 0.6,
  },
  {
    id: 'speed',
    name: '低延迟',
    description: '优先响应速度，适合实时场景',
    confidence: 0.55,
    iou: 0.4,
  },
]

export function useModelCatalog() {
  const models = ref([])
  const loading = ref(false)
  const source = ref('loading')

  async function load() {
    loading.value = true
    try {
      const response = await api.get('/api/v1/models/', { timeout: 5000 })
      const payload = response.data?.data ?? response.data
      const items = Array.isArray(payload) ? payload : payload?.items
      models.value = (Array.isArray(items) ? items : [])
        .filter((item) => item?.id != null && item.status !== 'inactive')
        .map((item) => ({ ...item, id: String(item.id) }))
      source.value = models.value.length ? 'api' : 'unavailable'
    } catch {
      models.value = []
      source.value = 'unavailable'
    } finally {
      loading.value = false
    }
  }

  onMounted(load)

  return {
    models,
    loading,
    source,
    defaultModelId: computed(() => models.value[0]?.id || ''),
    presets: detectionPresets,
    reload: load,
  }
}
