<template>
  <div class="cluster-management">

    <div v-if="!currentCluster" class="empty-cluster">
      <el-header>
        <el-empty description="请先选择一个集群" />
      </el-header>
    </div>
    <template v-else>
      <el-header>
        <span size="small">集群 / {{ currentCluster?.name }}</span>
        <!-- 命名空间选择器 -->
        <div class="namespace-selector">
          <span>命名空间:</span>
          <el-select v-model="currentNamespace" placeholder="选择命名空间" style="width: 200px"
            @change="handleNamespaceChange">
            <el-option v-for="ns in namespaces" :key="ns.NAME" :label="ns.NAME" :value="ns.NAME" />
            <template #footer>
              <el-button v-if="!showCreateNamespaceDialog" text bg size="small"
                @click="showCreateNamespaceDialog = true">
                新建命名空间
              </el-button>
              <template v-else>
                <el-input v-model="newNamespaceName" placeholder="请输入命名空间名称" size="small"
                  @keyup.enter="handleCreateNamespace" />
                <el-button type="primary" size="small" @click="handleCreateNamespace">
                  创建
                </el-button>
                <el-button size="small" @click="showCreateNamespaceDialog = false">取消</el-button>
              </template>
            </template>
          </el-select>
          <el-button type="danger" :disabled="!currentNamespace || currentNamespace === 'default'"
            @click="handleDeleteNamespace">删除命名空间</el-button>
          <div class="right-buttons">
            <el-button type="success" @click="showBatchUpdateDialog = true">
              快速更新镜像
            </el-button>
            <el-button type="primary" @click="showApplyYamlDialog = true">
              应用YAML
            </el-button>
            <el-button type="primary" :icon="Refresh" @click="loadCurrentTabData">
              刷新
            </el-button>
          </div>
        </div>

        <!-- Tab导航 -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="Deployments" name="deployments">
            <DeploymentsTable ref="deploymentsTableRef" :cluster-id="clusterId" :namespace="currentNamespace"
              @refresh="loadCurrentTabData" />
          </el-tab-pane>
          <el-tab-pane label="Services" name="services">
            <ServicesTable ref="servicesTableRef" :cluster-id="clusterId" :namespace="currentNamespace" />
          </el-tab-pane>
          <el-tab-pane label="Pods" name="pods">
            <PodsTable ref="podsTableRef" :cluster-id="clusterId" :namespace="currentNamespace"
              @refresh="loadCurrentTabData" />
          </el-tab-pane>
          <el-tab-pane label="ConfigMaps" name="configmaps">
            <ConfigMapsTable ref="configmapsTableRef" :cluster-id="clusterId" :namespace="currentNamespace"
              @refresh="loadCurrentTabData" />
          </el-tab-pane>
          <el-tab-pane label="Ingresses" name="ingresses">
            <IngressesTable ref="ingressesTableRef" :cluster-id="clusterId" :namespace="currentNamespace"
              @refresh="loadCurrentTabData" />
          </el-tab-pane>
        </el-tabs>
      </el-header>
    </template>

    <!-- 批量更新镜像对话框 -->
    <BatchUpdateImageDialog v-model="showBatchUpdateDialog" :cluster-id="clusterId" :namespace="currentNamespace" />

    <!-- 应用YAML对话框 -->
    <ApplyYamlDialog v-model="showApplyYamlDialog" :cluster-id="clusterId" :namespace="currentNamespace" />

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getNamespaces, createNamespace, deleteNamespace } from '../api/cluster'
import DeploymentsTable from '../components/tables/DeploymentsTable.vue'
import ServicesTable from '../components/tables/ServicesTable.vue'
import PodsTable from '../components/tables/PodsTable.vue'
import ConfigMapsTable from '../components/tables/ConfigMapsTable.vue'
import IngressesTable from '../components/tables/IngressesTable.vue'
import BatchUpdateImageDialog from '../components/dialogs/BatchUpdateImageDialog.vue'
import ApplyYamlDialog from '../components/dialogs/ApplyYamlDialog.vue'

const store = useStore()

const activeTab = ref('deployments')
const namespaces = ref([])
const showBatchUpdateDialog = ref(false)
const showApplyYamlDialog = ref(false)
const showCreateNamespaceDialog = ref(false)
const newNamespaceName = ref('')
const deploymentsTableRef = ref(null)
const servicesTableRef = ref(null)
const podsTableRef = ref(null)
const configmapsTableRef = ref(null)
const ingressesTableRef = ref(null)

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

const handleCreateNamespace = async () => {
  if (!newNamespaceName.value.trim()) {
    ElMessage.error('请输入命名空间名称')
    return
  }

  try {
    await createNamespace(clusterId.value, newNamespaceName.value.trim())
    ElMessage.success('命名空间创建成功')
    showCreateNamespaceDialog.value = false
    newNamespaceName.value = ''
    await loadNamespaces() // 重新加载命名空间列表

    // 如果当前没有选择命名空间，自动选择新创建的命名空间
    if (!currentNamespace.value) {
      currentNamespace.value = newNamespaceName.value.trim()
    }
  } catch (error) {
    ElMessage.error(`创建命名空间失败: ${error.message || error}`)
  }
}

const handleDeleteNamespace = async () => {
  try {
    await ElMessageBox.confirm(
      `确认要删除命名空间 "${currentNamespace.value}" 吗？此操作无法撤销！`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteNamespace(clusterId.value, currentNamespace.value)
    ElMessage.success('命名空间删除成功')

    // 重新加载命名空间列表并选择第一个
    await loadNamespaces()
    if (namespaces.value.length > 0) {
      currentNamespace.value = namespaces.value[0].NAME
    } else {
      currentNamespace.value = 'default'
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`删除命名空间失败: ${error.message || error}`)
    }
  }
}

const loadCurrentTabData = () => {
  // 根据当前激活的标签页，调用对应组件的刷新方法
  if (activeTab.value === 'deployments' && deploymentsTableRef.value && deploymentsTableRef.value.loadData) {
    deploymentsTableRef.value.loadData()
  } else if (activeTab.value === 'services' && servicesTableRef.value && servicesTableRef.value.loadData) {
    servicesTableRef.value.loadData()
  } else if (activeTab.value === 'pods' && podsTableRef.value && podsTableRef.value.loadData) {
    podsTableRef.value.loadData()
  } else if (activeTab.value === 'configmaps' && configmapsTableRef.value && configmapsTableRef.value.loadData) {
    configmapsTableRef.value.loadData()
  } else if (activeTab.value === 'ingresses' && ingressesTableRef.value && ingressesTableRef.value.loadData) {
    ingressesTableRef.value.loadData()
  }
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
  width: 100%;
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

.namespace-selector .right-buttons {
  margin-left: auto;
  display: flex;
  gap: 10px;
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
