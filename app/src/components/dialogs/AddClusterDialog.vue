<template>
  <el-dialog
    v-model="dialogVisible"
    title="添加新集群"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      label-position="left"
    >
      <el-form-item label="连接方式" prop="k8s_controller">
        <el-select v-model="form.k8s_controller" style="width: 100%">
          <el-option label="kubeconfig" value="KUBE" />
          <el-option label="SSH（适用于仅能通过跳板机访问集群）" value="SSH" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="集群名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入集群名称" />
      </el-form-item>
      
      <el-form-item label="默认命名空间" prop="namespace">
        <el-input v-model="form.namespace" placeholder="default" />
      </el-form-item>
      
      <!-- SSH 配置 -->
      <template v-if="form.k8s_controller === 'SSH'">
        <el-divider content-position="left">SSH 认证</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="SSH主机" prop="ssh_config.hostname">
              <el-input v-model="form.ssh_config.hostname" placeholder="请输入主机地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SSH端口" prop="ssh_config.port">
              <el-input-number v-model="form.ssh_config.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="SSH用户名" prop="ssh_config.username">
              <el-input v-model="form.ssh_config.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SSH密码" prop="ssh_config.password">
              <el-input 
                v-model="form.ssh_config.password" 
                type="password" 
                placeholder="请输入密码（可选）"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="SSH密钥路径" prop="ssh_config.key_path">
          <el-input v-model="form.ssh_config.key_path" placeholder="请输入密钥路径（可选）" />
        </el-form-item>
      </template>
      
      <!-- KUBE 配置 -->
      <template v-if="form.k8s_controller === 'KUBE'">
        <el-divider content-position="left">KUBE 认证</el-divider>
        <el-form-item label="kubeconfig 路径" prop="kube_config">
          <el-input 
            v-model="form.kube_config" 
            placeholder="不填写则使用默认路径 ~/.kube/config"
          />
        </el-form-item>
      </template>
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
import { addCluster } from '../../api/cluster'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(props.modelValue)
const formRef = ref()
const loading = ref(false)

const form = reactive({
  name: '',
  namespace: 'default',
  k8s_controller: 'KUBE',
  ssh_config: {
    hostname: '',
    port: 22,
    username: '',
    password: '',
    key_path: ''
  },
  kube_config: ''
})

const rules = {
  name: [
    { required: true, message: '请输入集群名称', trigger: 'blur' }
  ],
  namespace: [
    { required: true, message: '请输入默认命名空间', trigger: 'blur' }
  ],
  'ssh_config.hostname': [
    { 
      required: true, 
      message: '请输入SSH主机地址', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.k8s_controller === 'SSH' && !value) {
          callback(new Error('请输入SSH主机地址'))
        } else {
          callback()
        }
      }
    }
  ],
  'ssh_config.username': [
    {
      required: true,
      message: '请输入SSH用户名',
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.k8s_controller === 'SSH' && !value) {
          callback(new Error('请输入SSH用户名'))
        } else {
          callback()
        }
      }
    }
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
  Object.assign(form, {
    name: '',
    namespace: 'default',
    k8s_controller: 'KUBE',
    ssh_config: {
      hostname: '',
      port: 22,
      username: '',
      password: '',
      key_path: ''
    },
    kube_config: ''
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const clusterData = {
        name: form.name,
        namespace: form.namespace,
        k8s_controller: form.k8s_controller
      }
      
      if (form.k8s_controller === 'SSH') {
        clusterData.ssh_config = {
          hostname: form.ssh_config.hostname,
          port: form.ssh_config.port,
          username: form.ssh_config.username,
          password: form.ssh_config.password || '',
          key_path: form.ssh_config.key_path || ''
        }
      } else if (form.k8s_controller === 'KUBE') {
        clusterData.kube_config = form.kube_config || null
      }
      
      await addCluster(clusterData)
      ElMessage.success('集群添加成功')
      emit('success')
      handleClose()
    } catch (error) {
      ElMessage.error('添加集群失败: ' + error.message)
    } finally {
      loading.value = false
    }
  })
}
</script>


