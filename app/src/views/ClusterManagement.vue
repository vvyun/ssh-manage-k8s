<template>
  <div class="cluster-management">
    <div v-if="!currentCluster" class="empty-cluster">
      <el-empty description="请先选择一个集群" />
    </div>
    
    <template v-else>
      <!-- 命名空间选择器 -->
      <div class="namespace-selector">
        <el-select 
          v-model="currentNamespace" 
          placeholder="选择命名空间"
          style="width: 200px"
          @change="handleNamespaceChange"
        >
          <el-option
            v-for="ns in namespaces"
            :key="ns.NAME"
            :label="ns.NAME"
            :value="ns.NAME"
          />
        </el-select>
        <el-button 
          type="primary" 
          :icon="Refresh"
          @click="loadCurrentTabData"
        >
          刷新
        </el-button>
        <el-button 
          type="success"
          @click="showBatchUpdateDialog = true"
        >
          快速更新镜像
        </el-button>
      </div>
      
      <!-- Tab导航 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="工作负载" name="deployments">
          <DeploymentsTable 
            :cluster-id="clusterId"
            :namespace="currentNamespace"
            @refresh="loadCurrentTabData"
          />
        </el-tab-pane>
        <el-tab-pane label="服务" name="services">
          <ServicesTable 
            :cluster-id="clusterId"
            :namespace="currentNamespace"
          />
        </el-tab-pane>
        <el-tab-pane label="Pods" name="pods">
          <PodsTable 
            :cluster-id="clusterId"
            :namespace="currentNamespace"
            @refresh="loadCurrentTabData"
          />
        </el-tab-pane>
      </el-tabs>
    </template>
    
    <!-- 批量更新镜像对话框 -->
    <BatchUpdateImageDialog
      v-model="showBatchUpdateDialog"
      :cluster-id="clusterId"
      :namespace="currentNamespace"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Refresh } from '@element-plus/icons-vue'
import { getNamespaces } from '../api/cluster'
import DeploymentsTable from '../components/DeploymentsTable.vue'
import ServicesTable from '../components/ServicesTable.vue'
import PodsTable from '../components/PodsTable.vue'
import BatchUpdateImageDialog from '../components/BatchUpdateImageDialog.vue'

const store = useStore()

const activeTab = ref('deployments')
const namespaces = ref([])
const showBatchUpdateDialog = ref(false)

const currentCluster = computed(() => store.state.currentCluster)
const currentNamespace = computed({
  get: () => store.state.currentNamespace,
  set: (val) => store.commit('SET_CURRENT_NAMESPACE', val)
})

const clusterId = computed(() => {
  if (!currentCluster.value) return null
  return (currentCluster.value.name || '').toLowerCase().replace(/\s+/g, '-')
})

const loadNamespaces = async () => {
  if (!clusterId.value) return
  
  try {
    const data = await getNamespaces(clusterId.value)
    namespaces.value = Array.isArray(data) ? data : []
    
    // 设置默认命名空间
    const defaultNs = namespaces.value.find(ns => ns.SELECT) || 
                     namespaces.value[0] || 
                     { NAME: 'default' }
    currentNamespace.value = defaultNs.NAME
  } catch (error) {
    console.error('加载命名空间失败:', error)
  }
}

const handleNamespaceChange = () => {
  loadCurrentTabData()
}

const handleTabChange = () => {
  loadCurrentTabData()
}

const loadCurrentTabData = () => {
  // 触发子组件刷新
  // 子组件会监听 props 变化自动刷新
}

watch(() => currentCluster.value, (newCluster) => {
  if (newCluster) {
    loadNamespaces()
  } else {
    namespaces.value = []
  }
}, { immediate: true })

onMounted(() => {
  if (currentCluster.value) {
    loadNamespaces()
  }
})
</script>

<style scoped>
.cluster-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-cluster {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.namespace-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.05);
  border: 1px solid #e6ecf3;
  margin-bottom: 16px;
}

:deep(.el-tabs) {
  background: #ffffff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 16px 40px rgba(17, 24, 39, 0.08);
  border: 1px solid #e5ecf5;
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}
</style>


