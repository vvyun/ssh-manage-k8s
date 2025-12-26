<template>
  <div class="services-table">
    <div class="table-header">
      <div class="header-content">
        <el-input v-model="filterText" placeholder="按名称筛选Service..." :prefix-icon="Search" clearable
          style="width: 300px" />
        <el-button type="primary" @click="handleCreate" style="margin-left: auto; ">
          部署Service
        </el-button>
      </div>
    </div>

    <el-table :data="paginatedData" v-loading="loading" stripe style="width: 100%"
      :default-sort="{ prop: 'NAME', order: 'ascending' }">
      <el-table-column prop="NAME" label="名称" sortable min-width="200" />
      <el-table-column prop="TYPE" label="类型" width="120" />
      <el-table-column prop="CLUSTER_IP" label="集群IP" width="150" />
      <el-table-column prop="PORTS" label="端口" min-width="200" />
      <el-table-column prop="AGE" label="运行时长" width="120" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button type="info" size="small" @click="handleShowServiceDetail(row.NAME)">
            详情
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row.NAME)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length" layout="total, sizes, prev, pager, next, jumper" />
    </div>

    <!-- 详情对话框 -->
    <DetailViewDialog
      v-model="showServiceDetailDialog"
      :cluster-id="props.clusterId"
      :namespace="props.namespace"
      :resource-name="selectedService"
      resource-type="Service"
    />
    
    <!-- 创建Service对话框 -->
    <CreateServiceDialog
      v-model="showCreateServiceDialog"
      :cluster-id="props.clusterId"
      :namespace="props.namespace"
      @success="loadData"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getServices, deleteService } from '../../api/cluster'
import { ElMessage, ElMessageBox } from 'element-plus'
import DetailViewDialog from '../dialogs/DetailViewDialog.vue'
import CreateServiceDialog from '../dialogs/CreateServiceDialog.vue'

const props = defineProps({
  clusterId: String,
  namespace: String
})

const loading = ref(false)
const data = ref([])
const filterText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const showServiceDetailDialog = ref(false)
const selectedService = ref(null)

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

const handleShowServiceDetail = (serviceName) => {
  selectedService.value = serviceName
  showServiceDetailDialog.value = true
}

// 处理创建按钮点击
const showCreateServiceDialog = ref(false)

const handleCreate = () => {
  showCreateServiceDialog.value = true
}

const handleDelete = async (serviceName) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Service ${serviceName}吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteService(props.clusterId, serviceName, props.namespace)
    ElMessage.success('删除成功')
    loadData() // 重新加载数据
  } catch (error) {
    if (error !== 'cancel') { // 用户取消操作时不显示错误信息
      console.error('删除Service失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 暴露方法给父组件
defineExpose({
  loadData
})
</script>

<style scoped>
.common-table {
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
