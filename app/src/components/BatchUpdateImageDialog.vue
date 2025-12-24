<template>
  <el-dialog
    v-model="dialogVisible"
    title="更新镜像"
    width="80%"
    @close="handleClose"
  >
    <div class="batch-update-container">
      <el-form :inline="true">
        <el-form-item label="镜像名称">
          <el-input 
            v-model="imageName" 
            placeholder="请输入镜像名称..."
            style="width: 300px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchDeployments" :loading="searching">
            查询
          </el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="searching" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <div v-else-if="deployments.length > 0" class="deployments-result">
        <div
          v-for="dep in deployments"
          :key="dep.name"
          class="deployment-item"
        >
          <div class="deployment-info">
            <h4>{{ dep.name }}</h4>
            <p>命名空间: {{ dep.namespace }} | 当前镜像: {{ dep.image }}</p>
          </div>
          <div class="deployment-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="updateDeployment(dep)"
              :loading="updating[dep.name]"
            >
              更新
            </el-button>
          </div>
        </div>
      </div>
      
      <div v-else-if="searched" class="empty-state">
        <p>未找到匹配的工作负载</p>
      </div>
      
      <div v-else class="hint-state">
        <p>请输入镜像名称并点击查询</p>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { searchDeploymentsByImage, updateDeploymentImage } from '../api/cluster'

const props = defineProps({
  modelValue: Boolean,
  clusterId: String,
  namespace: String
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)
const imageName = ref('')
const searching = ref(false)
const searched = ref(false)
const deployments = ref([])
const updating = ref({})

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (!val) {
    imageName.value = ''
    deployments.value = []
    searched.value = false
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const searchDeployments = async () => {
  if (!imageName.value.trim()) {
    ElMessage.warning('请输入镜像名称')
    return
  }
  
  if (!props.clusterId) {
    ElMessage.warning('未选择集群')
    return
  }
  
  searching.value = true
  searched.value = true
  
  try {
    const result = await searchDeploymentsByImage(
      props.clusterId,
      imageName.value.trim(),
      props.namespace
    )
    deployments.value = result.deployments || []
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
    deployments.value = []
  } finally {
    searching.value = false
  }
}

const updateDeployment = async (deployment) => {
  updating.value[deployment.name] = true
  
  try {
    await updateDeploymentImage(
      props.clusterId,
      deployment.name,
      imageName.value.trim(),
      props.namespace
    )
    ElMessage.success('镜像更新成功')
    // 从列表中移除已更新的部署
    deployments.value = deployments.value.filter(d => d.name !== deployment.name)
  } catch (error) {
    ElMessage.error('镜像更新失败: ' + error.message)
  } finally {
    updating.value[deployment.name] = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.batch-update-container {
  min-height: 300px;
}

.loading-state,
.empty-state,
.hint-state {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.deployments-result {
  max-height: 400px;
  overflow-y: auto;
}

.deployment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.deployment-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.deployment-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.deployment-actions {
  flex-shrink: 0;
}
</style>


