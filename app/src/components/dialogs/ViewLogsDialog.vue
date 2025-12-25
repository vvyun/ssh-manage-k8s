<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`Pod日志 - ${podName}`"
    width="80%"
    @close="handleClose"
  >
    <div class="log-controls">
      <el-select 
        v-model="logLines" 
        style="width: 150px"
        @change="loadLogs"
      >
        <el-option label="50行" :value="50" />
        <el-option label="100行" :value="100" />
        <el-option label="200行" :value="200" />
        <el-option label="500行" :value="500" />
        <el-option label="1000行" :value="1000" />
        <el-option label="全部" :value="null" />
      </el-select>
      <el-button :icon="Refresh" @click="loadLogs">刷新</el-button>
      <el-button :icon="Download" @click="downloadLogs">下载日志</el-button>
    </div>
    
    <div class="log-content">
      <pre v-if="loading">加载中...</pre>
      <pre v-else-if="logs">{{ logs }}</pre>
      <pre v-else>无日志输出</pre>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Refresh, Download } from '@element-plus/icons-vue'
import { getPodLogs } from '../../api/cluster'

const props = defineProps({
  modelValue: Boolean,
  clusterId: String,
  namespace: String,
  podName: String
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)
const loading = ref(false)
const logs = ref('')
const logLines = ref(100)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    loadLogs()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const loadLogs = async () => {
  if (!props.clusterId || !props.namespace || !props.podName) return
  
  loading.value = true
  try {
    const result = await getPodLogs(
      props.clusterId,
      props.podName,
      props.namespace,
      logLines.value
    )
    logs.value = result.logs || '无日志输出'
  } catch (error) {
    logs.value = '加载日志失败: ' + error.message
  } finally {
    loading.value = false
  }
}

const downloadLogs = () => {
  if (!logs.value || logs.value === '加载中...' || logs.value === '无日志输出') {
    return
  }
  
  const blob = new Blob([logs.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  a.download = `${props.podName}_${timestamp}.log`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const handleClose = () => {
  dialogVisible.value = false
  logs.value = ''
}
</script>

<style scoped>
.log-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.log-content {
  background-color: #1e1e1e;
  border-radius: 4px;
  padding: 15px;
  max-height: 500px;
  overflow-y: auto;
}

.log-content pre {
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>


