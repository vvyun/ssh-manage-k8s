import os

import yaml
from flask import Flask, render_template, jsonify, request

from crypto_utils import crypto_manager
from k8s_client_svc import K8sClientSvc

app = Flask(__name__)

# 配置文件路径
CLUSTERS_CONFIG_FILE = '.clusters.yaml'


def load_clusters():
    """从YAML文件加载集群配置"""
    if os.path.exists(CLUSTERS_CONFIG_FILE):
        try:
            with open(CLUSTERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                clusters_data = config.get('clusters', {})

                # 解密SSH配置
                for cluster_name, cluster_info in clusters_data.items():
                    if 'ssh_config' in cluster_info:
                        cluster_info['ssh_config'] = crypto_manager.decrypt_ssh_config(
                            cluster_info['ssh_config']
                        )

                return clusters_data
        except Exception as e:
            print(f"加载集群配置文件失败: {e}")
            return {}
    return {}


def save_clusters(clusters_data):
    """保存集群配置到YAML文件"""
    try:
        # 深拷贝，避免修改原始数据
        encrypted_clusters = {}

        for cluster_name, cluster_info in clusters_data.items():
            encrypted_cluster = cluster_info.copy()

            # 加密SSH配置
            if 'ssh_config' in encrypted_cluster:
                encrypted_cluster['ssh_config'] = crypto_manager.encrypt_ssh_config(
                    encrypted_cluster['ssh_config']
                )

            encrypted_clusters[cluster_name] = encrypted_cluster

        # 保存到文件
        with open(CLUSTERS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump({'clusters': encrypted_clusters}, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        print(f"保存集群配置文件失败: {e}")
        return False


# 从文件加载集群配置
clusters = load_clusters()

# 预创建每个集群的客户端，避免每个请求重复初始化
clients = {}


def init_clients():
    """根据已加载的集群配置初始化客户端"""
    for cluster_id, cluster_info in clusters.items():
        try:
            clients[cluster_id] = K8sClientSvc(
                namespace=cluster_info.get('namespace', 'default'),
                ssh_config=cluster_info.get('ssh_config')
            )
        except Exception as e:
            # 初始化失败仅记录，相关接口会返回错误
            print(f"初始化集群客户端失败 {cluster_id}: {e}")


init_clients()


def get_cluster_client(cluster_id):
    """获取已初始化的集群客户端"""
    if cluster_id not in clusters:
        return None, (jsonify({"error": "Cluster not found"}), 404)
    client = clients.get(cluster_id)
    if not client:
        return None, (jsonify({"error": "Cluster client not initialized"}), 500)
    return client, None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """获取集群列表"""
    return jsonify(list(clusters.values()))


@app.route('/api/clusters', methods=['POST'])
def add_cluster():
    """添加新集群"""
    data = request.json
    cluster_id = data['name']

    # 先初始化客户端，避免反复创建
    try:
        client = K8sClientSvc(
            namespace=data.get('namespace', 'default'),
            ssh_config=data.get('ssh_config')
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"初始化集群客户端失败: {e}"}), 500

    # 添加到内存中的集群字典
    clusters[cluster_id] = data

    # 保存到YAML文件
    if save_clusters(clusters):
        clients[cluster_id] = client
        return jsonify({"success": True, "cluster_id": cluster_id})
    else:
        # 如果保存失败，从内存中移除
        del clusters[cluster_id]
        return jsonify({"success": False, "error": "保存集群配置失败"}), 500


@app.route('/api/clusters/<cluster_id>/namespaces', methods=['GET'])
def get_namespaces(cluster_id):
    """获取命名空间列表"""
    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    cluster = clusters[cluster_id]
    try:
        namespaces = client.get_namespace()
        for ns in namespaces:
            if ns['NAME'] == cluster['namespace']:
                ns['SELECT'] = True
        return jsonify(namespaces)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/deployments', methods=['GET'])
def get_deployments(cluster_id):
    """获取工作负载列表"""
    namespace = request.args.get('namespace', 'default')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    try:
        deployments = client.get_deployments(namespace)
        return jsonify(deployments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/services', methods=['GET'])
def get_services(cluster_id):
    """获取服务列表"""
    namespace = request.args.get('namespace', 'default')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    try:
        services = client.get_services(namespace)
        return jsonify(services)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/pods', methods=['GET'])
def get_pods(cluster_id):
    """获取Pod列表"""
    namespace = request.args.get('namespace', 'default')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    try:
        pods = client.get_pods(namespace)
        return jsonify(pods)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/deployments/<deployment_name>/update-image', methods=['POST'])
def update_deployment_image(cluster_id, deployment_name):
    """更新部署镜像"""
    namespace = request.args.get('namespace', 'default')
    data = request.json
    image = data.get('image')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    if not image:
        return jsonify({"error": "Image is required"}), 400

    try:
        result = client.update_deployment_image(namespace, deployment_name, image)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/pods/<pod_name>', methods=['DELETE'])
def delete_pod(cluster_id, pod_name):
    """删除Pod"""
    namespace = request.args.get('namespace', 'default')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    try:
        result = client.delete_pod(namespace, pod_name)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/pods/<pod_name>/logs', methods=['GET'])
def get_pod_logs(cluster_id, pod_name):
    """获取Pod日志"""
    namespace = request.args.get('namespace', 'default')
    lines = request.args.get('lines', None)

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    try:
        # 将lines转换为整数，如果为空则不传
        log_lines = int(lines) if lines else None
        logs = client.logs(namespace, pod_name, log_lines)
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/search-deployments-by-image', methods=['GET'])
def search_deployments_by_image(cluster_id):
    """根据镜像名称查询工作负载"""
    namespace = request.args.get('namespace', 'default')
    image_name = request.args.get('image', '')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    if not image_name:
        return jsonify({"error": "Image name is required"}), 400

    try:
        deoloy_images = client.get_deployment_images(namespace)

        # 筛选包含指定镜像的部署
        # 这里简化处理，实际需要根据具体情况调整
        matching_deployments = []
        for deoloy_image in deoloy_images:
            if str(deoloy_image["IMAGES"]).startswith(image_name.split(":")[0]):
                matching_deployments.append({
                    "name": deoloy_image.get("NAME", ""),
                    "ready": deoloy_image.get("READY", ""),
                    "image": deoloy_image.get("IMAGES", ""),
                    "namespace": namespace
                })
        return jsonify({"success": True, "deployments": matching_deployments})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>/deployments/<deployment_name>/scale', methods=['POST'])
def scale_deployment(cluster_id, deployment_name):
    """伸缩容器副本数"""
    namespace = request.args.get('namespace', 'default')
    data = request.json
    replicas = data.get('replicas')

    client, error_resp = get_cluster_client(cluster_id)
    if error_resp:
        return error_resp

    if replicas is None:
        return jsonify({"error": "Replicas is required"}), 400

    try:
        replicas = int(replicas)
        if replicas < 0:
            return jsonify({"error": "Replicas must be non-negative"}), 400
    except ValueError:
        return jsonify({"error": "Replicas must be a number"}), 400

    try:
        result = client.scale_deployment(namespace, deployment_name, replicas)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clusters/<cluster_id>', methods=['PUT'])
def update_cluster(cluster_id):
    """更新集群信息"""
    data = request.json
    new_name = data.get('name')
    
    if cluster_id not in clusters:
        return jsonify({"error": "Cluster not found"}), 404
    
    if not new_name:
        return jsonify({"error": "Cluster name is required"}), 400
    
    # 更新集群名称
    cluster = clusters[cluster_id]
    old_name = cluster['name']
    cluster['name'] = new_name
    
    # 如果集群ID是根据旧名称生成的，也需要更新
    if cluster_id == old_name:
        new_cluster_id = new_name
        clusters[new_cluster_id] = cluster
        del clusters[cluster_id]
        if cluster_id in clients:
            clients[new_cluster_id] = clients.pop(cluster_id)
    
    # 保存到文件
    if save_clusters(clusters):
        return jsonify({"success": True, "cluster_id": cluster_id})
    else:
        # 回滚更改
        cluster['name'] = old_name
        if cluster_id == old_name:
            clusters[cluster_id] = cluster
            del clusters[new_cluster_id]
            if new_cluster_id in clients:
                clients[cluster_id] = clients.pop(new_cluster_id)
        return jsonify({"success": False, "error": "保存集群配置失败"}), 500


@app.route('/api/clusters/<cluster_id>', methods=['DELETE'])
def delete_cluster(cluster_id):
    """删除集群"""
    if cluster_id not in clusters:
        return jsonify({"error": "Cluster not found"}), 404
    
    backup_cluster = clusters[cluster_id]
    backup_client = clients.pop(cluster_id, None)
    # 删除集群
    del clusters[cluster_id]
    
    # 保存到文件
    if save_clusters(clusters):
        return jsonify({"success": True})
    else:
        # 如果保存失败，需要恢复集群（这里简化处理，实际应该更复杂）
        clusters[cluster_id] = backup_cluster
        if backup_client:
            clients[cluster_id] = backup_client
        return jsonify({"success": False, "error": "保存集群配置失败"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
