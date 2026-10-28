<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'

// 模拟数据
const mockData = {
  // 3D散点图数据 - 模型性能对比
  modelPerformance3D: (() => {
    const data = []
    const models = ['YOLOv8n', 'YOLOv8s', 'YOLOv8m', 'YOLOv8l', 'YOLOv8x']
    
    // 为每个模型生成多个数据点，表示不同配置下的性能
    models.forEach((model, idx) => {
      // 基础性能值
      const baseAccuracy = 0.75 + idx * 0.05
      const baseSpeed = 50 - idx * 5
      const baseMemory = 5 + idx * 15
      
      // 为每个模型生成10个变种数据点
      for (let i = 0; i < 10; i++) {
        // 添加随机波动
        const accuracy = Math.min(0.99, baseAccuracy + (Math.random() * 0.1 - 0.05))
        const speed = baseSpeed + (Math.random() * 10 - 5)
        const memory = baseMemory + (Math.random() * 8 - 4)
        
        data.push([
          accuracy.toFixed(3),  // 准确率
          speed.toFixed(1),     // 速度 (FPS)
          memory.toFixed(1),    // 内存占用 (MB)
          model,                // 模型名称
          idx                   // 模型索引，用于颜色区分
        ])
      }
    })
    return data
  })(),
  
  // 3D柱状图数据 - 不同场景下的识别准确率
  scenarioAccuracy: (() => {
    const scenarios = ['室内明亮', '室内昏暗', '户外阳光', '户外阴天', '动态背景']
    const signTypes = ['日常用语', '紧急求助', '医疗相关', '教育场景', '工作交流']
    const data = []
    
    scenarios.forEach((scenario, i) => {
      signTypes.forEach((type, j) => {
        // 基础准确率，室内明亮条件下最高
        let baseAccuracy = 0.95
        if (scenario === '室内昏暗') baseAccuracy = 0.85
        if (scenario === '户外阳光') baseAccuracy = 0.80
        if (scenario === '户外阴天') baseAccuracy = 0.88
        if (scenario === '动态背景') baseAccuracy = 0.75
        
        // 不同手语类型的准确率调整
        if (type === '日常用语') baseAccuracy += 0.05
        if (type === '紧急求助') baseAccuracy -= 0.02
        if (type === '医疗相关') baseAccuracy -= 0.03
        
        // 添加随机波动并确保不超过1
        const accuracy = Math.min(0.99, baseAccuracy + (Math.random() * 0.06 - 0.03))
        
        data.push([i, j, accuracy.toFixed(2) * 100])
      })
    })
    return {
      data,
      scenarios,
      signTypes
    }
  })(),
  
  // 3D曲面图数据 - 识别准确率随距离和角度变化
  distanceAngleAccuracy: (() => {
    const data = []
    // 距离范围：0.5米到3米
    for (let distance = 0.5; distance <= 3; distance += 0.1) {
      // 角度范围：-90度到90度
      for (let angle = -90; angle <= 90; angle += 5) {
        // 计算准确率：距离越远、角度越偏离正面，准确率越低
        const distanceFactor = 1 - (distance - 0.5) / 3.5
        const angleFactor = 1 - Math.abs(angle) / 100
        
        // 基础准确率
        let accuracy = 0.95 * distanceFactor * angleFactor
        
        // 添加一些随机波动
        accuracy += (Math.random() * 0.06 - 0.03)
        accuracy = Math.min(0.99, Math.max(0.5, accuracy))
        
        data.push([distance, angle, accuracy])
      }
    }
    return data
  })()
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
  // 3D散点图 - 模型性能对比
  charts.value.modelPerformance3D = initChart('modelPerformance3DChart', {
    title: {
      text: '模型性能3D分析',
      left: 'center',
      textStyle: { color: '#333' }
    },
    tooltip: {},
    legend: {
      data: ['YOLOv8n', 'YOLOv8s', 'YOLOv8m', 'YOLOv8l', 'YOLOv8x'],
      textStyle: { color: '#333' },
      right: 10,
      top: 10
    },
    grid3D: {
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 5,
        distance: 200
      },
      light: {
        main: {
          intensity: 1.2
        },
        ambient: {
          intensity: 0.3
        }
      },
      axisLine: {
        lineStyle: { color: '#999' }
      },
      axisLabel: {
        textStyle: { color: '#333' }
      },
      splitLine: {
        lineStyle: { color: 'rgba(0,0,0,0.1)' }
      }
    },
    xAxis3D: {
      name: '准确率',
      type: 'value',
      min: 0.7,
      max: 1.0
    },
    yAxis3D: {
      name: '速度(FPS)',
      type: 'value'
    },
    zAxis3D: {
      name: '内存占用(MB)',
      type: 'value'
    },
    dataset: {
      source: mockData.modelPerformance3D
    },
    series: [{
      type: 'scatter3D',
      symbolSize: 12,
      encode: {
        x: 0,
        y: 1,
        z: 2,
        tooltip: [3, 0, 1, 2]
      },
      itemStyle: {
        color: function(params) {
          const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'];
          return colors[params.value[4]];
        }
      }
    }]
  })

  // 3D柱状图 - 不同场景下的识别准确率
  charts.value.scenarioAccuracy = initChart('scenarioAccuracyChart', {
    title: {
      text: '不同场景识别准确率',
      left: 'center',
      textStyle: { color: '#333' }
    },
    tooltip: {},
    grid3D: {
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 10,
        distance: 200
      },
      light: {
        main: {
          intensity: 1.2
        },
        ambient: {
          intensity: 0.3
        }
      },
      axisLine: {
        lineStyle: { color: '#999' }
      },
      axisLabel: {
        textStyle: { color: '#333' }
      },
      splitLine: {
        lineStyle: { color: 'rgba(0,0,0,0.1)' }
      }
    },
    xAxis3D: {
      type: 'category',
      data: mockData.scenarioAccuracy.scenarios,
      axisLabel: {
        interval: 0
      }
    },
    yAxis3D: {
      type: 'category',
      data: mockData.scenarioAccuracy.signTypes,
      axisLabel: {
        interval: 0
      }
    },
    zAxis3D: {
      type: 'value',
      name: '准确率(%)'
    },
    series: [{
      type: 'bar3D',
      data: mockData.scenarioAccuracy.data,
      shading: 'lambert',
      itemStyle: {
        color: function(params) {
          // 根据值的大小设置不同的颜色
          const value = params.value[2];
          if (value > 90) return '#91cc75';
          if (value > 80) return '#fac858';
          if (value > 70) return '#ee6666';
          return '#73c0de';
        }
      },
      label: {
        show: false,
        formatter: '{c}%',
        textStyle: {
          color: '#333',
          fontSize: 12,
          borderWidth: 1
        }
      },
      emphasis: {
        label: {
          show: true
        },
        itemStyle: {
          color: '#5470c6'
        }
      }
    }]
  })

  // 3D曲面图 - 识别准确率随距离和角度变化
  charts.value.distanceAngleAccuracy = initChart('distanceAngleAccuracyChart', {
    title: {
      text: '距离与角度对准确率的影响',
      left: 'center',
      textStyle: { color: '#333' }
    },
    tooltip: {},
    grid3D: {
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 10,
        distance: 200
      },
      light: {
        main: {
          intensity: 1.2
        },
        ambient: {
          intensity: 0.3
        }
      },
      axisLine: {
        lineStyle: { color: '#999' }
      },
      axisLabel: {
        textStyle: { color: '#333' }
      },
      splitLine: {
        lineStyle: { color: 'rgba(0,0,0,0.1)' }
      }
    },
    visualMap: {
      show: true,
      dimension: 2,
      min: 0.5,
      max: 1.0,
      inRange: {
        color: ['#ee6666', '#fac858', '#91cc75']
      },
      textStyle: {
        color: '#333'
      }
    },
    xAxis3D: {
      type: 'value',
      name: '距离(米)'
    },
    yAxis3D: {
      type: 'value',
      name: '角度(度)'
    },
    zAxis3D: {
      type: 'value',
      name: '准确率'
    },
    series: [{
      type: 'surface',
      data: mockData.distanceAngleAccuracy,
      shading: 'color',
      wireframe: {
        show: true,
        lineStyle: {
          color: 'rgba(0,0,0,0.2)',
          width: 1
        }
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

// 更新数据
const updateData = () => {
  // 更新当前时间
  currentTime.value = new Date().toLocaleString()
  
  // 更新3D散点图数据
  if (charts.value.modelPerformance3D) {
    const newData = mockData.modelPerformance3D.map(item => {
      // 只对准确率和速度添加小的随机波动
      const accuracy = parseFloat(item[0]) + (Math.random() * 0.02 - 0.01)
      const speed = parseFloat(item[1]) + (Math.random() * 2 - 1)
      return [
        Math.min(0.99, Math.max(0.7, accuracy)).toFixed(3),
        Math.max(10, speed).toFixed(1),
        item[2],
        item[3],
        item[4]
      ]
    })
    
    charts.value.modelPerformance3D.setOption({
      dataset: {
        source: newData
      }
    })
  }
}

// 窗口大小变化时重新调整图表大小
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
  <div class="analysis-container">
    <div class="analysis-header">
      <h1>手语识别3D数据分析</h1>
      <div class="analysis-time">{{ currentTime }}</div>
    </div>
    
    <div class="analysis-content">
      <div class="chart-card" @click="showFullscreenChart('modelPerformance3D', '模型性能3D分析')">
        <div id="modelPerformance3DChart" class="chart"></div>
        <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
      </div>
      
      <div class="chart-row">
        <div class="chart-card" @click="showFullscreenChart('scenarioAccuracy', '场景准确率分析')">
          <div id="scenarioAccuracyChart" class="chart"></div>
          <div class="chart-zoom-hint"><i class="el-icon-zoom-in"></i> 点击放大</div>
        </div>
        <div class="chart-card" @click="showFullscreenChart('distanceAngleAccuracy', '距离角度影响分析')">
          <div id="distanceAngleAccuracyChart" class="chart"></div>
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
.analysis-container {
  height: 100%;
  width: 100%;
  background-color: #f5f7fa;
  color: #333;
  padding: 20px;
  box-sizing: border-box;
  overflow: auto;
  
  .analysis-header {
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
    
    .analysis-time {
      font-size: 16px;
      color: #5b8ff9;
      font-weight: 500;
    }
  }
  
  .analysis-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
    
    .chart-card {
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
      
      .chart {
        width: 100%;
        height: 400px;
        
        @media (max-width: 768px) {
          height: 350px;
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
    
    .chart-row {
      display: flex;
      gap: 20px;
      
      @media (max-width: 1200px) {
        flex-direction: column;
      }
      
      .chart-card {
        flex: 1;
        
        .chart {
          height: 350px;
          
          @media (max-width: 768px) {
            height: 300px;
          }
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
