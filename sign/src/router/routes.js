import AppShell from '@/layout/app/AppShell.vue'

export const routes = [
  {
    path: '/',
    name: 'public-home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '无界手语 SignFlow AI｜多模态手语沟通平台' },
  },
  {
    path: '/home',
    redirect: '/',
  },
  {
    path: '/product-tour',
    name: 'public-product-tour',
    component: () => import('@/views/demo/ProductTour.vue'),
    meta: { title: '产品导览｜无界手语 SignFlow AI' },
  },
  {
    path: '/privacy',
    name: 'public-privacy',
    component: () => import('@/views/system/PrivacyPolicy.vue'),
    meta: { title: '隐私与数据保留｜SignFlow AI' },
  },
  {
    path: '/product-tour/results/:id',
    name: 'public-product-result',
    component: () => import('@/views/results/ResultDetailPage.vue'),
    meta: { title: '样例结果｜SignFlow AI' },
  },
  { path: '/demo', redirect: '/product-tour' },
  {
    path: '/demo/results/:id',
    redirect: (to) => `/product-tour/results/${to.params.id}`,
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录｜SignFlow AI', publicOnly: true },
  },
  {
    path: '/login',
    redirect: '/auth/login',
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册｜SignFlow AI', publicOnly: true },
  },
  {
    path: '/register',
    redirect: '/auth/register',
  },
  {
    path: '/app',
    component: AppShell,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/app/overview' },
      {
        path: 'overview',
        name: 'app-overview',
        component: () => import('@/views/overview/OverviewPage.vue'),
        meta: { title: '概览', requiresAuth: true },
      },
      {
        path: 'workbench',
        name: 'app-workbench',
        component: () => import('@/views/workbench/RecognitionWorkbench.vue'),
        props: (route) => ({
          initialMode: ['live', 'image', 'video'].includes(route.query.mode)
            ? route.query.mode
            : 'live',
        }),
        meta: { title: '识别工作台', requiresAuth: true },
      },
      {
        path: 'results',
        name: 'app-results',
        component: () => import('@/views/results/ResultsPage.vue'),
        meta: { title: '结果中心', requiresAuth: true },
      },
      {
        path: 'results/:id',
        name: 'app-result-detail',
        component: () => import('@/views/results/ResultDetailPage.vue'),
        meta: { title: '结果详情', requiresAuth: true },
      },
      {
        path: 'analytics',
        name: 'app-analytics',
        component: () => import('@/views/analytics/AnalyticsPage.vue'),
        meta: { title: '数据洞察', requiresAuth: true },
      },
      {
        path: 'models',
        name: 'app-models',
        component: () => import('@/views/models/ModelCatalogPage.vue'),
        meta: { title: '模型中心', requiresAuth: true },
      },
      {
        path: 'team',
        redirect: '/app/settings#team',
      },
      {
        path: 'settings',
        name: 'app-settings',
        component: () => import('@/views/settings/SettingsPage.vue'),
        meta: { title: '设置', requiresAuth: true },
      },
    ],
  },
  {
    path: '/admin',
    component: AppShell,
    meta: { requiresAuth: true, roles: ['admin', 'superadmin'] },
    children: [
      { path: '', redirect: '/admin/users' },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/AdminConsolePage.vue'),
        meta: { title: '用户管理', requiresAuth: true, roles: ['admin', 'superadmin'] },
      },
      {
        path: 'roles',
        name: 'admin-roles',
        component: () => import('@/views/admin/AdminConsolePage.vue'),
        meta: { title: '角色权限', requiresAuth: true, roles: ['admin', 'superadmin'] },
      },
      {
        path: 'system',
        name: 'admin-system',
        component: () => import('@/views/admin/AdminConsolePage.vue'),
        meta: { title: '系统运行', requiresAuth: true, roles: ['admin', 'superadmin'] },
      },
    ],
  },
  { path: '/index', redirect: '/app/overview' },
  { path: '/model', redirect: '/app/models' },
  { path: '/bsns/model', redirect: '/app/models' },
  { path: '/bsns/Image', redirect: '/app/workbench?mode=image' },
  { path: '/bsns/Video', redirect: '/app/workbench?mode=video' },
  { path: '/bsns/camera', redirect: '/app/workbench?mode=live' },
  { path: '/history/:pathMatch(.*)*', redirect: '/app/results' },
  { path: '/sys/user', redirect: '/admin/users' },
  { path: '/sys/role', redirect: '/admin/roles' },
  { path: '/sys/menu', redirect: '/admin/roles' },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/system/NotFoundView.vue'),
    meta: { title: '页面未找到｜SignFlow AI' },
  },
]
