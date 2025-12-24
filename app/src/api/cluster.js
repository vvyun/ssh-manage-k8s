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

export const getServices = (clusterId, namespace) => 
  api.get(`/clusters/${clusterId}/services`, { params: { namespace } })

export const getPods = (clusterId, namespace) => 
  api.get(`/clusters/${clusterId}/pods`, { params: { namespace } })

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

