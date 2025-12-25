<template>
  <div class="cluster-sidebar">
    <div class="sidebar-header">
      <div>
        <h3>集群列表</h3>
        <p class="sidebar-subtitle">点击切换集群并进行管理</p>
      </div>
      <div class="sidebar-actions">
        <el-button :icon="Refresh" circle size="medium" @click="loadClusters" title="刷新集群" />
        <el-button :icon="Plus" circle size="medium" type="primary" @click="showAddDialog = true" title="添加集群" />
      </div>
    </div>

    <el-input v-model="searchKeyword" placeholder="筛选集群..." :prefix-icon="Search" class="cluster-search" clearable />

    <div class="cluster-list">
      <el-scrollbar height="200px">
        <div v-if="filteredClusters.length === 0" class="empty-state">
          <p>{{ searchKeyword ? '未找到匹配的集群' : '暂无集群，请先创建一个集群' }}</p>
          <el-button :icon="Plus" type="primary" circle @click="showAddDialog = true" />
        </div>
        <div v-for="cluster in filteredClusters" :key="cluster.name"
          :class="['cluster-item', { active: currentClusterId === normalizeClusterId(cluster.name) }]"
          @click="selectCluster(cluster)">
          <div class="cluster-info">
            <div class="cluster-title">{{ cluster.name || '未命名集群' }}</div>
          </div>
          <el-dropdown trigger="click" @command="handleCommand">
            <el-button :icon="MoreFilled" circle size="small" class="actions-btn" @click.stop />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :command="{ action: 'rename', cluster }">
                  重命名
                </el-dropdown-item>
                <el-dropdown-item :command="{ action: 'delete', cluster }" divided>
                  删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-scrollbar>
    </div>

    <AddClusterDialog v-model="showAddDialog" @success="handleAddSuccess" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Search, MoreFilled } from '@element-plus/icons-vue'
import { getClusters, deleteCluster, updateCluster } from '../api/cluster'
import AddClusterDialog from './dialogs/AddClusterDialog.vue'

const store = useStore()
const router = useRouter()

const clusters = ref([])
const searchKeyword = ref('')
const showAddDialog = ref(false)
const currentClusterId = ref(null)

const filteredClusters = computed(() => {
  if (!searchKeyword.value) return clusters.value
  const keyword = searchKeyword.value.toLowerCase()
  return clusters.value.filter(c =>
    c.name && c.name.toLowerCase().includes(keyword)
  )
})

const normalizeClusterId = (name) => {
  return (name || '').toLowerCase().replace(/\s+/g, '-')
}

const loadClusters = async () => {
  try {
    const data = await getClusters()
    clusters.value = Array.isArray(data) ? data : []
    store.commit('SET_CLUSTERS', clusters.value)

    // 自动选择第一个集群
    if (clusters.value.length > 0 && !currentClusterId.value) {
      const firstCluster = clusters.value[0]
      selectCluster(firstCluster)
    }
  } catch (error) {
    ElMessage.error('加载集群列表失败: ' + error.message)
  }
}

const selectCluster = (cluster) => {
  const clusterId = normalizeClusterId(cluster.name)
  currentClusterId.value = clusterId
  store.commit('SET_CURRENT_CLUSTER', cluster)
  store.commit('SET_CURRENT_NAMESPACE', cluster.namespace || 'default')
}

const handleCommand = async ({ action, cluster }) => {
  if (action === 'rename') {
    const { value } = await ElMessageBox.prompt('请输入新的集群名称', '重命名集群', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: cluster.name,
      inputValidator: (val) => {
        if (!val || !val.trim()) {
          return '集群名称不能为空'
        }
        return true
      }
    })

    if (value && value.trim() !== cluster.name) {
      try {
        const clusterId = normalizeClusterId(cluster.name)
        await updateCluster(clusterId, { name: value.trim() })
        ElMessage.success('集群名称更新成功')
        loadClusters()
      } catch (error) {
        ElMessage.error('更新失败: ' + error.message)
      }
    }
  } else if (action === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确认要删除集群 ${cluster.name} 吗？此操作将永久删除集群配置，无法恢复！`,
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      const clusterId = normalizeClusterId(cluster.name)
      await deleteCluster(clusterId)
      ElMessage.success('集群删除成功')

      if (currentClusterId.value === clusterId) {
        currentClusterId.value = null
        store.commit('SET_CURRENT_CLUSTER', null)
      }

      loadClusters()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败: ' + error.message)
      }
    }
  }
}

const handleAddSuccess = () => {
  loadClusters()
}

onMounted(() => {
  loadClusters()
})
</script>

<style scoped>
.cluster-sidebar {
  height: 100%;
  background: linear-gradient(180deg, #233445 0%, #1c2633 100%);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px;
  margin-bottom: 0px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 20px;
  color: #f3f6f9;
}

.sidebar-subtitle {
  margin-top: 4px;
  color: #dae0e7;
  font-size: 12px;
}

.sidebar-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
}

.cluster-search {
  margin-bottom: 5px;
  padding-left: 12px;
  padding-right: 12px;
}

:deep(.cluster-search .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

:deep(.cluster-search .el-input__inner) {
  color: #e7eef6;
}

:deep(.cluster-search .el-input__inner::placeholder) {
  color: #9fb3c8;
}

.cluster-list {
  flex: 1;
  margin-top: 5px;
  overflow: auto;
  padding: 12px;
}

.cluster-list::-webkit-scrollbar {
  display: none;
}

.cluster-list {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.empty-state {
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.25);
  border-radius: 12px;
  padding: 20px 12px;
  text-align: center;
  color: #9fb3c8;
}

.empty-state p {
  margin-bottom: 12px;
}

.cluster-item {
  padding: 12px;
  margin-bottom: 10px;
  background-color: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid transparent;
}

.cluster-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
}

.cluster-item.active {
  background: linear-gradient(90deg, rgba(74, 167, 255, 0.2), rgba(52, 152, 219, 0.35));
  border-color: rgba(74, 167, 255, 0.5);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

.cluster-info {
  flex: 1;
  min-width: 0;
}

.cluster-title {
  font-size: 15px;
  font-weight: 600;
  color: #f3f6f9;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions-btn {
  background-color: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.actions-btn:hover {
  background-color: rgba(255, 255, 255, 0.18);
}
</style>
