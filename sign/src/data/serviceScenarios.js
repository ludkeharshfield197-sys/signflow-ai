import { FirstAidKit, OfficeBuilding, Reading } from '@element-plus/icons-vue'

export const serviceScenarios = [
  {
    id: 'government',
    name: '政务服务',
    icon: OfficeBuilding,
    caption: '窗口咨询、材料办理与公共事务沟通',
    assistantTitle: '政务服务沟通建议',
    guidance: '请复述识别结果，并确认办理事项、所需材料与是否需要无障碍人工协助。',
    rephrasePrompt: '请放慢动作并面向摄像头重新表达，我们会再次确认办理诉求。',
    assistanceLabel: '政务无障碍协助卡',
  },
  {
    id: 'medical',
    name: '医疗导诊',
    icon: FirstAidKit,
    caption: '预检分诊、科室引导与就医信息确认',
    assistantTitle: '医疗导诊沟通建议',
    guidance: '请先确认是否需要急诊、导诊或无障碍人工协助；识别结果仅用于沟通辅助。',
    rephrasePrompt: '请放慢动作并面向摄像头重新表达，我们会再次确认识别结果。',
    assistanceLabel: '医疗导诊协助卡',
  },
  {
    id: 'education',
    name: '特殊教育',
    icon: Reading,
    caption: '课堂互动、手语练习与学习反馈',
    assistantTitle: '特殊教育沟通建议',
    guidance: '请结合课堂语境确认识别含义，并将结果朗读或复制给教师进行双向确认。',
    rephrasePrompt: '请放慢动作并面向摄像头重新表达，教师会结合课堂语境再次确认。',
    assistanceLabel: '课堂沟通协助卡',
  },
]

export function getServiceScenario(id) {
  return serviceScenarios.find((item) => item.id === id) || serviceScenarios[0]
}
