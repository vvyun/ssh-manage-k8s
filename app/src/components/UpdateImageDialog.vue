<template>
  <el-dialog
    v-model="dialogVisible"
    title="更新部署镜像"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="部署名称">
        <el-input :value="props.deploymentName" disabled />
      </el-form-item>
      <el-form-item label="镜像名称" prop="image">
        <el-input 
          v-model="form.image" 
          placeholder="请输入新的镜像名称"
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
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { updateDeploymentImage } from '../api/cluster'

const props = defineProps({
  modelValue: Boolean,
  clusterId: String,
  namespace: String,
  deploymentName: String
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(props.modelValue)
const formRef = ref()
const loading = ref(false)

const form = reactive({
  image: ''
})

const rules = {
  image: [
    { required: true, message: '请输入镜像名称', trigger: 'blur' }
  ]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
  form.image = ''
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await updateDeploymentImage(
        props.clusterId,
        props.deploymentName,
        form.image,
        props.namespace
      )
      ElMessage.success('镜像更新成功')
      emit('success')
      handleClose()
    } catch (error) {
      ElMessage.error('镜像更新失败: ' + error.message)
    } finally {
      loading.value = false
    }
  })
}
</script>


