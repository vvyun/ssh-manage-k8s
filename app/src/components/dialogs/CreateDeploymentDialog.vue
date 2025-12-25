<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建Deployment"
    width="60%"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="表单创建" name="form">
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="120px"
          style="margin-top: 20px"
        >
          <el-form-item label="名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入Deployment名称" />
          </el-form-item>
          
          <el-form-item label="命名空间">
            <el-input 
              :placeholder="`当前命名空间: ${props.namespace || 'default'}`"
              :value="props.namespace || 'default'"
              disabled
            />
            <div class="form-help-text">使用当前命名空间</div>
          </el-form-item>
          
          <el-form-item label="镜像" prop="image">
            <el-input v-model="formData.image" placeholder="请输入容器镜像" />
          </el-form-item>
          
          <el-form-item label="副本数" prop="replicas">
            <el-input-number v-model="formData.replicas" :min="1" :max="100" />
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
                  v-model="port.containerPort" 
                  placeholder="容器端口" 
                  style="width: 120px; margin-right: 10px"
                />
                <el-input 
                  v-model="port.servicePort" 
                  placeholder="服务端口" 
                  style="width: 120px; margin-right: 10px"
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
          
          <el-form-item label="环境变量">
            <el-button @click="addEnvVar" type="primary" size="small" plain>添加环境变量</el-button>
            <div class="env-list">
              <div 
                v-for="(env, index) in formData.env" 
                :key="index" 
                class="env-item"
              >
                <el-input 
                  v-model="env.name" 
                  placeholder="变量名" 
                  style="width: 150px; margin-right: 10px"
                />
                <el-input 
                  v-model="env.value" 
                  placeholder="变量值" 
                  style="width: 200px; margin-right: 10px"
                />
                <el-button @click="removeEnvVar(index)" type="danger" size="small" plain>删除</el-button>
              </div>
            </div>
          </el-form-item>
          
          <el-form-item label="挂载卷">
            <el-button @click="addVolume" type="primary" size="small" plain>添加挂载</el-button>
            <div class="volume-list">
              <div 
                v-for="(volume, index) in formData.volumes" 
                :key="index" 
                class="volume-item"
              >
                <el-input 
                  v-model="volume.name" 
                  placeholder="卷名" 
                  style="width: 120px; margin-right: 10px"
                />
                <el-input 
                  v-model="volume.mountPath" 
                  placeholder="挂载路径" 
                  style="width: 150px; margin-right: 10px"
                />
                <el-input 
                  v-model="volume.volumePath" 
                  placeholder="卷路径" 
                  style="width: 150px; margin-right: 10px"
                />
                <el-button @click="removeVolume(index)" type="danger" size="small" plain>删除</el-button>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="YAML创建" name="yaml">
        <div style="margin-top: 20px">
          <div class="yaml-input-header">
            <span>Deployment YAML</span>
            <el-button 
              @click="formatYaml" 
              type="primary" 
              size="small"
              :disabled="!yamlContent.trim()"
            >
              格式化
            </el-button>
          </div>
          <el-input
            v-model="yamlContent"
            type="textarea"
            :rows="15"
            placeholder="在此输入Deployment的YAML配置..."
            style="margin-top: 10px"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
    
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
import { createDeployment } from '../../api/cluster'

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

const activeTab = ref('form')
const submitting = ref(false)

// 表单数据
const formData = ref({
  name: '',
  namespace: '',
  image: '',
  replicas: 1,
  ports: [],
  env: [],
  volumes: []
})

// YAML数据
const yamlContent = ref('')

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入Deployment名称', trigger: 'blur' },
    { min: 1, max: 63, message: '长度在 1 到 63 个字符', trigger: 'blur' }
  ],
  image: [
    { required: true, message: '请输入容器镜像', trigger: 'blur' }
  ],
  replicas: [
    { required: true, message: '请输入副本数', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '副本数必须在 1 到 100 之间', trigger: 'blur' }
  ]
}

// 添加端口
const addPort = () => {
  formData.value.ports.push({
    containerPort: '',
    servicePort: '',
    protocol: 'TCP'
  })
}

// 删除端口
const removePort = (index) => {
  formData.value.ports.splice(index, 1)
}

// 添加环境变量
const addEnvVar = () => {
  formData.value.env.push({
    name: '',
    value: ''
  })
}

// 删除环境变量
const removeEnvVar = (index) => {
  formData.value.env.splice(index, 1)
}

// 添加挂载卷
const addVolume = () => {
  formData.value.volumes.push({
    name: '',
    mountPath: '',
    volumePath: ''
  })
}

// 删除挂载卷
const removeVolume = (index) => {
  formData.value.volumes.splice(index, 1)
}

// 处理创建
const handleCreate = async () => {
  if (activeTab.value === 'form') {
    // 表单验证
    if (!formData.value.name || !formData.value.image) {
      ElMessage.error('请填写必填字段')
      return
    }
    
    // 使用表单数据创建Deployment
    const deploymentData = {
      name: formData.value.name,
      image: formData.value.image,
      replicas: formData.value.replicas,
      ports: formData.value.ports,
      env: formData.value.env,
      volumes: formData.value.volumes
    }
    
    try {
      submitting.value = true
      await createDeployment(props.clusterId, deploymentData, props.namespace)
      ElMessage.success('Deployment创建成功')
      handleClose()
      emit('success')
    } catch (error) {
      console.error('创建Deployment失败:', error)
      ElMessage.error(`创建Deployment失败: ${error.message || error}`)
    } finally {
      submitting.value = false
    }
  } else {
    // YAML创建
    if (!yamlContent.value.trim()) {
      ElMessage.error('请输入YAML内容')
      return
    }
    
    try {
      submitting.value = true
      await createDeployment(props.clusterId, { yaml: yamlContent.value }, props.namespace)
      ElMessage.success('Deployment创建成功')
      handleClose()
      emit('success')
    } catch (error) {
      console.error('创建Deployment失败:', error)
      ElMessage.error(`创建Deployment失败: ${error.message || error}`)
    } finally {
      submitting.value = false
    }
  }
}

// 格式化YAML
const formatYaml = () => {
  try {
    // 这里可以添加YAML格式化逻辑
    // 目前简单地美化缩进
    const formatted = yamlContent.value
    // 可以在这里添加更复杂的格式化逻辑
    yamlContent.value = formatted
  } catch (e) {
    ElMessage.error('YAML格式不正确')
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  // 重置表单
  formData.value = {
    name: '',
    namespace: '',
    image: '',
    replicas: 1,
    ports: [],
    env: [],
    volumes: []
  }
  yamlContent.value = ''
  activeTab.value = 'form'
}

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    handleClose()
  }
})
</script>

<style scoped>
.port-item, .env-item, .volume-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.form-help-text {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.yaml-input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>