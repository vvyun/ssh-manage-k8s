<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建ConfigMap"
    width="60%"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      style="margin-top: 20px"
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入ConfigMap名称" />
      </el-form-item>
      
      <el-form-item label="命名空间">
        <el-input 
          :placeholder="`当前命名空间: ${props.namespace || 'default'}`"
          :value="props.namespace || 'default'"
          disabled
        />
        <div class="form-help-text">使用当前命名空间</div>
      </el-form-item>
      
      <el-form-item label="数据项">
        <el-button @click="addDataItem" type="primary" size="small" plain>添加数据项</el-button>
        <div class="data-list">
          <div 
            v-for="(dataItem, index) in formData.data" 
            :key="index" 
            class="data-item"
          >
            <el-input 
              v-model="dataItem.key" 
              placeholder="键" 
              style="width: 200px; margin-right: 10px"
            />
            <el-input 
              v-model="dataItem.value" 
              placeholder="值" 
              type="textarea"
              :rows="2"
              style="flex: 1; margin-right: 10px"
            />
            <el-button @click="removeDataItem(index)" type="danger" size="small" plain>删除</el-button>
          </div>
        </div>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button 
        type="primary" 
        @click="handleCreate"
        :loading="submitting"
      >
        创建
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createConfigMap } from '../../api/cluster'

const props = defineProps({
  modelValue: Boolean,
  clusterId: String,
  namespace: String
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const submitting = ref(false)

// 表单数据
const formData = ref({
  name: '',
  data: []
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入ConfigMap名称', trigger: 'blur' },
    { min: 1, max: 63, message: '长度在 1 到 63 个字符', trigger: 'blur' }
  ]
}

// 添加数据项
const addDataItem = () => {
  formData.value.data.push({
    key: '',
    value: ''
  })
}

// 删除数据项
const removeDataItem = (index) => {
  formData.value.data.splice(index, 1)
}

// 处理创建
const handleCreate = async () => {
  // 表单验证
  if (!formData.value.name) {
    ElMessage.error('请填写ConfigMap名称')
    return
  }
  
  // 验证数据项
  const validData = {}
  let hasEmpty = false
  formData.value.data.forEach(item => {
    if (item.key && item.value) {
      validData[item.key] = item.value
    } else if (item.key || item.value) {
      hasEmpty = true
    }
  })
  
  if (hasEmpty) {
    ElMessage.error('请填写完整的键值对')
    return
  }
  
  if (Object.keys(validData).length === 0) {
    ElMessage.error('请至少添加一个数据项')
    return
  }
  
  // 构建ConfigMap数据
  const configMapData = {
    name: formData.value.name,
    data: validData
  }
  
  try {
    submitting.value = true
    await createConfigMap(props.clusterId, configMapData, props.namespace)
    ElMessage.success('ConfigMap创建成功')
    handleClose()
    emit('success')
  } catch (error) {
    console.error('创建ConfigMap失败:', error)
    ElMessage.error(`创建ConfigMap失败: ${error.message || error}`)
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  // 重置表单
  formData.value = {
    name: '',
    data: []
  }
}

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    handleClose()
  }
})
</script>

<style scoped>
.data-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.form-help-text {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>