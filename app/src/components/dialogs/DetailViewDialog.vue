<template>
    <el-dialog v-model="dialogVisible" :title="`${resourceType}详情 - ${resourceName}`" width="80%"
        :destroy-on-close="true" top="5vh">
        <div v-loading="loading">
            <el-tabs v-model="activeTab" class="detail-tabs">
                <el-tab-pane label="详情" name="detail">
                    <div class="yaml-content">
                        <pre>{{ formattedDetail }}</pre>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>

        <template #footer>
            <el-button @click="handleClose">关闭</el-button>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
    getDeploymentDetail,
    getServiceDetail,
    getConfigMapDetail,
    getIngressDetail
} from '../../api/cluster'

const props = defineProps({
    modelValue: Boolean,
    clusterId: String,
    namespace: String,
    resourceName: String,
    resourceType: {
        type: String,
        required: true,
        validator: (value) => ['Deployment', 'Service', 'ConfigMap', 'Ingress'].includes(value)
    }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)
const loading = ref(false)
const detail = ref(null)
const activeTab = ref('detail')

// 根据资源类型获取详情的函数
const fetchDetail = async () => {
    if (!props.clusterId || !props.namespace || !props.resourceName) {
        return
    }

    loading.value = true
    try {
        let result
        switch (props.resourceType) {
            case 'Deployment':
                result = await getDeploymentDetail(props.clusterId, props.resourceName, props.namespace)
                break
            case 'Service':
                result = await getServiceDetail(props.clusterId, props.resourceName, props.namespace)
                break
            case 'ConfigMap':
                result = await getConfigMapDetail(props.clusterId, props.resourceName, props.namespace)
                break
            case 'Ingress':
                result = await getIngressDetail(props.clusterId, props.resourceName, props.namespace)
                break
            default:
                throw new Error(`不支持的资源类型: ${props.resourceType}`)
        }
        detail.value = result
    } catch (error) {
        console.error(`获取${props.resourceType}详情失败:`, error)
        ElMessage.error(`获取${props.resourceType}详情失败: ${error.message || error}`)
    } finally {
        loading.value = false
    }
}

// 格式化详情内容
const formattedDetail = computed(() => {
    if (!detail.value) return ''
    return detail.value.yaml
})


// 监听属性变化，当打开对话框时获取详情
watch(() => props.modelValue, (newVal) => {
    dialogVisible.value = newVal
    if (newVal) {
        fetchDetail()
    } else {
        detail.value = null
        activeTab.value = 'detail'
    }
})

// 监听对话框关闭事件
watch(dialogVisible, (newVal) => {
    if (!newVal) {
        emit('update:modelValue', false)
    }
})

// 关闭对话框
const handleClose = () => {
    dialogVisible.value = false
}
</script>

<style scoped>
.yaml-content {
    max-height: 60vh;
    overflow: auto;
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
}

.yaml-content pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.metadata-content {
    padding: 20px 0;
}

.metadata-content h4 {
    margin: 15px 0 10px 0;
    font-size: 16px;
    font-weight: bold;
}

.label-tag {
    margin-right: 8px;
    margin-bottom: 8px;
}

.annotations-section {
    margin-top: 20px;
}

.annotation-value {
    word-break: break-all;
    max-width: 400px;
    display: inline-block;
}

.detail-tabs :deep(.el-tabs__content) {
    padding: 20px 0;
}
</style>