<template>
  <div class="common-table">
    <div class="table-header">
      <div class="header-content">
        <el-input v-model="filterText" placeholder="按名称筛选Pods..." :prefix-icon="Search" clearable
          style="width: 300px" />
        <!-- <el-button type="primary" @click="showCreateDialog = true" style="margin-left: auto; ">
          部署Pod
        </el-button> -->
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
      <el-table-column prop="STATUS" label="状态" width="100">
        <template #default="{ row }">
          <el-tag 
            :type="getStatusType(row.STATUS)"
            size="small"
          >
            {{ row.STATUS }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="RESTARTS" label="重启次数" width="100" />
      <el-table-column prop="AGE" label="运行时长" width="120" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            size="small"
            @click="handleViewLogs(row.NAME)"
          >
            日志
          </el-button>
          <el-button 
            type="danger" 
            size="small"
            @click="handleDelete(row.NAME)"
          >
            删除
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
    
    <!-- 查看日志对话框 -->
    <ViewLogsDialog
      v-model="showLogsDialog"
      :cluster-id="clusterId"
      :namespace="namespace"
      :pod-name="selectedPod"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getPods, deletePod } from '../../api/cluster'
import ViewLogsDialog from '../dialogs/ViewLogsDialog.vue'

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
const showLogsDialog = ref(false)
const selectedPod = ref(null)

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

const getStatusType = (status) => {
  const statusMap = {
    'Running': 'success',
    'Pending': 'warning',
    'Failed': 'danger',
    'Succeeded': 'success',
    'Error': 'danger'
  }
  return statusMap[status] || 'info'
}

const loadData = async () => {
  if (!props.clusterId || !props.namespace) return
  
  loading.value = true
  try {
    const result = await getPods(props.clusterId, props.namespace)
    data.value = Array.isArray(result) ? result : []
    currentPage.value = 1
  } catch (error) {
    console.error('加载Pods失败:', error)
    data.value = []
  } finally {
    loading.value = false
  }
}

const handleViewLogs = (name) => {
  selectedPod.value = name
  showLogsDialog.value = true
}

const handleDelete = async (name) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除Pod ${name} 吗？此操作将重启Pod，无法恢复！`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deletePod(props.clusterId, name, props.namespace)
    ElMessage.success(`Pod ${name} 已成功删除`)
    loadData()
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除Pod失败: ' + error.message)
    }
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


