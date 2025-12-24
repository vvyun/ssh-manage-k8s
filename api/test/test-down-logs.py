# 获取pods日志
import json
import os

from api.k8s_client_svc import K8sClientSvc

deploy_name = "base-svc-xxx"
# 命名空间
name_space = "ns-xxx"
logs_dir = "../logs"
# 查看日志行数
lines = 500

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
    result = client.logs(pod_name=pods_name, lines=lines)
    # 将日志输出到文件
    with open(f"{logs_dir}/{deploy_name}.log", "w", encoding="utf-8") as file:
        file.write(result)
finally:
    print('success!')
