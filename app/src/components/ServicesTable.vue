<template>
  <div class="services-table">
    <div class="table-header">
      <el-input
        v-model="filterText"
        placeholder="按名称筛选服务..."
        :prefix-icon="Search"
        clearable
        style="width: 300px"
      />
    </div>
    
    <el-table
      :data="paginatedData"
      v-loading="loading"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'NAME', order: 'ascending' }"
    >
      <el-table-column prop="NAME" label="名称" sortable min-width="200" />
      <el-table-column prop="TYPE" label="类型" width="120" />
      <el-table-column prop="CLUSTER_IP" label="集群IP" width="150" />
      <el-table-column prop="PORTS" label="端口" min-width="200" />
      <el-table-column prop="AGE" label="年龄" width="120" />
    </el-table>
    
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getServices } from '../api/cluster'

const props = defineProps({
  clusterId: String,
  namespace: String
})

const loading = ref(false)
const data = ref([])
const filterText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  if (!filterText.value) return data.value
  const keyword = filterText.value.toLowerCase()
  return data.value.filter(item => 
    (item.NAME || '').toLowerCase().includes(keyword)
  )
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const loadData = async () => {
  if (!props.clusterId || !props.namespace) return
  
  loading.value = true
  try {
    const result = await getServices(props.clusterId, props.namespace)
    data.value = Array.isArray(result) ? result : []
    currentPage.value = 1
  } catch (error) {
    console.error('加载服务失败:', error)
    data.value = []
  } finally {
    loading.value = false
  }
}

watch([() => props.clusterId, () => props.namespace], () => {
  loadData()
}, { immediate: true })

watch(() => filterText.value, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.services-table {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-header {
  margin-bottom: 15px;
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}
</style>


