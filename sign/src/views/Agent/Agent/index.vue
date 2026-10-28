<template>
  <div class="knowledge-base-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="status-card">
          <div class="status-indicator">
            <div class="status-icon" :class="{ 'online': ollamaStatus }"></div>
            <span>Ollama服务状态: {{ ollamaStatus ? '在线' : '离线' }}</span>
            <el-button type="primary" size="small" @click="checkOllamaStatus" icon="Refresh">刷新</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <!-- 左侧：知识库管理 -->
      <el-col :span="12">
        <el-card class="knowledge-card">
          <template #header>
            <div class="card-header">
              <span>手语知识库管理</span>
              <el-button type="primary" @click="showAddDocumentDialog">添加文档</el-button>
            </div>
          </template>
          
          <div class="document-list">
            <el-empty v-if="documents.length === 0" description="暂无知识文档"></el-empty>
            
            <el-collapse v-else accordion>
              <el-collapse-item v-for="doc in documents" :key="doc.id" :name="doc.id">
                <template #title>
                  <div class="document-title">
                    <span>{{ doc.title }}</span>
                    <span class="document-date">{{ formatDate(doc.updated_at) }}</span>
                  </div>
                </template>
                
                <div class="document-content">
                  <p>{{ doc.content }}</p>
                  <div class="document-actions">
                    <el-button type="primary" size="small" @click.stop="editDocument(doc)">编辑</el-button>
                    <el-button type="danger" size="small" @click.stop="confirmDeleteDocument(doc)">删除</el-button>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：查询界面 -->
      <el-col :span="12">
        <el-card class="query-card">
          <template #header>
            <div class="card-header">
              <span>手语知识查询</span>
            </div>
          </template>
          
          <div class="query-form">
            <el-form>
              <el-form-item label="问题">
                <el-input 
                  v-model="queryForm.query" 
                  type="textarea" 
                  :rows="4" 
                  placeholder="请输入您的手语相关问题..."
                ></el-input>
              </el-form-item>
              
              <el-form-item>
                <el-switch
                  v-model="queryForm.useRAG"
                  active-text="使用知识库增强"
                  inactive-text="仅使用模型"
                ></el-switch>
              </el-form-item>
              
              <el-form-item label="温度">
                <el-slider 
                  v-model="queryForm.temperature" 
                  :min="0" 
                  :max="1" 
                  :step="0.1"
                ></el-slider>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="submitQuery" 
                  :loading="queryLoading"
                  :disabled="!queryForm.query"
                >提交问题</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div v-if="queryResult" class="query-result">
            <h3>回答</h3>
            <div class="answer-content">{{ queryResult.answer }}</div>
            
            <div v-if="queryResult.documents && queryResult.documents.length > 0" class="reference-docs">
              <h4>参考文档</h4>
              <el-collapse>
                <el-collapse-item 
                  v-for="(doc, index) in queryResult.documents" 
                  :key="index" 
                  :title="`${doc.title} (相似度: ${(doc.similarity * 100).toFixed(2)}%)`"
                >
                  <p>{{ doc.content }}</p>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑文档对话框 -->
    <el-dialog 
      v-model="documentDialog.visible" 
      :title="documentDialog.isEdit ? '编辑文档' : '添加文档'"
      width="50%"
    >
      <el-form :model="documentDialog.form" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="documentDialog.form.title" placeholder="请输入文档标题"></el-input>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input 
            v-model="documentDialog.form.content" 
            type="textarea" 
            :rows="10" 
            placeholder="请输入文档内容"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="documentDialog.visible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveDocument" 
            :loading="documentDialog.loading"
            :disabled="!documentDialog.form.title || !documentDialog.form.content"
          >保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialog.visible"
      title="确认删除"
      width="30%"
    >
      <p>确定要删除文档 "{{ deleteDialog.title }}" 吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialog.visible = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="deleteDocument" 
            :loading="deleteDialog.loading"
          >确认删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import requestUtil from '@/util/request'

// 状态
const ollamaStatus = ref(false)
const documents = ref([])
const queryLoading = ref(false)
const queryResult = ref(null)

// 表单
const queryForm = ref({
  query: '',
  useRAG: true,
  temperature: 0.7
})

// 对话框状态
const documentDialog = ref({
  visible: false,
  isEdit: false,
  loading: false,
  form: {
    id: null,
    title: '',
    content: ''
  }
})

const deleteDialog = ref({
  visible: false,
  loading: false,
  id: null,
  title: ''
})

// 初始化
onMounted(() => {
  checkOllamaStatus()
  fetchDocuments()
})

// 检查Ollama服务状态
const checkOllamaStatus = async () => {
  try {
    const response = await requestUtil.get('/agent/api/status/ollama/')
    ollamaStatus.value = response.data.available
  } catch (error) {
    console.error('检查Ollama状态失败:', error)
    ollamaStatus.value = false
  }
}

// 获取文档列表
const fetchDocuments = async () => {
  try {
    const response = await requestUtil.get('/agent/api/document/')
    documents.value = response.data
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  }
}

// 提交查询
const submitQuery = async () => {
  if (!queryForm.value.query) return
  
  queryLoading.value = true
  queryResult.value = null
  
  try {
    const response = await requestUtil.post('/agent/api/query/', {
      query: queryForm.value.query,
      use_rag: queryForm.value.useRAG,
      temperature: queryForm.value.temperature
    })
    
    queryResult.value = response.data
  } catch (error) {
    console.error('查询失败:', error)
    
    // 显示更友好的错误信息
    let errorMessage = '查询失败，请稍后重试'
    
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
    
    // 设置一个错误结果
    queryResult.value = {
      answer: `查询出错: ${errorMessage}\n\n可能的原因:\n1. Ollama服务未启动\n2. 模型未下载\n3. 服务器内部错误\n\n请检查Ollama服务状态并重试。`,
      source: 'error'
    }
  } finally {
    queryLoading.value = false
  }
}

// 显示添加文档对话框
const showAddDocumentDialog = () => {
  documentDialog.value.isEdit = false
  documentDialog.value.form = {
    id: null,
    title: '',
    content: ''
  }
  documentDialog.value.visible = true
}

// 编辑文档
const editDocument = (doc) => {
  documentDialog.value.isEdit = true
  documentDialog.value.form = {
    id: doc.id,
    title: doc.title,
    content: doc.content
  }
  documentDialog.value.visible = true
}

// 保存文档
const saveDocument = async () => {
  const { title, content } = documentDialog.value.form
  
  if (!title || !content) return
  
  documentDialog.value.loading = true
  
  try {
    if (documentDialog.value.isEdit) {
      // 更新文档
      await requestUtil.post(`/agent/api/document/${documentDialog.value.form.id}/update/`, {
        title,
        content
      })
      ElMessage.success('文档更新成功')
    } else {
      // 添加文档
      await requestUtil.post('/agent/api/document/', {
        title,
        content
      })
      ElMessage.success('文档添加成功')
    }
    
    // 刷新文档列表
    fetchDocuments()
    documentDialog.value.visible = false
  } catch (error) {
    console.error('保存文档失败:', error)
    ElMessage.error('保存文档失败')
  } finally {
    documentDialog.value.loading = false
  }
}

// 确认删除文档
const confirmDeleteDocument = (doc) => {
  deleteDialog.value.id = doc.id
  deleteDialog.value.title = doc.title
  deleteDialog.value.visible = true
}

// 删除文档
const deleteDocument = async () => {
  deleteDialog.value.loading = true
  
  try {
    await requestUtil.del(`/agent/api/document/${deleteDialog.value.id}/`)
    ElMessage.success('文档删除成功')
    fetchDocuments()
    deleteDialog.value.visible = false
  } catch (error) {
    console.error('删除文档失败:', error)
    ElMessage.error('删除文档失败')
  } finally {
    deleteDialog.value.loading = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped lang="scss">
.knowledge-base-container {
  padding: 20px;
  
  .mt-20 {
    margin-top: 20px;
  }
  
  .status-card {
    margin-bottom: 20px;
    
    .status-indicator {
      display: flex;
      align-items: center;
      
      .status-icon {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #f56c6c;
        margin-right: 8px;
        
        &.online {
          background-color: #67c23a;
        }
      }
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .document-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    
    .document-date {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .document-content {
    padding: 10px 0;
    
    .document-actions {
      margin-top: 10px;
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
  }
  
  .query-result {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
    
    .answer-content {
      background-color: #f8f9fa;
      padding: 15px;
      border-radius: 4px;
      margin-bottom: 20px;
      white-space: pre-wrap;
    }
    
    .reference-docs {
      margin-top: 20px;
    }
  }
}
</style>
