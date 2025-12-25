import api from './index'

export const getClusters = () => api.get('/clusters')

export const addCluster = (data) => api.post('/clusters', data)

export const updateCluster = (clusterId, data) => api.put(`/clusters/${clusterId}`, data)

export const deleteCluster = (clusterId) => api.delete(`/clusters/${clusterId}`)

export const getNamespaces = (clusterId) => api.get(`/clusters/${clusterId}/namespaces`)

export const createNamespace = (clusterId, namespace) => api.post(`/clusters/${clusterId}/namespaces`, { namespace })

export const deleteNamespace = (clusterId, namespace) => api.delete(`/clusters/${clusterId}/namespaces/${namespace}`)

export const getDeployments = (clusterId, namespace) => 
  api.get(`/clusters/${clusterId}/deployments`, { params: { namespace } })

export const getDeploymentDetail = (clusterId, deploymentName, namespace) =>
  api.get(`/clusters/${clusterId}/deployments/${deploymentName}/detail`, { params: { namespace } })

export const getServiceDetail = (clusterId, serviceName, namespace) =>
  api.get(`/clusters/${clusterId}/services/${serviceName}/detail`, { params: { namespace } })

export const getConfigMapDetail = (clusterId, configMapName, namespace) =>
  api.get(`/clusters/${clusterId}/configmaps/${configMapName}/detail`, { params: { namespace } })

export const getIngressDetail = (clusterId, ingressName, namespace) =>
  api.get(`/clusters/${clusterId}/ingresses/${ingressName}/detail`, { params: { namespace } })

export const getServices = (clusterId, namespace) => 
  api.get(`/clusters/${clusterId}/services`, { params: { namespace } })

export const getPods = (clusterId, namespace) => 
  api.get(`/clusters/${clusterId}/pods`, { params: { namespace } })

export const getConfigmaps = (clusterId, namespace) =>
  api.get(`/clusters/${clusterId}/configmaps`, { params: { namespace } })

export const getIngresses = (clusterId, namespace) =>
  api.get(`/clusters/${clusterId}/ingresses`, { params: { namespace } })

export const updateDeploymentImage = (clusterId, deploymentName, image, namespace) =>
  api.post(`/clusters/${clusterId}/deployments/${deploymentName}/update-image`, 
    { image }, 
    { params: { namespace } }
  )

export const deletePod = (clusterId, podName, namespace) =>
  api.delete(`/clusters/${clusterId}/pods/${podName}`, { params: { namespace } })

export const getPodLogs = (clusterId, podName, namespace, lines) =>
  api.get(`/clusters/${clusterId}/pods/${podName}/logs`, { 
    params: { namespace, lines } 
  })

export const searchDeploymentsByImage = (clusterId, image, namespace) =>
  api.get(`/clusters/${clusterId}/search-deployments-by-image`, {
    params: { image, namespace }
  })

export const scaleDeployment = (clusterId, deploymentName, replicas, namespace) =>
  api.post(`/clusters/${clusterId}/deployments/${deploymentName}/scale`,
    { replicas },
    { params: { namespace } }
  )

// 创建Deployment - 表单模式
export const createDeploymentFromForm = (clusterId, deploymentData, namespace) =>
  api.post(`/clusters/${clusterId}/deployments`, deploymentData, { params: { namespace } })

// 创建Deployment - YAML模式
export const createDeploymentFromYaml = (clusterId, yamlContent, namespace) =>
  api.post(`/clusters/${clusterId}/deployments/yaml`, { yaml: yamlContent }, { params: { namespace } })

// 通用的createDeployment函数，根据参数类型决定使用哪种方式
export const createDeployment = (clusterId, data, namespace) => {
  if (data.yaml !== undefined) {
    // YAML模式
    return createDeploymentFromYaml(clusterId, data.yaml, namespace);
  } else {
    // 表单模式
    return createDeploymentFromForm(clusterId, data, namespace);
  }
}

