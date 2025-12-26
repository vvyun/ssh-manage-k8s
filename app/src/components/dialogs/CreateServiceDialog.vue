<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建Service"
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
        <el-input v-model="formData.name" placeholder="请输入Service名称" />
      </el-form-item>
      
      <el-form-item label="命名空间">
        <el-input 
          :placeholder="`当前命名空间: ${props.namespace || 'default'}`"
          :value="props.namespace || 'default'"
          disabled
        />
        <div class="form-help-text">使用当前命名空间</div>
      </el-form-item>
      
      <el-form-item label="类型" prop="type">
        <el-select v-model="formData.type" placeholder="请选择Service类型">
          <el-option label="ClusterIP" value="ClusterIP" />
          <el-option label="NodePort" value="NodePort" />
          <el-option label="LoadBalancer" value="LoadBalancer" />
          <el-option label="ExternalName" value="ExternalName" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="选择器">
        <el-button @click="addSelector" type="primary" size="small" plain>添加选择器</el-button>
        <div class="selector-list">
          <div 
            v-for="(selector, index) in formData.selector" 
            :key="index" 
            class="selector-item"
          >
            <el-input 
              v-model="selector.key" 
              placeholder="键" 
              style="width: 150px; margin-right: 10px"
            />
            <el-input 
              v-model="selector.value" 
              placeholder="值" 
              style="width: 150px; margin-right: 10px"
            />
            <el-button @click="removeSelector(index)" type="danger" size="small" plain>删除</el-button>
          </div>
        </div>
      </el-form-item>
      
      <el-form-item label="端口映射">
        <el-button @click="addPort" type="primary" size="small" plain>添加端口</el-button>
        <div class="port-list">
          <div 
            v-for="(port, index) in formData.ports" 
            :key="index" 
            class="port-item"
          >
            <el-input 
              v-model="port.port" 
              placeholder="服务端口" 
              style="width: 120px; margin-right: 10px"
            />
            <el-input 
              v-model="port.targetPort" 
              placeholder="目标端口" 
              style="width: 120px; margin-right: 10px"
            />
            <el-input 
              v-model="port.nodePort" 
              placeholder="NodePort(可选)" 
              style="width: 120px; margin-right: 10px"
              v-if="formData.type === 'NodePort' || formData.type === 'LoadBalancer'"
            />
            <el-select 
              v-model="port.protocol" 
              placeholder="协议" 
              style="width: 100px; margin-right: 10px"
            >
              <el-option label="TCP" value="TCP" />
              <el-option label="UDP" value="UDP" />
            </el-select>
            <el-button @click="removePort(index)" type="danger" size="small" plain>删除</el-button>
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
import { createService } from '../../api/cluster'

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
  type: 'ClusterIP',
  selector: [],
  ports: []
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入Service名称', trigger: 'blur' },
    { min: 1, max: 63, message: '长度在 1 到 63 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择Service类型', trigger: 'change' }
  ]
}

// 添加选择器
const addSelector = () => {
  formData.value.selector.push({
    key: '',
    value: ''
  })
}

// 删除选择器
const removeSelector = (index) => {
  formData.value.selector.splice(index, 1)
}

// 添加端口
const addPort = () => {
  formData.value.ports.push({
    port: '',
    targetPort: '',
    nodePort: '',
    protocol: 'TCP'
  })
}

// 删除端口
const removePort = (index) => {
  formData.value.ports.splice(index, 1)
}

// 处理创建
const handleCreate = async () => {
  // 表单验证
  if (!formData.value.name) {
    ElMessage.error('请填写Service名称')
    return
  }
  
  // 构建选择器对象
  const selector = {}
  formData.value.selector.forEach(item => {
    if (item.key && item.value) {
      selector[item.key] = item.value
    }
  })
  
  // 构建端口数据
  const ports = formData.value.ports
    .filter(port => port.port && port.targetPort)
    .map(port => {
      const portObj = {
        port: parseInt(port.port),
        targetPort: parseInt(port.targetPort),
        protocol: port.protocol
      }
      
      // 只有在NodePort或LoadBalancer类型时才添加nodePort
      if ((formData.value.type === 'NodePort' || formData.value.type === 'LoadBalancer') && port.nodePort) {
        portObj.nodePort = parseInt(port.nodePort)
      }
      
      // 添加名称（可选）
      if (port.name) {
        portObj.name = port.name
      }
      
      return portObj
    })
  
  // 构建Service数据
  const serviceData = {
    name: formData.value.name,
    type: formData.value.type,
    selector: selector,
    ports: ports
  }
  
  try {
    submitting.value = true
    await createService(props.clusterId, serviceData, props.namespace)
    ElMessage.success('Service创建成功')
    handleClose()
    emit('success')
  } catch (error) {
    console.error('创建Service失败:', error)
    ElMessage.error(`创建Service失败: ${error.message || error}`)
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
    type: 'ClusterIP',
    selector: [],
    ports: []
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
.selector-item, .port-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.form-help-text {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>