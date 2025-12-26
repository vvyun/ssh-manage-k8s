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

export const deleteDeployment = (clusterId, deploymentName, namespace) =>
  api.delete(`/clusters/${clusterId}/deployments/${deploymentName}`, { params: { namespace } })

export const deleteService = (clusterId, serviceName, namespace) =>
  api.delete(`/clusters/${clusterId}/services/${serviceName}`, { params: { namespace } })

export const deleteConfigMap = (clusterId, configMapName, namespace) =>
  api.delete(`/clusters/${clusterId}/configmaps/${configMapName}`, { params: { namespace } })

export const deleteIngress = (clusterId, ingressName, namespace) =>
  api.delete(`/clusters/${clusterId}/ingresses/${ingressName}`, { params: { namespace } })

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

// apply YAML
export const createFromYaml = (clusterId, yamlContent, namespace) =>
  api.post(`/clusters/${clusterId}/yaml`, { yaml: yamlContent }, { params: { namespace } })

// 创建Deployment
export const createDeployment = (clusterId, deploymentData, namespace) => {
    api.post(`/clusters/${clusterId}/deployments`, deploymentData, { params: { namespace } })
}

// 创建Service
export const createService = (clusterId, serviceData, namespace) =>
  api.post(`/clusters/${clusterId}/services`, serviceData, { params: { namespace } })

// 创建ConfigMap
export const createConfigMap = (clusterId, configMapData, namespace) =>
  api.post(`/clusters/${clusterId}/configmaps`, configMapData, { params: { namespace } })

// 创建Ingress
export const createIngress = (clusterId, ingressData, namespace) =>
  api.post(`/clusters/${clusterId}/ingresses`, ingressData, { params: { namespace } })

