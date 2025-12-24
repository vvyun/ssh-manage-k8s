<template>
  <el-container class="app-container">
    <el-aside width="280px" class="sidebar">
      <ClusterSidebar />
    </el-aside>
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import ClusterSidebar from './components/ClusterSidebar.vue'
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #233445 0%, #1c2633 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.main-content {
  background: linear-gradient(180deg, #f7f9fc 0%, #eef2f7 100%);
  padding: 24px;
}
</style>


