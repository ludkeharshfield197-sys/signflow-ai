<script setup>
import {
  Camera,
  Check,
  DataLine,
  Lock,
  Picture,
  Right,
  VideoCamera,
} from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'

import DemoPreview from '@/components/marketing/DemoPreview.vue'
import PublicFooter from '@/components/marketing/PublicFooter.vue'
import PublicHeader from '@/components/marketing/PublicHeader.vue'
import api from '@/services/api'

const metrics = ref({
  version: '等待服务连接',
  dataset: '由部署服务返回',
  sampleCount: '—',
  evaluatedAt: '—',
})
const metricsStatus = ref('loading')

onMounted(async () => {
  try {
    const response = await api.get('/api/v1/public/model-metrics/', {
      skipAuth: true,
      skipRefresh: true,
      timeout: 4000,
    })
    metrics.value = { ...metrics.value, ...(response.data?.data || response.data) }
    metricsStatus.value = 'ready'
  } catch {
    metricsStatus.value = 'offline'
  }
})

const capabilities = [
  {
    icon: Picture,
    title: '多模态手语感知',
    description: '统一接入图片、视频与摄像头画面，在同一任务链路中完成真实模型推理。',
  },
  {
    icon: VideoCamera,
    title: '中英文模型切换',
    description: '提供中国手语 CSL 与美国手语 ASL 模型，按服务对象直接切换识别语言。',
  },
  {
    icon: Camera,
    title: '场景化沟通闭环',
    description: '把识别结果转成朗读、复制与协助卡，服务政务、医疗和特殊教育沟通。',
  },
]

const scenarios = [
  { title: '政务服务', description: '面向办事窗口、咨询台与公共事务办理，辅助确认诉求和材料。' },
  { title: '医疗导诊', description: '面向预检分诊与科室引导，提供不替代专业判断的沟通辅助。' },
  { title: '特殊教育', description: '面向课堂互动与手语练习，支持识别结果复核、朗读和复制。' },
]
</script>

<template>
  <div class="sf-landing">
    <PublicHeader />

    <main>
      <section class="sf-hero">
        <div class="sf-hero__copy">
          <h1>让手语沟通自然进入每一次服务</h1>
          <p><strong>无界手语 SignFlow AI</strong> 是一套多模态手语沟通平台，把视觉识别、场景策略与双向确认连接成可复查的服务流程。</p>
          <div class="sf-hero__actions">
            <RouterLink class="sf-hero__primary" to="/product-tour">
              在线体验
              <el-icon><Right /></el-icon>
            </RouterLink>
            <RouterLink class="sf-hero__secondary" to="/auth/login">进入工作台</RouterLink>
          </div>
          <p class="sf-hero__note">
            <el-icon><Lock /></el-icon>
            无需注册即可体验官方样例；上传内容默认不会进入训练集
          </p>
        </div>
        <DemoPreview />
      </section>

      <section class="sf-comparison" aria-labelledby="comparison-title">
        <header class="sf-section-heading">
          <h2 id="comparison-title">识别之后，沟通才真正开始</h2>
          <p>平台把动作检测、文字结果、场景建议和双向确认组织成一条清晰的沟通链路。</p>
        </header>
        <div class="sf-comparison__flow">
          <div>
            <span>输入动作</span>
            <strong>图片 / 视频 / 实时画面</strong>
            <small>中国手语 CSL 与美国手语 ASL 可切换</small>
          </div>
          <el-icon class="sf-comparison__arrow" :size="28"><Right /></el-icon>
          <div class="sf-comparison__result">
            <span>无界手语服务结果</span>
            <strong>我需要服务台帮助。</strong>
            <small><el-icon><Check /></el-icon> 可朗读、可复制、可生成本机协助卡</small>
          </div>
        </div>
      </section>

      <section id="capabilities" class="sf-capabilities">
        <header class="sf-section-heading">
          <h2>一套平台，承接多场景手语沟通</h2>
          <p>视觉模型负责感知，场景策略负责组织下一步动作，产品界面让每一步都可理解、可操作。</p>
        </header>
        <div class="sf-capabilities__list">
          <article v-for="item in capabilities" :key="item.title">
            <div class="sf-capabilities__icon"><el-icon :size="25"><component :is="item.icon" /></el-icon></div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            <RouterLink to="/product-tour">
              查看能力 <el-icon><Right /></el-icon>
            </RouterLink>
          </article>
        </div>
      </section>

      <section class="sf-evidence" aria-labelledby="evidence-title">
        <div class="sf-evidence__copy">
          <h2 id="evidence-title">可信结果，完整保留技术上下文</h2>
          <p>模型版本、验证集、样本量和评测日期由服务端接口返回；服务不可用时保持空缺，不用装饰性数字替代真实证据。</p>
          <RouterLink to="/product-tour">查看可追溯结果 <el-icon><Right /></el-icon></RouterLink>
        </div>
        <dl class="sf-evidence__metrics" :aria-busy="metricsStatus === 'loading'">
          <div>
            <dt>当前部署版本</dt>
            <dd>{{ metrics.version }}</dd>
          </div>
          <div>
            <dt>验证数据集</dt>
            <dd>{{ metrics.dataset }}</dd>
          </div>
          <div>
            <dt>有效样本量</dt>
            <dd>{{ metrics.sampleCount }}</dd>
          </div>
          <div>
            <dt>最近评测日期</dt>
            <dd>{{ metrics.evaluatedAt }}</dd>
          </div>
          <p v-if="metricsStatus === 'offline'">当前未连接评测服务，指标暂不展示。</p>
        </dl>
      </section>

      <section id="security" class="sf-security">
        <div class="sf-security__visual">
          <div class="sf-security__visual-mark"><el-icon :size="34"><Lock /></el-icon></div>
          <div>
            <span>Privacy by design</span>
            <strong>数据策略从识别前就清晰可见</strong>
          </div>
        </div>
        <div class="sf-security__content">
          <h2>隐私优先，能力边界清晰</h2>
          <p>识别内容仅用于生成当前任务结果，不会默认进入训练集。医疗导诊等高风险场景会明确声明结果仅用于沟通辅助。</p>
          <ul>
            <li><el-icon><Check /></el-icon><span>当前部署使用本机推理服务，不把上传内容用于训练</span></li>
            <li><el-icon><Check /></el-icon><span>结果附带模型、置信度、耗时与输入类型</span></li>
            <li><el-icon><Check /></el-icon><span>协助卡只保存在本机，未接入外部人员时明确提示</span></li>
          </ul>
        </div>
      </section>

      <section id="scenarios" class="sf-scenarios">
        <header class="sf-section-heading sf-section-heading--left">
          <h2>面向高频服务场景持续扩展</h2>
          <p>从窗口咨询到医疗导诊与课堂互动，以统一工作流降低手语沟通的服务门槛。</p>
        </header>
        <div class="sf-scenarios__list">
          <article v-for="(item, index) in scenarios" :key="item.title">
            <span>0{{ index + 1 }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
        <div class="sf-scenarios__team">
          <div>
            <el-icon :size="24"><DataLine /></el-icon>
            <strong>可嵌入现有服务流程</strong>
          </div>
          <p>提供识别服务、场景策略、结果追溯与无障碍交互组件；官方样例、真实任务与规划能力保持清晰边界。</p>
          <RouterLink to="/product-tour">查看产品导览 <el-icon><Right /></el-icon></RouterLink>
        </div>
      </section>
    </main>

    <PublicFooter />
  </div>
</template>

<style scoped>
.sf-landing {
  background: var(--sf-color-surface);
  color: var(--sf-color-text);
}

.sf-hero {
  display: grid;
  width: min(100%, 1440px);
  min-height: min(700px, calc(100vh - 72px));
  padding: clamp(64px, 7vw, 96px) var(--sf-space-8);
  margin: 0 auto;
  align-items: center;
  grid-template-columns: minmax(360px, 0.78fr) minmax(600px, 1.45fr);
  gap: clamp(48px, 6vw, 88px);
}

.sf-hero__copy { min-width: 0; }

.sf-hero h1 {
  margin: 0;
  font-size: var(--sf-text-display);
  font-weight: 760;
  line-height: 1.13;
  letter-spacing: -0.055em;
}

.sf-hero__copy > p {
  max-width: 600px;
  margin: var(--sf-space-6) 0 0;
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-md);
  line-height: 1.85;
}

.sf-hero__copy > p strong { color: var(--sf-color-text-secondary); }

.sf-hero__actions {
  display: flex;
  margin-top: var(--sf-space-8);
  flex-wrap: wrap;
  gap: var(--sf-space-3);
}

.sf-hero__primary,
.sf-hero__secondary {
  display: inline-flex;
  min-height: 48px;
  padding: 0 var(--sf-space-6);
  align-items: center;
  justify-content: center;
  gap: var(--sf-space-2);
  border-radius: var(--sf-radius-control);
  font-size: var(--sf-text-sm);
  font-weight: 750;
}

.sf-hero__primary { background: var(--sf-color-primary); color: white; }
.sf-hero__primary:hover { background: var(--sf-color-primary-hover); }
.sf-hero__secondary { border: 1px solid var(--sf-color-primary); color: var(--sf-color-primary); }
.sf-hero__secondary:hover { background: var(--sf-color-primary-soft); }

.sf-hero__copy .sf-hero__note {
  display: flex;
  margin-top: var(--sf-space-5);
  align-items: center;
  gap: var(--sf-space-2);
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-xs);
}

.sf-section-heading {
  max-width: 760px;
  margin: 0 auto var(--sf-space-10);
  text-align: center;
}

.sf-section-heading h2,
.sf-evidence h2,
.sf-security h2 {
  margin: 0;
  font-size: var(--sf-text-3xl);
  line-height: 1.25;
  letter-spacing: -0.04em;
}

.sf-section-heading p,
.sf-evidence__copy > p,
.sf-security__content > p {
  margin: var(--sf-space-4) 0 0;
  color: var(--sf-color-text-muted);
  font-size: var(--sf-text-sm);
  line-height: 1.8;
}

.sf-section-heading--left { margin-inline: 0; text-align: left; }

.sf-comparison,
.sf-capabilities,
.sf-evidence,
.sf-security,
.sf-scenarios {
  padding: var(--sf-space-24) max(var(--sf-space-8), calc((100vw - 1376px) / 2));
}

.sf-comparison { border-block: 1px solid var(--sf-color-border); background: var(--sf-color-bg); }

.sf-comparison__flow {
  display: grid;
  padding: var(--sf-space-8);
  align-items: center;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--sf-space-6);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-card);
  background: var(--sf-color-surface);
}

.sf-comparison__flow > div {
  display: flex;
  min-height: 132px;
  padding: var(--sf-space-5);
  flex-direction: column;
  justify-content: center;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-control);
}

.sf-comparison__flow span { color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-comparison__flow strong { margin-top: var(--sf-space-3); font-size: var(--sf-text-xl); }
.sf-comparison__flow small { display: flex; margin-top: var(--sf-space-3); align-items: center; gap: 6px; color: var(--sf-color-text-muted); }
.sf-comparison__result { border-color: #9bd5cc !important; background: linear-gradient(90deg, white, var(--sf-color-accent-soft)); }
.sf-comparison__result small { color: var(--sf-color-accent); }
.sf-comparison__arrow { color: var(--sf-color-text-disabled); }

.sf-capabilities__list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-block: 1px solid var(--sf-color-border);
}

.sf-capabilities__list article {
  min-width: 0;
  padding: var(--sf-space-8);
  border-right: 1px solid var(--sf-color-border);
}

.sf-capabilities__list article:last-child { border-right: 0; }
.sf-capabilities__icon {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border: 1px solid #c9c9f4;
  border-radius: 13px;
  color: var(--sf-color-primary);
}
.sf-capabilities h3 { margin: var(--sf-space-5) 0 0; font-size: var(--sf-text-lg); }
.sf-capabilities article p { min-height: 52px; margin: var(--sf-space-3) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); line-height: 1.7; }
.sf-capabilities article a,
.sf-evidence__copy a,
.sf-scenarios__team a {
  display: inline-flex;
  margin-top: var(--sf-space-5);
  align-items: center;
  gap: 6px;
  color: var(--sf-color-primary);
  font-size: var(--sf-text-sm);
  font-weight: 750;
}

.sf-evidence {
  display: grid;
  align-items: center;
  grid-template-columns: 0.8fr 1.2fr;
  gap: clamp(48px, 8vw, 120px);
  background: var(--sf-color-bg);
}

.sf-evidence__metrics {
  display: grid;
  padding: var(--sf-space-8);
  margin: 0;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-card);
  background: var(--sf-color-surface);
}

.sf-evidence__metrics div { padding: var(--sf-space-5); border-bottom: 1px solid var(--sf-color-border); }
.sf-evidence__metrics div:nth-child(odd) { border-right: 1px solid var(--sf-color-border); }
.sf-evidence__metrics div:nth-child(n + 3) { border-bottom: 0; }
.sf-evidence__metrics dt { color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-evidence__metrics dd { margin: var(--sf-space-2) 0 0; font-size: var(--sf-text-lg); font-weight: 750; }
.sf-evidence__metrics > p { grid-column: 1 / -1; margin: var(--sf-space-4) var(--sf-space-5) 0; color: var(--sf-color-warning); font-size: var(--sf-text-xs); }

.sf-security {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(48px, 8vw, 120px);
}

.sf-security__visual {
  display: flex;
  min-height: 300px;
  padding: var(--sf-space-10);
  align-items: flex-end;
  gap: var(--sf-space-5);
  border-radius: var(--sf-radius-card);
  background: var(--sf-color-canvas);
  color: white;
}

.sf-security__visual-mark {
  display: grid;
  width: 64px;
  height: 64px;
  flex: 0 0 64px;
  place-items: center;
  border-radius: 18px;
  background: rgb(91 91 214 / 24%);
  color: #aaaaf2;
}
.sf-security__visual span { color: #98a2b3; font-size: var(--sf-text-xs); text-transform: uppercase; letter-spacing: 0.08em; }
.sf-security__visual strong { display: block; margin-top: var(--sf-space-2); font-size: var(--sf-text-xl); }
.sf-security__content { align-self: center; }
.sf-security__content ul { display: grid; padding: 0; margin: var(--sf-space-6) 0 0; gap: var(--sf-space-3); list-style: none; }
.sf-security__content li { display: flex; align-items: center; gap: var(--sf-space-3); color: var(--sf-color-text-secondary); font-size: var(--sf-text-sm); }
.sf-security__content li .el-icon { color: var(--sf-color-accent); }

.sf-scenarios { background: var(--sf-color-bg); }
.sf-scenarios__list { display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--sf-color-border); }
.sf-scenarios__list article { padding: var(--sf-space-8) var(--sf-space-6); border-right: 1px solid var(--sf-color-border); }
.sf-scenarios__list article:last-child { border-right: 0; }
.sf-scenarios__list span { color: var(--sf-color-primary); font-family: var(--sf-font-mono); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-scenarios__list h3 { margin: var(--sf-space-4) 0 0; font-size: var(--sf-text-lg); }
.sf-scenarios__list p { margin: var(--sf-space-3) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); line-height: 1.7; }
.sf-scenarios__team {
  display: grid;
  padding: var(--sf-space-8);
  margin-top: var(--sf-space-12);
  align-items: center;
  grid-template-columns: 0.8fr 1.3fr auto;
  gap: var(--sf-space-8);
  border: 1px solid var(--sf-color-border);
  border-radius: var(--sf-radius-card);
  background: var(--sf-color-surface);
}
.sf-scenarios__team > div { display: flex; align-items: center; gap: var(--sf-space-3); color: var(--sf-color-primary); }
.sf-scenarios__team strong { color: var(--sf-color-text); font-size: var(--sf-text-sm); }
.sf-scenarios__team p { margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-sm); line-height: 1.7; }
.sf-scenarios__team a { margin: 0; white-space: nowrap; }

@media (max-width: 1100px) {
  .sf-hero { min-height: auto; grid-template-columns: 1fr; }
  .sf-hero__copy { max-width: 760px; }
  .sf-evidence,
  .sf-security { grid-template-columns: 1fr; }
  .sf-scenarios__team { grid-template-columns: 1fr; }
}

@media (max-width: 767px) {
  .sf-hero { padding: var(--sf-space-16) var(--sf-space-4); gap: var(--sf-space-12); }
  .sf-hero h1 { font-size: clamp(38px, 12vw, 52px); }
  .sf-hero h1 br { display: none; }
  .sf-hero__actions { display: grid; }
  .sf-comparison,
  .sf-capabilities,
  .sf-evidence,
  .sf-security,
  .sf-scenarios { padding: var(--sf-space-16) var(--sf-space-4); }
  .sf-comparison__flow { grid-template-columns: 1fr; padding: var(--sf-space-4); }
  .sf-comparison__arrow { margin: auto; transform: rotate(90deg); }
  .sf-capabilities__list,
  .sf-scenarios__list { grid-template-columns: 1fr; }
  .sf-capabilities__list article,
  .sf-scenarios__list article { padding-inline: 0; border-right: 0; border-bottom: 1px solid var(--sf-color-border); }
  .sf-capabilities__list article:last-child,
  .sf-scenarios__list article:last-child { border-bottom: 0; }
  .sf-evidence__metrics { grid-template-columns: 1fr; padding: var(--sf-space-4); }
  .sf-evidence__metrics div,
  .sf-evidence__metrics div:nth-child(odd) { border-right: 0; border-bottom: 1px solid var(--sf-color-border); }
  .sf-evidence__metrics div:last-of-type { border-bottom: 0; }
  .sf-security__visual { min-height: 240px; padding: var(--sf-space-6); }
}
</style>
