import { getOfficialSample, OFFICIAL_SAMPLE_MODEL } from '@/demo/sample-manifest'


export function createOfficialDemoResult(overrides = {}) {
  const sample = getOfficialSample(overrides.sampleId)
  const segment = Math.floor(sample.inputDurationMs / sample.labels.length)
  const resultOverrides = { ...overrides }
  delete resultOverrides.sampleId
  return {
    id: 'official-demo-hello',
    sentence: sample.sentence,
    labels: sample.labels.map((text, index) => ({
      text,
      confidence: sample.confidences[index],
      startMs: index * segment,
      endMs: index === sample.labels.length - 1
        ? sample.inputDurationMs
        : (index + 1) * segment,
    })),
    confidence: Number(
      (sample.confidences.reduce((sum, value) => sum + value, 0) / sample.confidences.length)
        .toFixed(3),
    ),
    durationMs: 2640,
    inputDurationMs: sample.inputDurationMs,
    model: OFFICIAL_SAMPLE_MODEL,
    mode: sample.mode,
    sourceName: `${sample.name}官方样例`,
    sampleId: sample.id,
    previewUrl: sample.image,
    dataKind: 'demo',
    status: 'succeeded',
    createdAt: new Date(Date.now() - 12 * 60_000).toISOString(),
    frames: 8,
    preset: 'balanced',
    advanced: { confidence: 0.45, iou: 0.5 },
    authorization: sample.authorization,
    provenance: sample.provenance,
    ...resultOverrides,
  }
}

export function createDemoAnalytics() {
  const today = new Date()
  const daily = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today)
    date.setDate(today.getDate() - (6 - index))
    return {
      date: date.toISOString().slice(5, 10),
      tasks: [1, 2, 1, 3, 2, 4, 3][index],
      latencyMs: [2840, 2710, 2660, 2780, 2590, 2640, 2610][index],
      successRate: [100, 100, 100, 100, 100, 100, 100][index],
    }
  })

  return {
    source: 'SignFlow AI 官方样例演示数据',
    range: '近 7 天（演示）',
    updatedAt: new Date().toISOString(),
    daily,
    modes: [
      { name: '视频', value: 8 },
      { name: '图片', value: 5 },
      { name: '实时', value: 3 },
    ],
    labels: [
      { name: '问候', value: 7 },
      { name: '求助', value: 4 },
      { name: '课堂', value: 3 },
      { name: '其他', value: 2 },
    ],
  }
}

export const demoModel = {
  id: 'signflow-base-2.1',
  name: 'SignFlow Base',
  version: '2.1',
  classes: '由模型服务返回',
  fileSize: '由模型服务返回',
  status: 'demo',
  statusLabel: '演示配置',
  lastUsedAt: new Date(Date.now() - 12 * 60_000).toISOString(),
  metric: {
    value: null,
    name: '验证集 mAP50',
    source: '',
    dataset: '',
    sampleCount: null,
    evaluatedAt: '',
  },
  deployment: '本地演示适配器',
  description: '用于官方样例闭环；连接模型服务后展示真实权重元数据。',
}
