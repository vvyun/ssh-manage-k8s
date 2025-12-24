import { createStore } from 'vuex'

export default createStore({
  state: {
    currentCluster: null,
    clusters: [],
    currentNamespace: 'default'
  },
  mutations: {
    SET_CURRENT_CLUSTER(state, cluster) {
      state.currentCluster = cluster
    },
    SET_CLUSTERS(state, clusters) {
      state.clusters = clusters
    },
    SET_CURRENT_NAMESPACE(state, namespace) {
      state.currentNamespace = namespace
    }
  },
  actions: {
    setCurrentCluster({ commit }, cluster) {
      commit('SET_CURRENT_CLUSTER', cluster)
    },
    setClusters({ commit }, clusters) {
      commit('SET_CLUSTERS', clusters)
    },
    setCurrentNamespace({ commit }, namespace) {
      commit('SET_CURRENT_NAMESPACE', namespace)
    }
  }
})


