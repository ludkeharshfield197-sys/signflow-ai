import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import PreviewStage from '@/components/workbench/PreviewStage.vue'
import ResultInspector from '@/components/workbench/ResultInspector.vue'

const emptyRealResult = {
  id: 'det-camera-empty',
  sentence: '',
  labels: [],
  confidence: null,
  durationMs: 2780,
  model: { id: 1, name: 'SignFlow Base', version: '2.1-local' },
  mode: 'live',
  dataKind: 'real',
  status: 'succeeded',
}

const global = {
  stubs: {
    ElIcon: { template: '<i><slot /></i>' },
  },
}

describe('empty real recognition result', () => {
  it('explains that no action was detected instead of reporting a fake zero confidence', () => {
    const wrapper = mount(ResultInspector, {
      props: {
        status: 'succeeded',
        result: emptyRealResult,
      },
      global,
    })

    expect(wrapper.text()).toContain('未检出可识别的手语动作')
    expect(wrapper.findAll('dd')[0].text()).toBe('—')
    expect(wrapper.text()).not.toContain('0.0%')
  })

  it('does not draw a detection box when the model returned no detection', () => {
    const wrapper = mount(PreviewStage, {
      props: {
        mode: 'live',
        status: 'succeeded',
        result: emptyRealResult,
      },
      global,
    })

    expect(wrapper.find('.sf-preview__detection-box').exists()).toBe(false)
  })
})
