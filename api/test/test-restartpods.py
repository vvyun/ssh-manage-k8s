# 重启pods
import json
import os

from api.k8s_client_svc import K8sClientSvc

deploy_name = "svc-dict"
# 命名空间
name_space = "ns-xxx"

print("deployment 名称 【", deploy_name, "】")

ns_server_info = json.loads(os.environ.get("ssh-xxx-env"))
client = K8sClientSvc(namespace=name_space, ssh_config=ns_server_info)

try:
    pods = client.get_pods()
    if len(pods) == 0:
        print("获取pods失败")
        exit(1)
    pods_name = None
    for pod in pods:
        if str(pod.get('NAME')).startswith(deploy_name):
            pods_name = pod.get('NAME')
    if not pods_name:
        print("获取pods失败 deploy=" + deploy_name)
        exit(1)
    print("pods名称 【", pods_name, "】")
    result = client.delete_pod(pods_name)
    print("重启pods成功")
finally:
    pass
