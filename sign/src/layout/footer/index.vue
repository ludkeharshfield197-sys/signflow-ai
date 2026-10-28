<template>
  <div class="footer">
    <div class="footer-content">
      <div class="copyright">
        © {{ currentYear }} 手语识别系统 - 版权所有
      </div>
      <div class="developer">
        由鹿津愉团队开发
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style lang="scss" scoped>
.footer {
  background-color: #f5f7fa;
  padding: 15px 20px;
  width: 100%;
  border-top: 1px solid #e4e7ed;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
}

.copyright, .developer {
  color: #606266;
  font-size: 14px;
}
</style>

