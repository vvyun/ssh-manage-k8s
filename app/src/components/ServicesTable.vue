<template>
  <div class="services-table">
    <div class="table-header">
      <el-input
        v-model="filterText"
        placeholder="按名称筛选服务..."
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
      <el-table-column prop="TYPE" label="类型" width="120" />
      <el-table-column prop="CLUSTER_IP" label="集群IP" width="150" />
      <el-table-column prop="PORTS" label="端口" min-width="200" />
      <el-table-column prop="AGE" label="年龄" width="120" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            text
            @click="handleShowServiceDetail(row.NAME)"
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
    
    <!-- 服务详情对话框 -->
    <el-dialog
      v-model="showServiceDetailDialog"
      title="服务详情"
      width="80%"
      :destroy-on-close="true"
    >
      <div v-loading="serviceDetailLoading">
        <pre v-if="serviceDetail" class="yaml-content">{{ JSON.stringify(serviceDetail, null, 2) }}</pre>
        <div v-else class="no-data">暂无服务详情数据</div>
      </div>
      <template #footer>
        <el-button @click="showServiceDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getServices, getServiceDetail } from '../api/cluster'
import { ElMessage } from 'element-plus'

const props = defineProps({
  clusterId: String,
  namespace: String
})

const loading = ref(false)
const data = ref([])
const filterText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 服务详情相关变量
const showServiceDetailDialog = ref(false)
const serviceDetail = ref(null)
const serviceDetailLoading = ref(false)

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
    const result = await getServices(props.clusterId, props.namespace)
    data.value = Array.isArray(result) ? result : []
    currentPage.value = 1
  } catch (error) {
    console.error('加载服务失败:', error)
    data.value = []
  } finally {
    loading.value = false
  }
}

watch([() => props.clusterId, () => props.namespace], () => {
  loadData()
}, { immediate: true })

watch(() => filterText.value, () => {
  currentPage.value = 1
})

// 获取服务详情
const handleShowServiceDetail = async (serviceName) => {
  if (!props.clusterId || !props.namespace) {
    ElMessage.error('集群或命名空间信息不完整')
    return
  }
  
  serviceDetailLoading.value = true
  showServiceDetailDialog.value = true
  
  try {
    const result = await getServiceDetail(props.clusterId, serviceName, props.namespace)
    serviceDetail.value = result
  } catch (error) {
    console.error('获取服务详情失败:', error)
    ElMessage.error(`获取服务详情失败: ${error.message || error}`)
    serviceDetail.value = null
  } finally {
    serviceDetailLoading.value = false
  }
}

// 暴露方法给父组件
defineExpose({
  loadData
})
</script>

<style scoped>
.services-table {
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
.yaml-content {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  max-height: 500px;
  overflow: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 20px;
}

</style>


