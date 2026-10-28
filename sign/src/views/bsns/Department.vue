<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

// 模拟数据
const mockData = {
  // 手语识别统计
  recognitionStats: {
    daily: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 330, 310, 220, 182, 191, 234, 290, 330, 310, 150, 232, 201, 154, 190, 330, 410],
    weekly: [820, 932, 901, 934, 1290, 1330, 1320, 1450, 1432, 1501, 1334, 1390],
    monthly: [2200, 1932, 2901, 2934, 2290, 3330, 3320, 3400, 2854, 3201, 3521, 3399]
  },
  // 模型性能对比
  modelPerformance: [
    { name: 'YOLOv8n', accuracy: 0.89, speed: 45, size: 6.5 },
    { name: 'YOLOv8s', accuracy: 0.92, speed: 38, size: 12.8 },
    { name: 'YOLOv8m', accuracy: 0.95, speed: 32, size: 25.5 },
    { name: 'YOLOv8l', accuracy: 0.97, speed: 28, size: 43.2 },
    { name: 'YOLOv8x', accuracy: 0.98, speed: 23, size: 68.7 }
  ],
  // 用户活跃度
  userActivity: {
    hours: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    values: [5, 2, 1, 0, 0, 2, 5, 15, 25, 38, 42, 45, 55, 62, 58, 55, 48, 42, 38, 30, 25, 18, 10, 5]
  },
  // 手语类别分布
  signCategories: [
    { value: 235, name: '日常用语' },
    { value: 274, name: '紧急求助' },
    { value: 310, name: '医疗相关' },
    { value: 335, name: '教育场景' },
    { value: 400, name: '工作交流' }
  ],
  // 系统性能监控
  systemPerformance: {
    timestamps: ['12:00', '12:05', '12:10', '12:15', '12:20', '12:25', '12:30', '12:35', '12:40', '12:45', '12:50', '12:55'],
    cpu: [30, 32, 45, 62, 58, 65, 55, 50, 42, 38, 40, 45],
    memory: [45, 48, 50, 55, 60, 65, 68, 70, 72, 70, 65, 60],
    gpu: [20, 25, 40, 70, 85, 90, 85, 75, 60, 50, 40, 35]
  },
  // 地理分布
  geographicDistribution: [
    { name: '北京', value: 235 },
    { name: '上海', value: 274 },
    { name: '广州', value: 310 },
    { name: '深圳', value: 335 },
    { name: '杭州', value: 278 },
    { name: '南京', value: 189 },
    { name: '武汉', value: 235 },
    { name: '成都', value: 305 },
    { name: '重庆', value: 268 },
    { name: '西安', value: 201 }
  ]
}

// 图表实例引用
const charts = ref({})
// 自动刷新定时器
let refreshTimer = null
// 当前时间
const currentTime = ref(new Date().toLocaleString())

// 放大图表相关
const showFullscreen = ref(false)
const currentChartId = ref('')
const currentChartTitle = ref('')
let fullscreenChart = null

// 显示全屏图表
const showFullscreenChart = (chartId, title) => {
  currentChartId.value = chartId
  currentChartTitle.value = title
  showFullscreen.value = true
  
  // 等待DOM更新后初始化全屏图表
  setTimeout(() => {
    const chartOptions = charts.value[chartId].getOption()
    fullscreenChart = echarts.init(document.getElementById('fullscreenChart'))
    fullscreenChart.setOption(chartOptions)
    
    // 监听窗口大小变化
    window.addEventListener('resize', resizeFullscreenChart)
  }, 100)
}

// 关闭全屏图表
const closeFullscreen = () => {
  showFullscreen.value = false
  if (fullscreenChart) {
    window.removeEventListener('resize', resizeFullscreenChart)
    fullscreenChart.dispose()
    fullscreenChart = null
  }
}

// 调整全屏图表大小
const resizeFullscreenChart = () => {
  if (fullscreenChart) {
    fullscreenChart.resize()
  }
}

// 初始化图表
const initCharts = () => {
  // 识别趋势图
  charts.value.recognitionTrend = initChart('recognitionTrendChart', {
    title: { text: '手语识别趋势', left: 'center', textStyle: { color: '#333' } },
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['日识别量', '周识别量', '月识别量'],
      textStyle: { color: '#333' },
      bottom: 10
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: Array.from({ length: 27 }, (_, i) => `${i + 1}日`),
      axisLabel: { color: '#333' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#333' }
    },
    series: [
      {
        name: '日识别量',
        type: 'line',
        stack: '总量',
        data: mockData.recognitionStats.daily,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(80, 141, 255, 0.8)' },
            { offset: 1, color: 'rgba(80, 141, 255, 0.1)' }
          ])
        },
        itemStyle: { color: '#508dff' },
        smooth: true
      },
      {
        name: '周识别量',
        type: 'line',
        stack: '总量',
        data: mockData.recognitionStats.weekly.concat(Array(15).fill(null)),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(36, 174, 145, 0.8)' },
            { offset: 1, color: 'rgba(36, 174, 145, 0.1)' }
          ])
        },
        itemStyle: { color: '#24ae91' },
        smooth: true
      },
      {
        name: '月识别量',
        type: 'line',
        stack: '总量',
        data: mockData.recognitionStats.monthly.concat(Array(15).fill(null)),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 138, 101, 0.8)' },
            { offset: 1, color: 'rgba(255, 138, 101, 0.1)' }
          ])
        },
        itemStyle: { color: '#ff8a65' },
        smooth: true
      }
    ]
  })

  // 模型性能雷达图
  charts.value.modelPerformance = initChart('modelPerformanceChart', {
    title: { text: '模型性能对比', left: 'center', textStyle: { color: '#333' } },
    tooltip: { trigger: 'item' },
    legend: {
      data: mockData.modelPerformance.map(item => item.name),
      textStyle: { color: '#333' },
      bottom: 10
    },
    radar: {
      indicator: [
        { name: '准确率', max: 1 },
        { name: '速度(FPS)', max: 50 },
        { name: '模型大小(MB)', max: 70, inverse: true }
      ],
      splitArea: {
        areaStyle: {
          color: ['rgba(245, 250, 255, 0.2)', 'rgba(235, 245, 255, 0.4)', 
                 'rgba(225, 240, 255, 0.6)', 'rgba(215, 235, 255, 0.8)', 'rgba(205, 230, 255, 1)'],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 10
        }
      },
      axisLine: { lineStyle: { color: 'rgba(120, 140, 180, 0.2)' } },
      splitLine: { lineStyle: { color: 'rgba(120, 140, 180, 0.2)' } }
    },
    series: [{
      type: 'radar',
      data: mockData.modelPerformance.map(item => ({
        value: [item.accuracy, item.speed, item.size],
        name: item.name,
        itemStyle: { color: getModelColor(item.name) },
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
            { offset: 0, color: getModelColorWithOpacity(item.name, 0.6) },
            { offset: 1, color: getModelColorWithOpacity(item.name, 0.1) }
          ])
        }
      }))
    }]
  })

  // 用户活跃度柱状图
  charts.value.userActivity = initChart('userActivityChart', {
    title: { text: '24小时用户活跃度', left: 'center', textStyle: { color: '#333' } },
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: mockData.userActivity.hours.map(h => `${h}:00`),
      axisLabel: { color: '#333' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#333' }
    },
    series: [{
      data: mockData.userActivity.values,
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#5b8ff9' },
          { offset: 1, color: '#5ad8a6' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  })

  // 手语类别饼图
  charts.value.signCategories = initChart('signCategoriesChart', {
    title: { text: '手语类别分布', left: 'center', textStyle: { color: '#333' } },
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#333' }
    },
    series: [{
      name: '手语类别',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: '14', fontWeight: 'bold' }
      },
      labelLine: { show: false },
      data: mockData.signCategories.map(item => ({
        ...item,
        itemStyle: { color: getCategoryColor(item.name) }
      }))
    }]
  })

  // 系统性能监控折线图
  charts.value.systemPerformance = initChart('systemPerformanceChart', {
    title: { text: '系统性能监控', left: 'center', textStyle: { color: '#333' } },
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['CPU使用率', '内存使用率', 'GPU使用率'],
      textStyle: { color: '#333' },
      bottom: 10
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: mockData.systemPerformance.timestamps,
      axisLabel: { color: '#333' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#333', formatter: '{value}%' }
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'line',
        data: mockData.systemPerformance.cpu,
        smooth: true,
        lineStyle: { width: 3, color: '#5b8ff9' },
        itemStyle: { color: '#5b8ff9' },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: '内存使用率',
        type: 'line',
        data: mockData.systemPerformance.memory,
        smooth: true,
        lineStyle: { width: 3, color: '#5ad8a6' },
        itemStyle: { color: '#5ad8a6' },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: 'GPU使用率',
        type: 'line',
        data: mockData.systemPerformance.gpu,
        smooth: true,
        lineStyle: { width: 3, color: '#ff8a65' },
        itemStyle: { color: '#ff8a65' },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  })

  // 地理分布柱状图
  charts.value.geographicDistribution = initChart('geographicDistributionChart', {
    title: { text: '用户地理分布', left: 'center', textStyle: { color: '#333' } },
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: mockData.geographicDistribution.map(item => item.name),
      axisLabel: { color: '#333', interval: 0, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#333' }
    },
    series: [{
      data: mockData.geographicDistribution.map(item => ({
        value: item.value,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#5b8ff9' },
            { offset: 1, color: '#5ad8a6' }
          ])
        }
      })),
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0]
      }
    }]
  })
}

// 初始化单个图表
const initChart = (id, option) => {
  const chartDom = document.getElementById(id)
  const chart = echarts.init(chartDom)
  chart.setOption(option)
  return chart
}

// 获取模型颜色
const getModelColor = (modelName) => {
  const colors = {
    'YOLOv8n': '#5b8ff9',
    'YOLOv8s': '#5ad8a6',
    'YOLOv8m': '#ff8a65',
    'YOLOv8l': '#8d98b3',
    'YOLOv8x': '#e8684a'
  }
  return colors[modelName] || '#5b8ff9'
}

// 获取带透明度的模型颜色
const getModelColorWithOpacity = (modelName, opacity) => {
  const color = getModelColor(modelName)
  return color.replace(')', `, ${opacity})`)
            .replace('rgb', 'rgba')
}

// 获取类别颜色
const getCategoryColor = (category) => {
  const colors = {
    '日常用语': '#5b8ff9',
    '紧急求助': '#5ad8a6',
    '医疗相关': '#ff8a65',
    '教育场景': '#8d98b3',
    '工作交流': '#e8684a'
  }
  return colors[category] || '#5b8ff9'
}

// 更新数据
const updateData = () => {
  // 更新时间
  currentTime.value = new Date().toLocaleString()
  
  // 更新识别趋势数据
  const trendChart = charts.value.recognitionTrend
  if (trendChart) {
    const newDaily = [...mockData.recognitionStats.daily]
    newDaily[newDaily.length - 1] = Math.floor(Math.random() * 200) + 200
    trendChart.setOption({
      series: [{
        data: newDaily
      }]
    })
  }
  
  // 更新系统性能数据
  const perfChart = charts.value.systemPerformance
  if (perfChart) {
    const timestamps = [...mockData.systemPerformance.timestamps]
    const cpu = [...mockData.systemPerformance.cpu]
    const memory = [...mockData.systemPerformance.memory]
    const gpu = [...mockData.systemPerformance.gpu]
    
    // 移除第一个数据点，添加新数据点
    timestamps.shift()
    cpu.shift()
    memory.shift()
    gpu.shift()
    
    const now = new Date()
    timestamps.push(`${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`)
    cpu.push(Math.floor(Math.random() * 30) + 30)
    memory.push(Math.floor(Math.random() * 20) + 50)
    gpu.push(Math.floor(Math.random() * 40) + 30)
    
    // 更新数据
    mockData.systemPerformance.timestamps = timestamps
    mockData.systemPerformance.cpu = cpu
    mockData.systemPerformance.memory = memory
    mockData.systemPerformance.gpu = gpu
    
    perfChart.setOption({
      xAxis: { data: timestamps },
      series: [
        { data: cpu },
        { data: memory },
        { data: gpu }
      ]
    })
  }
}

// 窗口大小变化时调整图表大小
const handleResize = () => {
  Object.values(charts.value).forEach(chart => {
    chart && chart.resize()
  })
}

// 组件挂载时初始化
onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
  
  // 设置定时刷新
  refreshTimer = setInterval(() => {
    updateData()
  }, 5000)
})

// 组件卸载时清理
onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  window.removeEventListener('resize', handleResize)
  Object.values(charts.value).forEach(chart => {
    chart && chart.dispose()
  })
})
</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>手语识别系统数据大屏</h1>
      <div class="dashboard-time">{{ currentTime }}</div>
    </div>
    
    <div class="dashboard-content">
      <div class="row">
        <div class="chart-card large" @click="showFullscreenChart('recognitionTrend', '手语识别趋势')">
          <div id="recognitionTrendChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
        <div class="chart-card" @click="showFullscreenChart('modelPerformance', '模型性能对比')">
          <div id="modelPerformanceChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
      </div>
      
      <div class="row">
        <div class="chart-card" @click="showFullscreenChart('userActivity', '用户活跃度')">
          <div id="userActivityChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
        <div class="chart-card" @click="showFullscreenChart('signCategories', '手语类别分布')">
          <div id="signCategoriesChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
      </div>
      
      <div class="row">
        <div class="chart-card" @click="showFullscreenChart('systemPerformance', '系统性能监控')">
          <div id="systemPerformanceChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
        <div class="chart-card" @click="showFullscreenChart('geographicDistribution', '地理分布')">
          <div id="geographicDistributionChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
      </div>
    </div>
    
    <!-- 全屏图表弹窗 -->
    <div class="fullscreen-modal" v-if="showFullscreen" @click.self="closeFullscreen">
      <div class="fullscreen-content">
        <div class="fullscreen-header">
          <h2>{{ currentChartTitle }}</h2>
          <button class="close-btn" @click="closeFullscreen">×</button>
        </div>
        <div id="fullscreenChart" class="fullscreen-chart"></div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard-container {
  height: 100%;
  width: 100%;
  background-color: #f5f7fa;
  color: #333;
  padding: 20px;
  box-sizing: border-box;
  overflow: auto;
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h1 {
      font-size: 24px;
      color: #333;
      margin: 0;
      font-weight: 600;
    }
    
    .dashboard-time {
      font-size: 16px;
      color: #5b8ff9;
      font-weight: 500;
    }
  }
  
  .dashboard-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
    
    .row {
      display: flex;
      gap: 20px;
      width: 100%;
      
      @media (max-width: 1200px) {
        flex-direction: column;
      }
      
      .chart-card {
        flex: 1;
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        padding: 15px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
        
        &:hover {
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
          transform: translateY(-2px);
          
          .chart-zoom-hint {
            opacity: 1;
          }
        }
        
        &.large {
          flex: 2;
          
          @media (max-width: 1200px) {
            flex: 1;
          }
        }
        
        .chart {
          width: 100%;
          height: 300px;
          
          @media (max-width: 768px) {
            height: 250px;
          }
        }
        
        .chart-zoom-hint {
          position: absolute;
          top: 15px;
          right: 15px;
          background: rgba(255, 255, 255, 0.8);
          padding: 5px 10px;
          border-radius: 4px;
          font-size: 12px;
          color: #5b8ff9;
          opacity: 0;
          transition: opacity 0.3s ease;
          z-index: 1;
        }
      }
    }
  }
  
  .fullscreen-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    
    .fullscreen-content {
      width: 90%;
      height: 90%;
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      
      .fullscreen-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        border-bottom: 1px solid #eee;
        
        h2 {
          margin: 0;
          font-size: 18px;
          color: #333;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          color: #999;
          cursor: pointer;
          transition: color 0.3s;
          
          &:hover {
            color: #333;
          }
        }
      }
      
      .fullscreen-chart {
        flex: 1;
        width: 100%;
        height: calc(100% - 60px);
      }
    }
  }
}
</style>
