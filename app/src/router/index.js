import { createRouter, createWebHistory } from 'vue-router'
import ClusterManagement from '../views/ClusterManagement.vue'

const routes = [
  {
    path: '/',
    name: 'ClusterManagement',
    component: ClusterManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router


