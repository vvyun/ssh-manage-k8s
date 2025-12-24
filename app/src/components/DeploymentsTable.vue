<template>
  <div class="deployments-table">
    <div class="table-header">
      <el-input
        v-model="filterText"
        placeholder="按名称筛选工作负载..."
        :prefix-icon="Search"
        clearable
        style="width: 300px"
      />
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
      <el-table-column label="操作" width="200" fixed="right">
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
            容器伸缩
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
      :cluster-id="clusterId"
      :namespace="namespace"
      :deployment-name="selectedDeployment"
      @success="loadData"
    />
    
    <!-- 容器伸缩对话框 -->
    <ScaleDeploymentDialog
      v-model="showScaleDialog"
      :cluster-id="clusterId"
      :namespace="namespace"
      :deployment="selectedDeployment"
      @success="loadData"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getDeployments } from '../api/cluster'
import UpdateImageDialog from './UpdateImageDialog.vue'
import ScaleDeploymentDialog from './ScaleDeploymentDialog.vue'

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
const selectedDeployment = ref(null)

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

watch([() => props.clusterId, () => props.namespace], () => {
  loadData()
}, { immediate: true })

watch(() => filterText.value, () => {
  currentPage.value = 1
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

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}
</style>


