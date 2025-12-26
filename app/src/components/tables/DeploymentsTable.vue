<template>
  <div class="common-table">
    <div class="table-header">
      <div class="header-content">
        <el-input v-model="filterText" placeholder="按名称筛选Deployment..." :prefix-icon="Search" clearable
          style="width: 300px" />
        <el-button type="primary" @click="showCreateDialog = true" style="margin-left: auto; ">
          部署Deployment
        </el-button>
      </div>
    </div>

    <el-table :data="paginatedData" v-loading="loading" stripe style="width: 100%"
      :default-sort="{ prop: 'NAME', order: 'ascending' }">
      <el-table-column prop="NAME" label="名称" sortable width="250" />
      <el-table-column prop="READY" label="状态" width="80" />
      <el-table-column prop="IMAGES" show-overflow-tooltip label="镜像" />
      <el-table-column prop="AGE" label="运行时长" width="100" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-dropdown trigger="click">
            <span class="el-dropdown-link">
               ...
              <!-- <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon> -->
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <el-button type="primary" size="small" title="更新Deployment"
                    @click="handleUpdateImage(row.NAME, row.IMAGES)">升级</el-button>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-button type="warning" size="small" @click="handleScale(row)">伸缩</el-button>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-button type="info" size="small" @click="handleShowDetail(row.NAME)">详情 </el-button>
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-button type="danger" size="small" @click="handleDelete(row.NAME)">删除</el-button>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length" layout="total, sizes, prev, pager, next, jumper" />
    </div>

    <!-- 更新镜像对话框 -->
    <UpdateImageDialog v-model="showUpdateDialog" :cluster-id="props.clusterId" :namespace="props.namespace"
      :deployment-name="selectedDeployment" :deployment-images="selectedDeploymentImages" @success="loadData" />

    <!-- 容器伸缩对话框 -->
    <ScaleDeploymentDialog v-model="showScaleDialog" :cluster-id="props.clusterId" :namespace="props.namespace"
      :deployment="selectedDeployment" @success="loadData" />

    <!-- 详情对话框 -->
    <DetailViewDialog v-model="showDetailDialog" :cluster-id="props.clusterId" :namespace="props.namespace"
      :resource-name="selectedDeployment" resource-type="Deployment" />

    <!-- 创建Deployment对话框 -->
    <CreateDeploymentDialog v-model="showCreateDialog" :cluster-id="props.clusterId" :namespace="props.namespace"
      @success="loadData" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowDown } from '@element-plus/icons-vue'
import { getDeployments, deleteDeployment } from '../../api/cluster'
import UpdateImageDialog from '../dialogs/UpdateImageDialog.vue'
import ScaleDeploymentDialog from '../dialogs/ScaleDeploymentDialog.vue'
import CreateDeploymentDialog from '../dialogs/CreateDeploymentDialog.vue'
import DetailViewDialog from '../dialogs/DetailViewDialog.vue'

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
const selectedDeploymentImages = ref(null)

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

const handleUpdateImage = (name, images) => {
  selectedDeployment.value = name
  selectedDeploymentImages.value = images
  showUpdateDialog.value = true
}

const handleScale = (deployment) => {
  selectedDeployment.value = deployment
  showScaleDialog.value = true
}

const handleShowDetail = (deploymentName) => {
  selectedDeployment.value = deploymentName
  showDetailDialog.value = true
}

const handleDelete = async (deploymentName) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Deployment ${deploymentName}吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteDeployment(props.clusterId, deploymentName, props.namespace)
    ElMessage.success('删除成功')
    loadData() // 重新加载数据
  } catch (error) {
    if (error !== 'cancel') { // 用户取消操作时不显示错误信息
      console.error('删除Deployment失败:', error)
      ElMessage.error(error.message || '删除失败')
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

.example-showcase .el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
</style>
