import classroomImage from '@/assets/demo/official-sample-classroom.webp'
import helloImage from '@/assets/demo/official-sample-hello.webp'
import serviceImage from '@/assets/demo/official-sample-service.webp'


export const OFFICIAL_SAMPLE_AUTHORIZATION = 'AI 生成授权素材 · 仅限 SignFlow AI 产品演示'
export const OFFICIAL_SAMPLE_MODEL = {
  id: 'signflow-base-2.1',
  name: 'SignFlow Base',
  version: '2.1',
}

export const officialSamples = [
  {
    id: 'official-hello-01',
    name: '日常问候',
    mode: 'image',
    modeLabel: '图片识别',
    meta: '官方样例 · 4.1 秒',
    image: helloImage,
    sentence: '你好，很高兴认识你。',
    labels: ['你好', '很高兴', '认识', '你'],
    confidences: [0.96, 0.94, 0.92, 0.95],
    inputDurationMs: 4120,
    expectedDuration: '2–4 秒',
    provenance: '使用生成式图像工具为本项目原创制作；无真实人物身份数据。',
    authorization: OFFICIAL_SAMPLE_AUTHORIZATION,
  },
  {
    id: 'official-help-02',
    name: '公共服务求助',
    mode: 'video',
    modeLabel: '视频识别',
    meta: '官方样例 · 5.8 秒',
    image: serviceImage,
    sentence: '您好，我需要服务台帮助。',
    labels: ['您好', '需要', '服务台', '帮助'],
    confidences: [0.94, 0.91, 0.93, 0.92],
    inputDurationMs: 5800,
    expectedDuration: '3–5 秒',
    provenance: '使用生成式图像工具为本项目原创制作；以静态关键帧替代视频用于流程演示。',
    authorization: OFFICIAL_SAMPLE_AUTHORIZATION,
  },
  {
    id: 'official-class-03',
    name: '课堂交流',
    mode: 'live',
    modeLabel: '实时演示',
    meta: '官方样例 · 6.2 秒',
    image: classroomImage,
    sentence: '老师，我想回答这个问题。',
    labels: ['老师', '我', '回答', '问题'],
    confidences: [0.93, 0.95, 0.9, 0.92],
    inputDurationMs: 6200,
    expectedDuration: '3–5 秒',
    provenance: '使用生成式图像工具为本项目原创制作；以预录关键帧替代摄像头用于稳定演示。',
    authorization: OFFICIAL_SAMPLE_AUTHORIZATION,
  },
]

export function getOfficialSample(sampleId) {
  return officialSamples.find((sample) => sample.id === sampleId) || officialSamples[0]
}
