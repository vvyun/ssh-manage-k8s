<template>
  <div class="ingresses-table">
    <div class="table-header">
      <el-button 
        type="primary" 
        :icon="Plus" 
        @click="handleCreate"
        style="margin-bottom: 16px;"
      >
        创建Ingress
      </el-button>
      <el-button 
        :icon="Refresh" 
        @click="loadData"
        style="margin-bottom: 16px; margin-left: 8px;"
      >
        刷新
      </el-button>
    </div>
    
    <el-table 
      :data="ingresses" 
      v-loading="loading"
      style="width: 100%"
      :default-sort="{ prop: 'AGE', order: 'descending' }"
    >
      <el-table-column prop="NAME" label="名称" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <el-link type="primary" @click="handleViewDetail(row)">{{ row.NAME }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="CLASS" label="类别" min-width="120" show-overflow-tooltip />
      <el-table-column prop="HOSTS" label="主机" min-width="200" show-overflow-tooltip />
      <el-table-column prop="ADDRESS" label="地址" min-width="150" show-overflow-tooltip />
      <el-table-column prop="AGE" label="年龄" min-width="120" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="handleViewDetail(row)">查看</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-if="total > pageSize"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[10, 20, 50, 100]"
      :page-size="pageSize"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      style="margin-top: 16px; justify-content: center; display: flex;"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { getIngresses } from '../api/cluster'

const props = defineProps({
  clusterId: {
    type: String,
    required: true
  },
  namespace: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['refresh'])

const ingresses = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 加载Ingress数据
const loadData = async () => {
  if (!props.clusterId || !props.namespace) return
  
  loading.value = true
  try {
    const response = await getIngresses(props.clusterId, props.namespace)
    ingresses.value = response
    
    // 计算总数（如果需要分页）
    total.value = response.length
  } catch (error) {
    console.error('获取Ingress列表失败:', error)
    ElMessage.error(`获取Ingress列表失败: ${error.message || error}`)
  } finally {
    loading.value = false
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadData()
}

// 处理创建按钮点击
const handleCreate = () => {
  ElMessage.info('创建Ingress功能待实现')
}

// 处理查看详情
const handleViewDetail = (row) => {
  ElMessage.info(`查看Ingress ${row.NAME} 详情功能待实现`)
}

// 处理删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认要删除Ingress "${row.NAME}" 吗？此操作无法撤销！`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info(`删除Ingress ${row.NAME} 功能待实现`)
    // 实际删除后重新加载数据
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`删除Ingress失败: ${error.message || error}`)
    }
  }
}

// 初始化加载数据
onMounted(() => {
  loadData()
})

// 暴露方法给父组件
defineExpose({
  loadData
})
</script>

<style scoped>
.ingresses-table {
  padding: 16px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>