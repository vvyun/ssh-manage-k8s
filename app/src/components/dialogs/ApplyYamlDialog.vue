<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="60%"
    :before-close="handleClose"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
      <el-form-item label="YAML内容" prop="yaml">
        <el-input
          v-model="form.yaml"
          type="textarea"
          :rows="20"
          placeholder="请输入YAML内容"
          resize="vertical"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">应用</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { createFromYaml } from '@/api/cluster'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  clusterId: {
    type: String,
    required: true
  },
  namespace: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(props.modelValue)
const formRef = ref()
const loading = ref(false)

const form = reactive({
  yaml: ''
})

const rules = {
  yaml: [
    { required: true, message: '请输入YAML内容', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value) {
          try {
            // 简单验证YAML格式
            const yamlLines = value.trim().split('\n')
            if (yamlLines.length > 0) {
              callback()
            } else {
              callback(new Error('YAML内容格式不正确'))
            }
          } catch (e) {
            callback(new Error('YAML内容格式不正确'))
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    // 重置表单
    nextTick(() => {
      formRef.value?.resetFields()
      form.yaml = ''
    })
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
  form.yaml = ''
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await createFromYaml(
        props.clusterId,
        form.yaml,
        props.namespace
      )
      ElMessage.success('YAML应用成功')
      emit('success')
      handleClose()
    } catch (error) {
      ElMessage.error('YAML应用失败: ' + error.message)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>