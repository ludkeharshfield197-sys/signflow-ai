<script setup>
import { ArrowRight, Camera, Check, Lock, Picture, VideoCamera } from '@element-plus/icons-vue'
import { computed, nextTick, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import PublicFooter from '@/components/marketing/PublicFooter.vue'
import PublicHeader from '@/components/marketing/PublicHeader.vue'
import {
  getOfficialSample,
  OFFICIAL_SAMPLE_MODEL,
  officialSamples,
} from '@/demo/sample-manifest'
import RecognitionWorkbench from '@/views/workbench/RecognitionWorkbench.vue'

const route = useRoute()
const router = useRouter()
const queryMode = ['image', 'video', 'live'].includes(route.query.mode) ? route.query.mode : 'image'
const activeSample = ref(
  officialSamples.find((sample) => sample.mode === queryMode) || getOfficialSample(),
)
const workbenchKey = ref(0)
const completedResult = ref(null)

const modeIcon = {
  image: Picture,
  video: VideoCamera,
  live: Camera,
}

const buttonLabel = {
  image: '体验图片识别',
  video: '体验视频识别',
  live: '体验实时识别',
}

const scenarioSummary = computed(() => (
  `${activeSample.value.name} · 预期界面耗时 ${activeSample.value.expectedDuration}`
))

async function selectSample(sample) {
  activeSample.value = sample
  completedResult.value = null
  workbenchKey.value += 1
  await nextTick()
  document.querySelector('#product-tour-workbench')?.scrollIntoView({
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    block: 'start',
  })
}

function handleComplete(result) {
  completedResult.value = result
  let existing = []
  try {
    existing = JSON.parse(window.localStorage.getItem('signflow.savedResults') || '[]')
  } catch {
    existing = []
  }
  const unique = existing.filter((item) => item.id !== result.id)
  window.localStorage.setItem('signflow.savedResults', JSON.stringify([result, ...unique].slice(0, 50)))
}

function viewFullResult() {
  if (completedResult.value) {
    router.push(`/product-tour/results/${completedResult.value.id}`)
  }
}
</script>

<template>
  <div class="sf-tour">
    <PublicHeader />

    <main>
      <section class="sf-tour__hero" aria-labelledby="product-tour-title">
        <h1 id="product-tour-title">从识别到确认，<br />完成一轮真实沟通</h1>
        <p>
          无界手语把中英文模型切换、场景化识别、语音朗读、双向确认与本机协助卡
          组织成一条可直接体验的服务工作流。固定结果均标注为官方样例，不替代真实评测。
        </p>
        <div class="sf-tour__proof">
          <span><el-icon><Check /></el-icon>CSL / ASL 双模型</span>
          <span><el-icon><Check /></el-icon>政务 / 医疗 / 教育三场景</span>
          <span><el-icon><Check /></el-icon>图片 / 视频 / 摄像头输入</span>
        </div>
      </section>

      <section class="sf-tour__scenarios" aria-labelledby="scenario-title">
        <header>
          <div>
            <span>01 · 选择输入</span>
            <h2 id="scenario-title">从官方样例快速了解工作流</h2>
          </div>
          <p>选定素材后，继续在工作台选择公共服务场景和手语模型。</p>
        </header>
        <div>
          <article
            v-for="sample in officialSamples"
            :key="sample.id"
            :class="{ 'is-active': activeSample.id === sample.id }"
          >
            <img :src="sample.image" :alt="`${sample.name}官方样例场景`" />
            <div>
              <span><el-icon><component :is="modeIcon[sample.mode]" /></el-icon>{{ sample.modeLabel }}</span>
              <h3>{{ sample.name }}</h3>
              <p>{{ sample.sentence }}</p>
              <button type="button" @click="selectSample(sample)">
                {{ buttonLabel[sample.mode] }}<el-icon><ArrowRight /></el-icon>
              </button>
            </div>
          </article>
        </div>
      </section>

      <section class="sf-tour__trust" aria-label="样例素材与数据说明">
        <div><el-icon><Lock /></el-icon></div>
        <section>
          <strong>AI 生成授权素材</strong>
          <span>{{ activeSample.provenance }}</span>
        </section>
        <dl>
          <div><dt>固定模型</dt><dd>{{ OFFICIAL_SAMPLE_MODEL.name }} {{ OFFICIAL_SAMPLE_MODEL.version }}</dd></div>
          <div><dt>当前场景</dt><dd>{{ scenarioSummary }}</dd></div>
          <div><dt>数据用途</dt><dd>仅用于体验，不进入训练集</dd></div>
        </dl>
      </section>

      <section id="product-tour-workbench" class="sf-tour__workbench" tabindex="-1">
        <div class="sf-tour__step">
          <span>02 · 场景化识别</span>
          <p>选择政务、医疗或特殊教育场景，再完成识别并使用沟通动作。</p>
        </div>
        <RecognitionWorkbench
          :key="workbenchKey"
          :initial-mode="activeSample.mode"
          :initial-sample-id="activeSample.id"
          guest
          @complete="handleComplete"
        />
      </section>

      <section v-if="completedResult" class="sf-tour__complete" aria-live="polite">
        <div><el-icon><Check /></el-icon></div>
        <section>
          <span>03 · 沟通闭环</span>
          <strong>任务已完成，可朗读、复制、生成协助卡，并追溯模型与标签信息。</strong>
        </section>
        <button type="button" @click="viewFullResult">
          查看完整结果<el-icon><ArrowRight /></el-icon>
        </button>
      </section>
    </main>

    <PublicFooter />
  </div>
</template>

<style scoped>
.sf-tour { min-height: 100vh; background: var(--sf-color-bg); }
.sf-tour main { padding-bottom: var(--sf-space-16); }
.sf-tour__hero { position: relative; padding: 88px max(var(--sf-space-8), calc((100vw - 1180px) / 2)) 72px; overflow: hidden; border-bottom: 1px solid var(--sf-color-border); background: radial-gradient(circle at 75% 15%, rgb(91 91 214 / 12%), transparent 34%), linear-gradient(145deg, #fff 0%, #f7f8fc 100%); }
.sf-tour__hero::after { position: absolute; width: 380px; height: 380px; right: -130px; bottom: -240px; border: 1px solid rgb(91 91 214 / 18%); border-radius: 50%; content: ""; }
.sf-tour__eyebrow { display: flex; align-items: center; gap: var(--sf-space-3); }
.sf-tour__eyebrow span { padding: 6px 10px; border-radius: var(--sf-radius-round); background: var(--sf-color-primary-soft); color: var(--sf-color-primary); font-size: 11px; font-weight: 800; }
.sf-tour__eyebrow small { color: var(--sf-color-text-muted); font-size: 10px; }
.sf-tour__hero h1 { max-width: 760px; margin: var(--sf-space-5) 0 0; font-size: clamp(40px, 6vw, 72px); letter-spacing: -0.055em; line-height: 1.02; }
.sf-tour__hero > p { max-width: 720px; margin: var(--sf-space-5) 0 0; color: var(--sf-color-text-secondary); font-size: var(--sf-text-md); line-height: 1.8; }
.sf-tour__proof { display: flex; margin-top: var(--sf-space-6); flex-wrap: wrap; gap: var(--sf-space-3); }
.sf-tour__proof span { display: flex; align-items: center; gap: 7px; color: var(--sf-color-text-secondary); font-size: var(--sf-text-xs); font-weight: 700; }
.sf-tour__proof .el-icon { color: var(--sf-color-accent); }
.sf-tour__scenarios { width: min(calc(100% - 48px), 1180px); margin: 64px auto 0; }
.sf-tour__scenarios > header { display: flex; align-items: end; justify-content: space-between; gap: var(--sf-space-8); }
.sf-tour__scenarios header span,
.sf-tour__step span,
.sf-tour__complete section span { color: var(--sf-color-primary); font-size: 10px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
.sf-tour__scenarios h2 { margin: var(--sf-space-2) 0 0; font-size: var(--sf-text-2xl); }
.sf-tour__scenarios header p { max-width: 400px; margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); text-align: right; }
.sf-tour__scenarios > div { display: grid; margin-top: var(--sf-space-6); grid-template-columns: repeat(3, 1fr); gap: var(--sf-space-4); }
.sf-tour__scenarios article { overflow: hidden; border: 1px solid var(--sf-color-border); border-radius: var(--sf-radius-card); background: white; box-shadow: var(--sf-shadow-card); transition: transform var(--sf-motion-base) var(--sf-ease), border-color var(--sf-motion-base) var(--sf-ease); }
.sf-tour__scenarios article:hover,
.sf-tour__scenarios article.is-active { border-color: #acaceb; transform: translateY(-3px); }
.sf-tour__scenarios article > img { width: 100%; aspect-ratio: 16 / 10; object-fit: cover; }
.sf-tour__scenarios article > div { padding: var(--sf-space-5); }
.sf-tour__scenarios article div > span { display: flex; align-items: center; gap: 6px; color: var(--sf-color-primary); font-size: 10px; font-weight: 750; }
.sf-tour__scenarios h3 { margin: var(--sf-space-3) 0 0; font-size: var(--sf-text-lg); }
.sf-tour__scenarios article p { min-height: 44px; margin: var(--sf-space-2) 0 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); line-height: 1.6; }
.sf-tour__scenarios button,
.sf-tour__complete button { display: flex; min-height: 42px; padding: 0 var(--sf-space-4); margin-top: var(--sf-space-4); align-items: center; justify-content: center; gap: var(--sf-space-2); border: 1px solid var(--sf-color-primary); border-radius: var(--sf-radius-control); background: white; color: var(--sf-color-primary); cursor: pointer; font-size: var(--sf-text-xs); font-weight: 800; }
.sf-tour__scenarios article.is-active button { background: var(--sf-color-primary); color: white; }
.sf-tour__trust { display: grid; width: min(calc(100% - 48px), 1180px); min-height: 116px; padding: var(--sf-space-5); margin: var(--sf-space-5) auto 0; align-items: center; grid-template-columns: 48px minmax(220px, 1fr) minmax(500px, 1.7fr); gap: var(--sf-space-4); border: 1px solid #b8e5dd; border-radius: var(--sf-radius-card); background: var(--sf-color-accent-soft); }
.sf-tour__trust > div { display: grid; width: 48px; height: 48px; place-items: center; border-radius: 13px; background: white; color: var(--sf-color-accent); }
.sf-tour__trust > section { display: flex; flex-direction: column; }
.sf-tour__trust strong { font-size: var(--sf-text-sm); }
.sf-tour__trust section span { margin-top: 4px; color: var(--sf-color-text-muted); font-size: 10px; line-height: 1.5; }
.sf-tour__trust dl { display: grid; margin: 0; grid-template-columns: repeat(3, 1fr); gap: var(--sf-space-3); }
.sf-tour__trust dl div { padding-left: var(--sf-space-4); border-left: 1px solid #b8e5dd; }
.sf-tour__trust dt { color: var(--sf-color-text-muted); font-size: 9px; }
.sf-tour__trust dd { margin: 5px 0 0; color: var(--sf-color-text-secondary); font-size: 10px; font-weight: 700; }
.sf-tour__workbench { scroll-margin-top: 72px; }
.sf-tour__step { display: flex; width: min(calc(100% - 64px), 1516px); padding: var(--sf-space-5) var(--sf-space-8) 0; margin: 56px auto 0; align-items: center; justify-content: space-between; gap: var(--sf-space-6); border-top: 1px solid var(--sf-color-border); }
.sf-tour__step p { margin: 0; color: var(--sf-color-text-muted); font-size: var(--sf-text-xs); }
.sf-tour__complete { position: sticky; z-index: 20; bottom: var(--sf-space-4); display: grid; width: min(calc(100% - 48px), 980px); min-height: 88px; padding: var(--sf-space-4); margin: var(--sf-space-6) auto 0; align-items: center; grid-template-columns: 48px 1fr auto; gap: var(--sf-space-4); border: 1px solid #b8e5dd; border-radius: var(--sf-radius-card); background: rgb(255 255 255 / 94%); box-shadow: var(--sf-shadow-overlay); backdrop-filter: blur(16px); }
.sf-tour__complete > div { display: grid; width: 48px; height: 48px; place-items: center; border-radius: 50%; background: var(--sf-color-accent-soft); color: var(--sf-color-accent); }
.sf-tour__complete section { display: flex; flex-direction: column; gap: 4px; }
.sf-tour__complete section strong { font-size: var(--sf-text-xs); line-height: 1.5; }
.sf-tour__complete button { margin: 0; background: var(--sf-color-primary); color: white; }
@media (max-width: 900px) {
  .sf-tour__scenarios > div { grid-template-columns: 1fr; }
  .sf-tour__scenarios article { display: grid; grid-template-columns: minmax(200px, 0.85fr) 1fr; }
  .sf-tour__trust { grid-template-columns: 48px 1fr; }
  .sf-tour__trust dl { grid-column: 1 / -1; }
}
@media (max-width: 640px) {
  .sf-tour__hero { padding: 64px var(--sf-space-5) 52px; }
  .sf-tour__eyebrow { align-items: flex-start; flex-direction: column; }
  .sf-tour__scenarios { width: calc(100% - 32px); }
  .sf-tour__scenarios > header { align-items: flex-start; flex-direction: column; }
  .sf-tour__scenarios header p { text-align: left; }
  .sf-tour__scenarios article { display: block; }
  .sf-tour__trust { width: calc(100% - 32px); grid-template-columns: 40px 1fr; }
  .sf-tour__trust > div { width: 40px; height: 40px; }
  .sf-tour__trust dl { grid-template-columns: 1fr; }
  .sf-tour__trust dl div { padding: var(--sf-space-2) 0 0; border-top: 1px solid #b8e5dd; border-left: 0; }
  .sf-tour__step { width: calc(100% - 32px); padding-inline: 0; align-items: flex-start; flex-direction: column; }
  .sf-tour__complete { position: static; width: calc(100% - 32px); grid-template-columns: 40px 1fr; }
  .sf-tour__complete button { grid-column: 1 / -1; }
}
@media (prefers-reduced-motion: reduce) {
  .sf-tour__scenarios article { transition: none; }
}
</style>
