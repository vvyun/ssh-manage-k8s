<template>
  <div class="deployments-table">
    <div class="table-header">
      <div class="header-content">
        <el-input
          v-model="filterText"
          placeholder="按名称筛选工作负载..."
          :prefix-icon="Search"
          clearable
          style="width: 300px"
        />
        <el-button
          type="primary"
          @click="showCreateDialog = true"
          style="margin-left: 10px;"
        >
          部署Deployment
        </el-button>
      </div>
    </div>
    
    <el-table
      :data="paginatedData"
      v-loading="loading"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'NAME', order: 'ascending' }"
    >
      <el-table-column prop="NAME" label="名称" sortable min-width="200" />
      <el-table-column prop="READY" label="就绪" width="100" />
      <el-table-column prop="UP_TO_DATE" label="更新" width="100" />
      <el-table-column prop="AVAILABLE" label="可用" width="100" />
      <el-table-column prop="AGE" label="年龄" width="120" />
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            size="small"
            @click="handleUpdateImage(row.NAME)"
          >
            更新镜像
          </el-button>
          <el-button 
            type="warning" 
            size="small"
            @click="handleScale(row)"
          >
            伸缩
          </el-button>
          <el-button 
            type="info" 
            size="small"
            @click="handleShowDetail(row.NAME)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
    
    <!-- 更新镜像对话框 -->
    <UpdateImageDialog
      v-model="showUpdateDialog"
      :cluster-id="props.clusterId"
      :namespace="props.namespace"
      :deployment-name="selectedDeployment"
      @success="loadData"
    />
    
    <!-- 容器伸缩对话框 -->
    <ScaleDeploymentDialog
      v-model="showScaleDialog"
      :cluster-id="props.clusterId"
      :namespace="props.namespace"
      :deployment="selectedDeployment"
      @success="loadData"
    />
    
    <!-- Deployment详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`Deployment详情 - ${selectedDeployment}`"
      width="80%"
      top="5vh"
    >
      <div class="yaml-content">
        <pre>{{ JSON.stringify(deploymentDetail, null, 2) }}</pre>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 创建Deployment对话框 -->
    <CreateDeploymentDialog
      v-model="showCreateDialog"
      :cluster-id="props.clusterId"
      :namespace="props.namespace"
      @success="loadData"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getDeployments, getDeploymentDetail, createDeployment } from '../api/cluster'
import UpdateImageDialog from './UpdateImageDialog.vue'
import ScaleDeploymentDialog from './ScaleDeploymentDialog.vue'
import CreateDeploymentDialog from './CreateDeploymentDialog.vue'

const props = defineProps({
  clusterId: String,
  namespace: String
})

const emit = defineEmits(['refresh'])

const loading = ref(false)
const data = ref([])
const filterText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const showUpdateDialog = ref(false)
const showScaleDialog = ref(false)
const showDetailDialog = ref(false)
const showCreateDialog = ref(false)
const selectedDeployment = ref(null)
const deploymentDetail = ref(null)

const filteredData = computed(() => {
  if (!filterText.value) return data.value
  const keyword = filterText.value.toLowerCase()
  return data.value.filter(item => 
    (item.NAME || '').toLowerCase().includes(keyword)
  )
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const loadData = async () => {
  if (!props.clusterId || !props.namespace) return
  
  loading.value = true
  try {
    const result = await getDeployments(props.clusterId, props.namespace)
    data.value = Array.isArray(result) ? result : []
    currentPage.value = 1
  } catch (error) {
    console.error('加载工作负载失败:', error)
    data.value = []
  } finally {
    loading.value = false
  }
}

const handleUpdateImage = (name) => {
  selectedDeployment.value = name
  showUpdateDialog.value = true
}

const handleScale = (deployment) => {
  selectedDeployment.value = deployment
  showScaleDialog.value = true
}

const handleShowDetail = async (deploymentName) => {
  try {
    deploymentDetail.value = await getDeploymentDetail(props.clusterId, deploymentName, props.namespace)
    selectedDeployment.value = deploymentName
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error(`获取Deployment详情失败: ${error.message || error}`)
  }
}

watch([() => props.clusterId, () => props.namespace], () => {
  loadData()
}, { immediate: true })

watch(() => filterText.value, () => {
  currentPage.value = 1
})

// 暴露方法给父组件
defineExpose({
  loadData
})
</script>

<style scoped>
.deployments-table {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-header {
  margin-bottom: 15px;
}

.header-content {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.yaml-content {
  max-height: 60vh;
  overflow: auto;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.yaml-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>


