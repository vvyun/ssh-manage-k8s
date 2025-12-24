<template>
  <el-dialog
    v-model="dialogVisible"
    title="容器伸缩"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="部署名称">
        <el-input v-model="deploymentName" disabled />
      </el-form-item>
      <el-form-item label="当前副本数">
        <el-input v-model="currentReplicas" disabled />
      </el-form-item>
      <el-form-item label="目标副本数" prop="replicas">
        <el-input-number 
          v-model="form.replicas" 
          :min="0"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { scaleDeployment } from '../api/cluster'

const props = defineProps({
  modelValue: Boolean,
  clusterId: String,
  namespace: String,
  deployment: [Object, String]
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(props.modelValue)
const formRef = ref()
const loading = ref(false)

const deploymentName = computed(() => {
  if (typeof props.deployment === 'string') {
    return props.deployment
  }
  return props.deployment?.NAME || ''
})

const currentReplicas = computed(() => {
  if (typeof props.deployment === 'string') {
    return '0'
  }
  const ready = props.deployment?.READY || '0/0'
  return ready.split('/')[1] || '0'
})

const form = reactive({
  replicas: parseInt(currentReplicas.value) || 0
})

const rules = {
  replicas: [
    { required: true, message: '请输入目标副本数', trigger: 'blur' },
    { type: 'number', min: 0, message: '副本数必须大于等于0', trigger: 'blur' }
  ]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    form.replicas = parseInt(currentReplicas.value) || 0
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await scaleDeployment(
        props.clusterId,
        deploymentName.value,
        form.replicas,
        props.namespace
      )
      ElMessage.success(`容器伸缩成功，目标副本数: ${form.replicas}`)
      emit('success')
      handleClose()
    } catch (error) {
      ElMessage.error('容器伸缩失败: ' + error.message)
    } finally {
      loading.value = false
    }
  })
}
</script>


