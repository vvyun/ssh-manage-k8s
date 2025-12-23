import json
import os

from ssh_client import SSHClient


class K8sClientSvc:

    def __init__(
            self,
            namespace="default",
            k8s_controller="SSH",  # 操作方式
            ssh_config=None
    ):
        self.namespace = namespace
        self.k8s_controller = k8s_controller
        if self.k8s_controller == "SSH":
            self.client = SshK8sClient(ssh_config)
        else:
            raise NotImplementedError()

    def get_namespace(self, ns: str = None) -> list[dict]:
        """
        获取命名空间
        """
        return self.client.get_namespace(ns)

    def get_deployments(self, ns: str = None) -> list[dict]:
        """
        获取工作负载
        """
        if ns is None:
            ns = self.namespace
        return self.client.get_deployments(ns)

    def get_pods(self, ns: str = None) -> list[dict]:
        """
        获取pods
        """
        if ns is None:
            ns = self.namespace
        return self.client.get_pods(ns)

    def get_services(self, ns: str = None) -> list[dict]:
        """
        获取服务
        """
        if ns is None:
            ns = self.namespace
        return self.client.get_services(ns)

    def logs(self, ns: str = None, pod_name: str = None, lines: int = None) -> str:
        if ns is None:
            ns = self.namespace
        if not pod_name:
            raise Exception("pod name 非空")
        return self.client.logs(ns, pod_name, lines)

    def delete_pod(self, ns: str = None, pod_name: str = None) -> str:
        if ns is None:
            ns = self.namespace
        if not pod_name:
            raise Exception("pod_name 非空")
        return self.client.delete_pod(ns, pod_name)

    def update_deployment_image(self, ns: str = None, deploy_name: str = None, image: str = None) -> str:
        if ns is None:
            ns = self.namespace
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if not image:
            raise Exception("image 非空")
        return self.client.update_deployment_image(ns, deploy_name, image)

    def get_deployment_images(self, ns: str = None) -> list[dict]:
        if ns is None:
            ns = self.namespace
        return self.client.get_deployment_images(ns)

    def scale_deployment(self, ns: str = None, deploy_name: str = None, replicas: int = None) -> str:
        """
        伸缩容器副本数
        """
        if ns is None:
            ns = self.namespace
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if replicas is None:
            raise Exception("replicas 非空")
        return self.client.scale_deployment(ns, deploy_name, replicas)


def convert2map(res: dict) -> list[dict]:
    if not res["success"]:
        return []
    lines = res["output"].splitlines()
    if len(lines) == 0:
        return []
    header = lines[0]
    fields = header.split()
    ns_list = []
    for line in lines[1:]:
        ns_item = {}
        for field in fields:
            field_name = str(field).replace("-", "_")
            if field_name.__contains__("PORT"):
                field_name = "PORTS"
            if len(line.split()) > fields.index(field):
                ns_item[field_name] = line.split()[fields.index(field)]
        ns_list.append(ns_item)
    return ns_list


class SshK8sClient:
    def __init__(self, ssh_config):
        self.ssh_client = SSHClient(**ssh_config)
        self.ssh_client.connect()

    def __del__(self):
        self.ssh_client.disconnect()

    def get_namespace(self, ns: str) -> list[dict]:
        """
        获取命名空间
        """
        result = self.ssh_client.execute_command("kubectl get ns")
        result = convert2map(result)
        if ns:
            return [next((item for item in result if item["NAME"] == ns), None)]
        return result

    def get_deployments(self, ns: str) -> list[dict]:
        """
        获取部署
        """
        result = self.ssh_client.execute_command(f"kubectl get deployments -n {ns}")
        return convert2map(result)

    def get_pods(self, ns: str) -> list[dict]:
        """
        获取Pod
        """
        result = self.ssh_client.execute_command(f"kubectl get pods -n {ns}")
        return convert2map(result)

    def get_services(self, ns: str) -> list[dict]:
        """
        获取服务
        """
        result = self.ssh_client.execute_command(f"kubectl get services -n {ns}")
        return convert2map(result)

    def logs(self, ns: str = None, pods_name: str = None, lines: int = None) -> str:
        print("pods名称 【", pods_name, "】")
        args = f"--tail {lines}" if lines else ""
        cmd = f"""kubectl logs {args} -n {ns} {pods_name}"""
        result = self.ssh_client.execute_command(cmd)
        return result["output"]

    def delete_pod(self, ns: str = None, pod_name: str = None) -> str:
        cmd = f"""kubectl delete pods -n {ns} {pod_name}"""
        result = self.ssh_client.execute_command(cmd)
        return result["output"]

    def update_deployment_image(self, ns: str = None, deploy_name: str = None, image: str = None) -> str:
        shell_cmd = f"""kubectl set image deployment/{deploy_name} {deploy_name}={image} -n {ns}"""
        result = self.ssh_client.execute_command(shell_cmd)
        return result["output"]

    def get_deployment_images(self, ns: str = None) -> list[dict]:
        shell_cmd = f"""kubectl get deployments -n {ns} -o custom-columns=NAME:.metadata.name,IMAGES:.spec.template.spec.containers[*].image"""
        result = self.ssh_client.execute_command(shell_cmd)
        return convert2map(result)

    def scale_deployment(self, ns: str = None, deploy_name: str = None, replicas: int = None) -> str:
        """
        伸缩容器副本数
        """
        shell_cmd = f"""kubectl scale deployment/{deploy_name} --replicas={replicas} -n {ns}"""
        result = self.ssh_client.execute_command(shell_cmd)
        return result["output"]


if __name__ == "__main__":
    ns_server_info = json.loads(os.environ.get("ssh-xxxx-pre"))
    client = K8sClientSvc(ssh_config=ns_server_info)
    print(client.get_namespace())
    client.namespace = "ns-xxxx"
    print(client.get_deployments())
    print(client.get_pods())
    print(client.get_services())
