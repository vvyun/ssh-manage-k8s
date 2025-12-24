# 升级deployment的镜像
import json
import os

from api.k8s_client_svc import K8sClientSvc

# 镜像名称
images = [
    "registry.cn-shenzhen.aliyuncs.com/xxx_test/xxxa:0.0.1-release",
    "registry.cn-shenzhen.aliyuncs.com/xxx_test/xxxb:0.0.1-release",
]

# 命名空间
name_space = "ns-xxx"


# 获取images对应的deployment名称
def get_deploy_name(client, image, namespace):
    deoloy_images = client.get_deployment_images(namespace)
    for deoloy_image in deoloy_images:
        if str(deoloy_image["IMAGES"]).startswith(image.split(":")[0]):
            return deoloy_image["NAME"]
    raise Exception("未找到对应的deployment名称")


def update_deployment_image(client, image, namespace):
    deploy_name = get_deploy_name(client, image, namespace)
    print("deployment 名称 【", deploy_name, "】")

    result = client.update_deployment_image(ns=namespace, deploy_name=deploy_name, image=image)
    print("**********升级结果************")
    print(result)


if __name__ == "__main__":
    ns_server_info = json.loads(os.environ.get("ssh-xxx-env"))
    _client_ = K8sClientSvc(namespace=name_space, ssh_config=ns_server_info)
    for _image_ in images:
        update_deployment_image(_client_, _image_, name_space)
