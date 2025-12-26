<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建Ingress"
    width="70%"
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
        <el-input v-model="formData.name" placeholder="请输入Ingress名称" />
      </el-form-item>
      
      <el-form-item label="命名空间">
        <el-input 
          :placeholder="`当前命名空间: ${props.namespace || 'default'}`"
          :value="props.namespace || 'default'"
          disabled
        />
        <div class="form-help-text">使用当前命名空间</div>
      </el-form-item>
      
      <el-form-item label="Ingress类">
        <el-input v-model="formData.ingressClassName" placeholder="例如: nginx" />
      </el-form-item>
      
      <el-form-item label="规则">
        <el-button @click="addRule" type="primary" size="small" plain>添加规则</el-button>
        <div class="rule-list">
          <div 
            v-for="(rule, ruleIndex) in formData.rules" 
            :key="ruleIndex" 
            class="rule-item"
          >
            <div class="rule-header">
              <span>规则 {{ ruleIndex + 1 }}</span>
              <el-button @click="removeRule(ruleIndex)" type="danger" size="small" plain>删除规则</el-button>
            </div>
            
            <el-form-item label="主机" style="margin-top: 10px;">
              <el-input v-model="rule.host" placeholder="例如: example.com" style="width: 100%;" />
            </el-form-item>
            
            <el-form-item label="路径" style="margin-top: 10px;">
              <el-button @click="addPath(ruleIndex)" type="primary" size="small" plain>添加路径</el-button>
              <div class="path-list">
                <div 
                  v-for="(path, pathIndex) in rule.paths" 
                  :key="pathIndex" 
                  class="path-item"
                >
                  <el-input 
                    v-model="path.path" 
                    placeholder="路径" 
                    style="width: 150px; margin-right: 10px"
                  />
                  <el-select 
                    v-model="path.pathType" 
                    placeholder="路径类型" 
                    style="width: 120px; margin-right: 10px"
                  >
                    <el-option label="Prefix" value="Prefix" />
                    <el-option label="Exact" value="Exact" />
                    <el-option label="ImplementationSpecific" value="ImplementationSpecific" />
                  </el-select>
                  <el-input 
                    v-model="path.serviceName" 
                    placeholder="服务名称" 
                    style="width: 150px; margin-right: 10px"
                  />
                  <el-input 
                    v-model="path.servicePort" 
                    placeholder="服务端口" 
                    style="width: 100px; margin-right: 10px"
                  />
                  <el-button @click="removePath(ruleIndex, pathIndex)" type="danger" size="small" plain>删除</el-button>
                </div>
              </div>
            </el-form-item>
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
import { createIngress } from '../../api/cluster'

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
  ingressClassName: '',
  rules: []
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入Ingress名称', trigger: 'blur' },
    { min: 1, max: 63, message: '长度在 1 到 63 个字符', trigger: 'blur' }
  ]
}

// 添加规则
const addRule = () => {
  formData.value.rules.push({
    host: '',
    paths: [{
      path: '/',
      pathType: 'Prefix',
      serviceName: '',
      servicePort: 80
    }]
  })
}

// 删除规则
const removeRule = (index) => {
  formData.value.rules.splice(index, 1)
}

// 为规则添加路径
const addPath = (ruleIndex) => {
  if (!formData.value.rules[ruleIndex].paths) {
    formData.value.rules[ruleIndex].paths = []
  }
  formData.value.rules[ruleIndex].paths.push({
    path: '/',
    pathType: 'Prefix',
    serviceName: '',
    servicePort: 80
  })
}

// 删除路径
const removePath = (ruleIndex, pathIndex) => {
  formData.value.rules[ruleIndex].paths.splice(pathIndex, 1)
}

// 处理创建
const handleCreate = async () => {
  // 表单验证
  if (!formData.value.name) {
    ElMessage.error('请填写Ingress名称')
    return
  }
  
  // 验证规则
  let hasValidRule = false
  for (const rule of formData.value.rules) {
    if (rule.paths && rule.paths.length > 0) {
      for (const path of rule.paths) {
        if (path.path && path.serviceName && path.servicePort) {
          hasValidRule = true
          break
        }
      }
      if (hasValidRule) break
    }
  }
  
  if (!hasValidRule) {
    ElMessage.error('请至少添加一个有效的路径规则')
    return
  }
  
  // 构建Ingress数据
  const ingressData = {
    name: formData.value.name,
    ingressClassName: formData.value.ingressClassName || undefined
  }
  
  // 过滤并构建规则
  const validRules = []
  for (const rule of formData.value.rules) {
    if (rule.paths && rule.paths.length > 0) {
      const validPaths = rule.paths
        .filter(path => path.path && path.serviceName && path.servicePort)
        .map(path => ({
          path: path.path,
          pathType: path.pathType,
          serviceName: path.serviceName,
          servicePort: parseInt(path.servicePort)
        }))
      
      if (validPaths.length > 0) {
        const ruleObj = {
          paths: validPaths
        }
        if (rule.host) {
          ruleObj.host = rule.host
        }
        validRules.push(ruleObj)
      }
    }
  }
  
  if (validRules.length > 0) {
    ingressData.rules = validRules
  }
  
  try {
    submitting.value = true
    await createIngress(props.clusterId, ingressData, props.namespace)
    ElMessage.success('Ingress创建成功')
    handleClose()
    emit('success')
  } catch (error) {
    console.error('创建Ingress失败:', error)
    ElMessage.error(`创建Ingress失败: ${error.message || error}`)
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
    ingressClassName: '',
    rules: []
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
.rule-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.path-item {
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