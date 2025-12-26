<template>
  <div class="common-table">
    <div class="table-header">
      <div class="header-content">
        <el-input v-model="filterText" placeholder="按名称筛选ConfigMap..." :prefix-icon="Search" clearable
          style="width: 300px" />
        <el-button type="primary" @click="handleCreate" style="margin-left: auto; ">
          部署ConfigMap
        </el-button>
      </div>
    </div>

    <el-table :data="configmaps" v-loading="loading" style="width: 100%"
      :default-sort="{ prop: 'AGE', order: 'descending' }">
      <el-table-column prop="NAME" label="名称" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <el-link type="primary" @click="handleViewDetail(row)">{{ row.NAME }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="DATA" label="数据项数量" min-width="120" />
      <el-table-column prop="AGE" label="运行时长" min-width="120" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" type="info" @click="handleViewDetail(row)">详情</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination v-if="total > pageSize" @size-change="handleSizeChange" @current-change="handleCurrentChange"
      :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize"
      layout="total, sizes, prev, pager, next, jumper" :total="total"
      style="margin-top: 16px; justify-content: center; display: flex;" />
  </div>

  <!-- 详情对话框 -->
  <DetailViewDialog
    v-model="showDetailDialog"
    :cluster-id="props.clusterId"
    :namespace="props.namespace"
    :resource-name="selectedConfigMap"
    resource-type="ConfigMap"
  />
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getConfigmaps, deleteConfigMap } from '../../api/cluster'
import DetailViewDialog from '../dialogs/DetailViewDialog.vue'

const props = defineProps({
  clusterId: {
    type: String,
    required: true
  },
  namespace: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['refresh'])

const configmaps = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 详情对话框相关变量
const showDetailDialog = ref(false)
const selectedConfigMap = ref(null)

// 加载ConfigMap数据
const loadData = async () => {
  if (!props.clusterId || !props.namespace) return

  loading.value = true
  try {
    const response = await getConfigmaps(props.clusterId, props.namespace)
    configmaps.value = response

    // 计算总数（如果需要分页）
    total.value = response.length
  } catch (error) {
    console.error('获取ConfigMap列表失败:', error)
    ElMessage.error(`获取ConfigMap列表失败: ${error.message || error}`)
  } finally {
    loading.value = false
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadData()
}

// 处理创建按钮点击
const handleCreate = () => {
  ElMessage.info('创建ConfigMap功能待实现')
}

// 处理查看详情
const handleViewDetail = (row) => {
  selectedConfigMap.value = row.NAME
  showDetailDialog.value = true
}

// 处理删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除ConfigMap "${row.NAME}" 吗？此操作无法撤销！`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteConfigMap(props.clusterId, row.NAME, props.namespace)
    ElMessage.success('ConfigMap删除成功')
    // 实际删除后重新加载数据
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除ConfigMap失败:', error)
      ElMessage.error(`删除ConfigMap失败: ${error.message || error}`)
    }
  }
}

// 初始化加载数据
onMounted(() => {
  loadData()
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