<template>
  <el-container class="app-container">
    <el-aside class="main-sidebar">
      <ClusterSidebar />
    </el-aside>
    <el-container class="main-content">
      <router-view />
    </el-container>
  </el-container>
</template>

<script setup>
import ClusterSidebar from './components/ClusterSidebar.vue'
</script>

<style scoped>
.app-container {
  height: 98vh;
  width: 100%;
  display: flex;
  margin: 0;
  padding: 0;
}

.main-sidebar {
  height: 100%;
}

.main-content {
  height: 100%;
}
</style>
