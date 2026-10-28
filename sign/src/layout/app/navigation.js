import {
  DataAnalysis,
  DataBoard,
  Lock,
  MagicStick,
  Monitor,
  Setting,
  User,
} from '@element-plus/icons-vue'

export const productNavigation = [
  { label: '概览', to: '/app/overview', icon: DataBoard },
  { label: '识别工作台', to: '/app/workbench', icon: MagicStick },
  { label: '结果中心', to: '/app/results', icon: Monitor },
  { label: '数据洞察', to: '/app/analytics', icon: DataAnalysis },
  { label: '模型中心', to: '/app/models', icon: Lock },
  { label: '设置', to: '/app/settings', icon: Setting },
]

export const adminNavigation = [
  { label: '用户管理', to: '/admin/users', icon: User },
  { label: '角色权限', to: '/admin/roles', icon: Lock },
  { label: '系统运行', to: '/admin/system', icon: Monitor },
]

export function canAccessAdmin(role) {
  return ['admin', 'superadmin'].includes(role)
}

