<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// 响应式相关
const contentHeight = ref('auto');

// 监听窗口大小变化
const handleResize = () => {
  updateContentHeight();
};

// 更新内容高度
const updateContentHeight = () => {
  // 延迟执行以确保DOM已更新
  setTimeout(() => {
    const headerHeight = 60; // 估计的头部高度
    const footerHeight = 40; // 估计的底部高度
    const padding = 40; // 上下内边距
    
    contentHeight.value = `calc(100vh - ${headerHeight + footerHeight + padding}px)`;
  }, 100);
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  updateContentHeight();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<template>
  <div class="dashboard-container" :style="{ minHeight: contentHeight }">
    <div class="dashboard-text">欢迎使用手语识别系统</div>
    <div class="feature-cards">
      <div class="feature-card">
        <h3>实时手语识别</h3>
        <p>通过摄像头实时捕捉手语动作，进行即时翻译和识别。</p>
        <div class="card-icon">
          <i class="el-icon-video-camera"></i>
        </div>
      </div>
      <div class="feature-card">
        <h3>多模型支持</h3>
        <p>支持多种YOLO模型，可根据不同场景选择最适合的识别模型。</p>
        <div class="card-icon">
          <i class="el-icon-s-grid"></i>
        </div>
      </div>
      <div class="feature-card">
        <h3>数据分析</h3>
        <p>提供详细的识别数据分析，帮助优化识别效果和用户体验。</p>
        <div class="card-icon">
          <i class="el-icon-data-line"></i>
        </div>
      </div>
      <div class="feature-card">
        <h3>批量处理</h3>
        <p>支持批量上传图片和视频进行手语识别，提高工作效率。</p>
        <div class="card-icon">
          <i class="el-icon-upload"></i>
        </div>
      </div>
    </div>
    
    <div class="system-info">
      <h2>系统信息</h2>
      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">系统版本</div>
          <div class="info-value">v1.0.0</div>
        </div>
        <div class="info-item">
          <div class="info-label">模型数量</div>
          <div class="info-value">5</div>
        </div>
        <div class="info-item">
          <div class="info-label">支持手语类型</div>
          <div class="info-value">中国手语、美国手语</div>
        </div>
        <div class="info-item">
          <div class="info-label">识别准确率</div>
          <div class="info-value">95.8%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: auto;
}

.dashboard-text {
  font-size: 30px;
  line-height: 46px;
  color: #333;
  text-align: center;
  margin-bottom: 30px;
  font-weight: bold;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  
  .feature-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    h3 {
      font-size: 18px;
      margin-bottom: 10px;
      color: #333;
    }
    
    p {
      color: #666;
      line-height: 1.6;
    }
    
    .card-icon {
      position: absolute;
      bottom: 15px;
      right: 15px;
      font-size: 24px;
      color: #409EFF;
      opacity: 0.2;
    }
  }
}

.system-info {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  
  h2 {
    font-size: 20px;
    margin-bottom: 20px;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    
    .info-item {
      .info-label {
        font-size: 14px;
        color: #999;
        margin-bottom: 5px;
      }
      
      .info-value {
        font-size: 16px;
        color: #333;
        font-weight: 500;
      }
    }
  }
}

@media (max-width: 768px) {
  .dashboard-text {
    font-size: 24px;
    line-height: 36px;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
  }
  
  .system-info {
    .info-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
