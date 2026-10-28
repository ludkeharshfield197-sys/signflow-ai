import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ResultInspector from '@/components/workbench/ResultInspector.vue'

const result = {
  id: 'result-1',
  sentence: '我需要帮助',
  confidence: 0.92,
  durationMs: 820,
  mode: 'image',
  dataKind: 'real',
  labels: [{ text: '帮助', confidence: 0.92, startMs: 0 }],
  model: { name: 'SignFlow CSL 37', version: '11n-local' },
}

const global = {
  stubs: {
    ElIcon: { template: '<i><slot /></i>' },
    StatusBadge: { template: '<span />' },
  },
}

describe('result inspector service actions', () => {
  it('turns a recognition result into usable medical-guidance actions', async () => {
    const wrapper = mount(ResultInspector, {
      props: {
        status: 'succeeded',
        result,
        scenarioId: 'medical',
      },
      global,
    })

    expect(wrapper.text()).toContain('医疗导诊沟通建议')
    expect(wrapper.text()).toContain('请先确认是否需要急诊、导诊或无障碍人工协助')

    await wrapper.get('[data-testid="speak-result"]').trigger('click')
    await wrapper.get('[data-testid="copy-result"]').trigger('click')
    await wrapper.get('[data-testid="create-assistance"]').trigger('click')
    await wrapper.get('[data-testid="confirm-result"]').trigger('click')
    await wrapper.get('[data-testid="request-rephrase"]').trigger('click')

    expect(wrapper.emitted('speak')).toEqual([['我需要帮助']])
    expect(wrapper.emitted('copy')).toEqual([['我需要帮助']])
    expect(wrapper.emitted('assist')).toEqual([['medical']])
    expect(wrapper.emitted('confirm')).toEqual([[
      {
        resultId: 'result-1',
        sentence: '我需要帮助',
        scenarioId: 'medical',
      },
    ]])
    expect(wrapper.emitted('rephrase')).toEqual([[
      {
        scenarioId: 'medical',
        prompt: '请放慢动作并面向摄像头重新表达，我们会再次确认识别结果。',
      },
    ]])
  })
})
