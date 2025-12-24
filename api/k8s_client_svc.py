import os
import yaml
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from kubernetes import client as k8s_client
from kubernetes import config as k8s_config

from ssh_client import SSHClient


class K8sClientSvc:

    def __init__(
            self,
            namespace="default",
            k8s_controller="KUBE",  # 操作方式
            ssh_config=None,
            kube_config=None,
    ):
        self.namespace = namespace
        self.k8s_controller = k8s_controller
        if self.k8s_controller == "SSH":
            self.client = SshK8sClient(ssh_config)
        elif self.k8s_controller == "KUBE":
            self.client = KubeK8sClient(kube_config, namespace)
        else:
            raise NotImplementedError(f"未知的 k8s_controller: {k8s_controller}")

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

    def get_configmaps(self, ns: str = None) -> list[dict]:
        """
        获取ConfigMap
        """
        if ns is None:
            ns = self.namespace
        return self.client.get_configmaps(ns)

    def get_ingresses(self, ns: str = None) -> list[dict]:
        """
        获取Ingress
        """
        if ns is None:
            ns = self.namespace
        return self.client.get_ingresses(ns)

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

    def create_namespace(self, ns: str) -> str:
        """
        创建命名空间
        """
        if not ns:
            raise Exception("namespace name 非空")
        return self.client.create_namespace(ns)

    def delete_namespace(self, ns: str) -> str:
        """
        删除命名空间
        """
        if not ns:
            raise Exception("namespace name 非空")
        return self.client.delete_namespace(ns)

    def get_deployment_detail(self, deploy_name: str, ns: str) -> dict:
        """
        获取Deployment详情
        """
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if not ns:
            raise Exception("namespace 非空")
        return self.client.get_deployment_detail(deploy_name, ns)

    def get_service_detail(self, service_name: str, ns: str) -> dict:
        """
        获取Service详情
        """
        if not service_name:
            raise Exception("service_name 非空")
        if not ns:
            raise Exception("namespace 非空")
        return self.client.get_service_detail(service_name, ns)

    def create_deployment(self, ns: str, deployment_data: dict) -> str:
        """
        创建Deployment
        """
        return self.client.create_deployment(ns, deployment_data)

    def create_deployment_from_yaml(self, ns: str, yaml_content: str) -> str:
        """
        从YAML创建Deployment
        """
        return self.client.create_deployment_from_yaml(ns, yaml_content)

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


def re_connect_if_disconnect_decorator(func):
    """前置调用装饰器"""

    def wrapper(self, *args, **kwargs):
        # 在调用原方法前执行统一操作
        self.re_connect_if_disconnect(func.__name__)
        # 调用原方法
        return func(self, *args, **kwargs)

    return wrapper


class SshK8sClient:
    def __init__(self, ssh_config):
        self.ssh_client = SSHClient(**ssh_config)
        self.ssh_client.connect()

    def __del__(self):
        self.ssh_client.disconnect()

    def re_connect_if_disconnect(self, method_name):
        # print(method_name)
        res = self.ssh_client.execute_command("echo 'hello world'")
        if not res.get('success', False) and res.get('error', '') == 'SSH session not active':
            self.ssh_client.connect()

    @re_connect_if_disconnect_decorator
    def get_namespace(self, ns: str) -> list[dict]:
        """
        获取命名空间
        """
        result = self.ssh_client.execute_command("kubectl get ns")
        result = convert2map(result)
        if ns:
            return [next((item for item in result if item["NAME"] == ns), None)]
        return result

    @re_connect_if_disconnect_decorator
    def get_deployments(self, ns: str) -> list[dict]:
        """
        获取部署
        """
        result = self.ssh_client.execute_command(f"kubectl get deployments -n {ns}")
        return convert2map(result)

    @re_connect_if_disconnect_decorator
    def get_pods(self, ns: str) -> list[dict]:
        """
        获取Pod
        """
        result = self.ssh_client.execute_command(f"kubectl get pods -n {ns}")
        return convert2map(result)

    @re_connect_if_disconnect_decorator
    def get_services(self, ns: str) -> list[dict]:
        """
        获取服务
        """
        result = self.ssh_client.execute_command(f"kubectl get services -n {ns}")
        return convert2map(result)

    @re_connect_if_disconnect_decorator
    def logs(self, ns: str = None, pods_name: str = None, lines: int = None) -> str:
        args = f"--tail {lines}" if lines else ""
        cmd = f"""kubectl logs {args} -n {ns} {pods_name}"""
        result = self.ssh_client.execute_command(cmd)
        return result["output"]

    @re_connect_if_disconnect_decorator
    def get_configmaps(self, ns: str) -> list[dict]:
        """
        获取ConfigMap
        """
        result = self.ssh_client.execute_command(f"kubectl get configmaps -n {ns}")
        return convert2map(result)

    @re_connect_if_disconnect_decorator
    def get_ingresses(self, ns: str) -> list[dict]:
        """
        获取Ingress
        """
        result = self.ssh_client.execute_command(f"kubectl get ingress -n {ns}")
        return convert2map(result)

    @re_connect_if_disconnect_decorator
    def delete_pod(self, ns: str = None, pod_name: str = None) -> str:
        cmd = f"""kubectl delete pods -n {ns} {pod_name}"""
        result = self.ssh_client.execute_command(cmd)
        return result["output"]

    @re_connect_if_disconnect_decorator
    def update_deployment_image(self, ns: str = None, deploy_name: str = None, image: str = None) -> str:
        shell_cmd = f"""kubectl set image deployment/{deploy_name} {deploy_name}={image} -n {ns}"""
        result = self.ssh_client.execute_command(shell_cmd)
        return result["output"]

    @re_connect_if_disconnect_decorator
    def get_deployment_images(self, ns: str = None) -> list[dict]:
        shell_cmd = f"""kubectl get deployments -n {ns} -o custom-columns=NAME:.metadata.name,IMAGES:.spec.template.spec.containers[*].image"""
        result = self.ssh_client.execute_command(shell_cmd)
        return convert2map(result)

    @re_connect_if_disconnect_decorator
    def scale_deployment(self, ns: str = None, deploy_name: str = None, replicas: int = None) -> str:
        """
        伸缩容器副本数
        """
        shell_cmd = f"""kubectl scale deployment/{deploy_name} --replicas={replicas} -n {ns}"""
        result = self.ssh_client.execute_command(shell_cmd)
        return result["output"]

    @re_connect_if_disconnect_decorator
    def create_namespace(self, ns: str) -> str:
        """
        创建命名空间
        """
        if not ns:
            raise Exception("namespace name 非空")
        
        # 检查命名空间是否已存在
        result = self.ssh_client.execute_command(f"kubectl get namespace {ns}")
        if result.get('success', False):
            raise Exception(f"命名空间 {ns} 已存在")
        
        # 创建命名空间
        result = self.ssh_client.execute_command(f"kubectl create namespace {ns}")
        if not result.get('success', False):
            raise Exception(f"创建命名空间 {ns} 失败: {result.get('error', 'Unknown error')}")
        return f"命名空间 {ns} 创建成功"

    @re_connect_if_disconnect_decorator
    def delete_namespace(self, ns: str) -> str:
        """
        删除命名空间
        """
        if not ns:
            raise Exception("namespace name 非空")
        
        # 检查命名空间是否存在
        result = self.ssh_client.execute_command(f"kubectl get namespace {ns}")
        if not result.get('success', False):
            raise Exception(f"命名空间 {ns} 不存在")
        
        # 删除命名空间
        result = self.ssh_client.execute_command(f"kubectl delete namespace {ns}")
        if not result.get('success', False):
            raise Exception(f"删除命名空间 {ns} 失败: {result.get('error', 'Unknown error')}")
        return f"命名空间 {ns} 删除成功"

    @re_connect_if_disconnect_decorator
    def get_deployment_detail(self, deploy_name: str, ns: str) -> dict:
        """
        获取Deployment详情
        """
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if not ns:
            raise Exception("namespace 非空")
        
        # 使用kubectl获取Deployment的YAML格式详情
        result = self.ssh_client.execute_command(f"kubectl get deployment {deploy_name} -n {ns} -o yaml")
        if not result.get('success', False):
            raise Exception(f"获取Deployment {deploy_name} 详情失败: {result.get('error', 'Unknown error')}")
        
        deployment_yaml = yaml.safe_load(result['output'])
        return deployment_yaml

    @re_connect_if_disconnect_decorator
    def get_service_detail(self, service_name: str, ns: str) -> dict:
        """
        获取Service详情
        """
        if not service_name:
            raise Exception("service_name 非空")
        if not ns:
            raise Exception("namespace 非空")
        
        # 使用kubectl获取Service的YAML格式详情
        result = self.ssh_client.execute_command(f"kubectl get service {service_name} -n {ns} -o yaml")
        if not result.get('success', False):
            raise Exception(f"获取Service {service_name} 详情失败: {result.get('error', 'Unknown error')}")
        
        service_yaml = yaml.safe_load(result['output'])
        return service_yaml

    @re_connect_if_disconnect_decorator
    def create_deployment(self, ns: str, deployment_data: dict) -> str:
        """
        创建Deployment - 通过表单数据
        """
        import tempfile
        import os
        
        # 构建Deployment YAML内容
        deployment_yaml = self._build_deployment_yaml(deployment_data)
        # 替换YAML中的占位符命名空间
        deployment_yaml = deployment_yaml.replace('PLACEHOLDER_NAMESPACE', ns)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(deployment_yaml)
            temp_file_path = f.name
        
        try:
            # 使用kubectl apply创建Deployment
            result = self.ssh_client.execute_command(f"kubectl apply -f {temp_file_path} -n {ns}")
            if not result.get('success', False):
                raise Exception(f"创建Deployment失败: {result.get('error', 'Unknown error')}")
            return result['output']
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)

    def create_deployment_from_yaml(self, ns: str, yaml_content: str) -> str:
        """
        从YAML内容创建Deployment
        """
        import tempfile
        import os
        import yaml as yaml_lib
        
        # 解析YAML内容，修改命名空间，然后重新序列化
        try:
            yaml_dict = yaml_lib.safe_load(yaml_content)
            if 'metadata' in yaml_dict and yaml_dict.get('kind') == 'Deployment':
                yaml_dict['metadata']['namespace'] = ns
            yaml_content = yaml_lib.dump(yaml_dict, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            # 如果YAML解析失败，使用字符串替换作为备选方案
            yaml_content = yaml_content.replace('namespace: default', f'namespace: {ns}')
            yaml_content = yaml_content.replace('namespace: PLACEHOLDER_NAMESPACE', f'namespace: {ns}')
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file_path = f.name
        
        try:
            # 使用kubectl apply创建Deployment
            result = self.ssh_client.execute_command(f"kubectl apply -f {temp_file_path} -n {ns}")
            if not result.get('success', False):
                raise Exception(f"创建Deployment失败: {result.get('error', 'Unknown error')}")
            return result['output']
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)

    def _build_deployment_yaml(self, deployment_data: dict) -> str:
        """
        根据表单数据构建Deployment YAML
        """
        
        name = deployment_data.get('name', 'default-deployment')
        image = deployment_data.get('image', 'nginx:latest')
        replicas = deployment_data.get('replicas', 1)
        # 注意：命名空间由调用方法传入，而不是从deployment_data中获取
        ports = deployment_data.get('ports', [])
        env = deployment_data.get('env', [])
        volumes = deployment_data.get('volumes', [])
        
        # 构建Deployment对象
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": "PLACEHOLDER_NAMESPACE",  # 将在调用方法中设置正确的命名空间
                "labels": {
                    "app": name
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                            }
                        ]
                    }
                }
            }
        }
        
        # 添加端口配置
        if ports:
            container = deployment['spec']['template']['spec']['containers'][0]
            container['ports'] = []
            for port in ports:
                if port.get('containerPort'):
                    container['ports'].append({
                        "containerPort": int(port['containerPort']),
                        "protocol": port.get('protocol', 'TCP')
                    })
        
        # 添加环境变量
        if env:
            container = deployment['spec']['template']['spec']['containers'][0]
            container['env'] = []
            for env_var in env:
                if env_var.get('name') and env_var.get('value'):
                    container['env'].append({
                        "name": env_var['name'],
                        "value": env_var['value']
                    })
        
        # 添加卷挂载
        if volumes:
            container = deployment['spec']['template']['spec']['containers'][0]
            container['volumeMounts'] = []
            deployment['spec']['template']['spec']['volumes'] = []
            
            for i, volume in enumerate(volumes):
                if volume.get('name') and volume.get('mountPath'):
                    # 卷挂载
                    container['volumeMounts'].append({
                        "name": volume['name'],
                        "mountPath": volume['mountPath']
                    })
                    
                    # 卷定义
                    deployment['spec']['template']['spec']['volumes'].append({
                        "name": volume['name'],
                        "hostPath": {
                            "path": volume.get('volumePath', '/tmp'),
                            "type": "Directory"
                        }
                    })
        
        # 转换为YAML格式
        return yaml.dump(deployment, default_flow_style=False, allow_unicode=True)


def switch_kubeconfig_decorator(func):
    """前置调用装饰器"""

    def wrapper(self, *args, **kwargs):
        # 在调用原方法前执行统一操作
        self.switch_kubeconfig(func.__name__)
        # 调用原方法
        return func(self, *args, **kwargs)

    return wrapper


class KubeK8sClient:
    """
    使用官方 kubernetes Python SDK 的客户端实现
    """

    def __init__(self, kube_config=None, namespace: str = "default"):
        self.apps_v1 = None
        self.core_v1 = None
        self.namespace = namespace
        self.kube_config = kube_config

    def switch_kubeconfig(self, method_name):
        self._load_config(self.kube_config)
        self.core_v1 = k8s_client.CoreV1Api()
        self.apps_v1 = k8s_client.AppsV1Api()

    @staticmethod
    def _load_config(kube_config):
        """
        支持三种方式加载配置：
        1. 未提供 -> 默认搜索 ~/.kube/config
        2. 字符串且是文件路径 -> 从该路径加载
        3. dict -> 直接从 dict 加载
        """
        if kube_config is None:
            k8s_config.load_kube_config()
            return
        if isinstance(kube_config, str) and os.path.exists(kube_config):
            k8s_config.load_kube_config(config_file=kube_config)
            return
        if isinstance(kube_config, dict):
            k8s_config.load_kube_config_from_dict(kube_config)
            return
        raise ValueError("kube_config 应为路径、dict 或 None")

    # ---------- 通用辅助 ----------
    @staticmethod
    def _format_age(creation_timestamp: Optional[datetime]) -> str:
        if not creation_timestamp:
            return ""
        now = datetime.now(timezone.utc)
        delta = now - creation_timestamp
        days = delta.days
        seconds = delta.seconds
        if days > 0:
            return f"{days}d"
        hours = seconds // 3600
        if hours > 0:
            return f"{hours}h"
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes}m"
        return f"{seconds}s"

    @staticmethod
    def _join_images(containers) -> str:
        return ",".join([c.image for c in containers]) if containers else ""

    # ---------- 业务方法 ----------
    @switch_kubeconfig_decorator
    def get_namespace(self, ns: str = None) -> List[Dict]:
        namespaces = self.core_v1.list_namespace().items
        results = [{
            "NAME": item.metadata.name,
            "STATUS": item.status.phase,
            "AGE": self._format_age(item.metadata.creation_timestamp),
        } for item in namespaces]
        if ns:
            return [next((item for item in results if item["NAME"] == ns), None)]
        return results

    @switch_kubeconfig_decorator
    def get_deployments(self, ns: str) -> List[Dict]:
        deployments = self.apps_v1.list_namespaced_deployment(ns).items
        result = []
        for dep in deployments:
            desired = dep.spec.replicas or 0
            ready = dep.status.ready_replicas or 0
            uptodate = dep.status.updated_replicas or 0
            available = dep.status.available_replicas or 0
            result.append({
                "NAME": dep.metadata.name,
                "READY": f"{ready}/{desired}",
                "UP-TO-DATE": uptodate,
                "AVAILABLE": available,
                "AGE": self._format_age(dep.metadata.creation_timestamp),
            })
        return result

    @switch_kubeconfig_decorator
    def get_pods(self, ns: str) -> List[Dict]:
        pods = self.core_v1.list_namespaced_pod(ns).items
        result = []
        for pod in pods:
            total = len(pod.spec.containers or [])
            ready = sum(1 for cs in (pod.status.container_statuses or []) if cs.ready)
            restarts = sum((cs.restart_count or 0) for cs in (pod.status.container_statuses or []))
            result.append({
                "NAME": pod.metadata.name,
                "READY": f"{ready}/{total}",
                "STATUS": pod.status.phase,
                "RESTARTS": restarts,
                "AGE": self._format_age(pod.metadata.creation_timestamp),
            })
        return result

    @switch_kubeconfig_decorator
    def get_services(self, ns: str) -> List[Dict]:
        services = self.core_v1.list_namespaced_service(ns).items
        result = []
        for svc in services:
            ports = []
            for p in svc.spec.ports or []:
                port_str = f"{p.port}"
                if p.node_port:
                    port_str = f"{p.port}:{p.node_port}"
                protocol = p.protocol or "TCP"
                ports.append(f"{port_str}/{protocol}")
            external_ip = ""
            if svc.status.load_balancer and svc.status.load_balancer.ingress:
                external_ip = svc.status.load_balancer.ingress[0].ip or svc.status.load_balancer.ingress[0].hostname
            elif svc.spec.external_i_ps:
                external_ip = ",".join(svc.spec.external_i_ps)
            else:
                external_ip = "None"
            result.append({
                "NAME": svc.metadata.name,
                "TYPE": svc.spec.type,
                "CLUSTER-IP": svc.spec.cluster_ip,
                "EXTERNAL-IP": external_ip,
                "PORTS": ",".join(ports),
                "AGE": self._format_age(svc.metadata.creation_timestamp),
            })
        return result

    @switch_kubeconfig_decorator
    def logs(self, ns: str = None, pods_name: str = None, lines: int = None) -> str:
        if not pods_name:
            raise Exception("pod name 非空")
        return self.core_v1.read_namespaced_pod_log(
            name=pods_name,
            namespace=ns or self.namespace,
            tail_lines=lines
        )

    @switch_kubeconfig_decorator
    def get_configmaps(self, ns: str) -> List[Dict]:
        """
        获取ConfigMap
        """
        configmaps = self.core_v1.list_namespaced_config_map(ns).items
        result = []
        for cm in configmaps:
            result.append({
                "NAME": cm.metadata.name,
                "DATA": str(len(cm.data)) if cm.data else "0",
                "AGE": self._format_age(cm.metadata.creation_timestamp),
            })
        return result

    @switch_kubeconfig_decorator
    def get_ingresses(self, ns: str) -> List[Dict]:
        """
        获取Ingress
        """
        # 需要导入networking v1 API
        networking_v1 = k8s_client.NetworkingV1Api()
        ingresses = networking_v1.list_namespaced_ingress(ns).items
        result = []
        for ing in ingresses:
            hosts = []
            if ing.spec.rules:
                for rule in ing.spec.rules:
                    if rule.host:
                        hosts.append(rule.host)
            addresses = []
            if ing.status.load_balancer and ing.status.load_balancer.ingress:
                for lb_ingress in ing.status.load_balancer.ingress:
                    if lb_ingress.ip:
                        addresses.append(lb_ingress.ip)
                    elif lb_ingress.hostname:
                        addresses.append(lb_ingress.hostname)
            result.append({
                "NAME": ing.metadata.name,
                "CLASS": getattr(ing.spec, 'ingress_class_name', '') if ing.spec else '',
                "HOSTS": ",".join(hosts) if hosts else "*",
                "ADDRESS": ",".join(addresses) if addresses else "",
                "AGE": self._format_age(ing.metadata.creation_timestamp),
            })
        return result

    @switch_kubeconfig_decorator
    def delete_pod(self, ns: str = None, pod_name: str = None) -> str:
        if not pod_name:
            raise Exception("pod_name 非空")
        self.core_v1.delete_namespaced_pod(
            name=pod_name,
            namespace=ns or self.namespace
        )
        return "pod deleted"

    @switch_kubeconfig_decorator
    def update_deployment_image(self, ns: str = None, deploy_name: str = None, image: str = None) -> str:
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if not image:
            raise Exception("image 非空")
        ns = ns or self.namespace
        dep = self.apps_v1.read_namespaced_deployment(name=deploy_name, namespace=ns)
        if not dep.spec.template.spec.containers:
            raise Exception("未找到容器")
        dep.spec.template.spec.containers[0].image = image
        self.apps_v1.patch_namespaced_deployment(name=deploy_name, namespace=ns, body=dep)
        return "deployment image updated"

    @switch_kubeconfig_decorator
    def get_deployment_images(self, ns: str = None) -> List[Dict]:
        ns = ns or self.namespace
        deployments = self.apps_v1.list_namespaced_deployment(ns).items
        return [{
            "NAME": dep.metadata.name,
            "IMAGES": self._join_images(dep.spec.template.spec.containers),
        } for dep in deployments]

    @switch_kubeconfig_decorator
    def scale_deployment(self, ns: str = None, deploy_name: str = None, replicas: int = None) -> str:
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if replicas is None:
            raise Exception("replicas 非空")
        ns = ns or self.namespace
        body = {"spec": {"replicas": replicas}}
        self.apps_v1.patch_namespaced_deployment_scale(name=deploy_name, namespace=ns, body=body)
        return "deployment scaled"

    @switch_kubeconfig_decorator
    def create_namespace(self, ns: str) -> str:
        """
        创建命名空间
        """
        if not ns:
            raise Exception("namespace name 非空")
        
        # 检查命名空间是否已存在
        try:
            existing_ns = self.core_v1.read_namespace(name=ns)
            if existing_ns:
                raise Exception(f"命名空间 {ns} 已存在")
        except k8s_client.ApiException as e:
            if e.status != 404:
                # 如果不是404错误（即不是因为不存在而报错），则抛出异常
                raise e
        
        # 创建命名空间
        namespace = k8s_client.V1Namespace(
            metadata=k8s_client.V1ObjectMeta(name=ns)
        )
        self.core_v1.create_namespace(body=namespace)
        return f"命名空间 {ns} 创建成功"

    @switch_kubeconfig_decorator
    def delete_namespace(self, ns: str) -> str:
        """
        删除命名空间
        """
        if not ns:
            raise Exception("namespace name 非空")
        
        # 检查命名空间是否存在
        try:
            existing_ns = self.core_v1.read_namespace(name=ns)
            if not existing_ns:
                raise Exception(f"命名空间 {ns} 不存在")
        except k8s_client.ApiException as e:
            if e.status == 404:
                raise Exception(f"命名空间 {ns} 不存在")
            else:
                raise e
        
        # 删除命名空间
        self.core_v1.delete_namespace(name=ns)
        return f"命名空间 {ns} 删除成功"

    @switch_kubeconfig_decorator
    def get_deployment_detail(self, deploy_name: str, ns: str) -> dict:
        """
        获取Deployment详情
        """
        if not deploy_name:
            raise Exception("deploy_name 非空")
        if not ns:
            raise Exception("namespace 非空")
        
        try:
            deployment = self.apps_v1.read_namespaced_deployment(name=deploy_name, namespace=ns)
            # 将Deployment对象转换为字典格式
            deployment_dict = {
                "apiVersion": deployment.api_version,
                "kind": deployment.kind,
                "metadata": {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "creation_timestamp": deployment.metadata.creation_timestamp,
                    "labels": deployment.metadata.labels,
                    "annotations": deployment.metadata.annotations,
                    "resource_version": deployment.metadata.resource_version,
                    "uid": deployment.metadata.uid,
                },
                "spec": deployment.spec.to_dict(),
                "status": deployment.status.to_dict() if deployment.status else None,
            }
            return deployment_dict
        except k8s_client.ApiException as e:
            if e.status == 404:
                raise Exception(f"Deployment {deploy_name} 在命名空间 {ns} 中不存在")
            else:
                raise e

    @switch_kubeconfig_decorator
    def get_service_detail(self, service_name: str, ns: str) -> dict:
        """
        获取Service详情
        """
        if not service_name:
            raise Exception("service_name 非空")
        if not ns:
            raise Exception("namespace 非空")
        
        try:
            service = self.core_v1.read_namespaced_service(name=service_name, namespace=ns)
            # 将Service对象转换为字典格式
            service_dict = {
                "apiVersion": service.api_version,
                "kind": service.kind,
                "metadata": {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "creation_timestamp": service.metadata.creation_timestamp,
                    "labels": service.metadata.labels,
                    "annotations": service.metadata.annotations,
                    "resource_version": service.metadata.resource_version,
                    "uid": service.metadata.uid,
                },
                "spec": service.spec.to_dict(),
                "status": service.status.to_dict() if service.status else None,
            }
            return service_dict
        except k8s_client.ApiException as e:
            if e.status == 404:
                raise Exception(f"Service {service_name} 在命名空间 {ns} 中不存在")
            else:
                raise e

    @switch_kubeconfig_decorator
    def create_deployment(self, ns: str, deployment_data: dict) -> str:
        """
        使用表单数据创建Deployment
        """
        # 构建Deployment对象
        deployment_yaml = self._build_deployment_yaml(deployment_data)
        deployment_dict = yaml.safe_load(deployment_yaml)
        
        # 确保YAML中的命名空间与请求参数一致
        deployment_dict['metadata']['namespace'] = ns
        
        # 转换为Kubernetes对象
        deployment = self.apps_v1.create_namespaced_deployment(
            namespace=ns,
            body=deployment_dict
        )
        return f"Deployment {deployment.metadata.name} 创建成功"

    @switch_kubeconfig_decorator
    def create_deployment_from_yaml(self, ns: str, yaml_content: str) -> str:
        """
        从YAML内容创建Deployment
        """
        # 解析YAML内容
        deployment_dict = yaml.safe_load(yaml_content)
        
        # 确保YAML中的命名空间与请求参数一致
        deployment_dict['metadata']['namespace'] = ns
        
        # 创建Deployment
        deployment = self.apps_v1.create_namespaced_deployment(
            namespace=ns,
            body=deployment_dict
        )
        return f"Deployment {deployment.metadata.name} 创建成功"

    def _build_deployment_yaml(self, deployment_data: dict) -> str:
        """
        根据表单数据构建Deployment YAML
        """
        name = deployment_data.get('name', 'default-deployment')
        image = deployment_data.get('image', 'nginx:latest')
        replicas = deployment_data.get('replicas', 1)
        # 注意：命名空间由调用方法传入，而不是从deployment_data中获取
        ports = deployment_data.get('ports', [])
        env = deployment_data.get('env', [])
        volumes = deployment_data.get('volumes', [])
        
        # 构建Deployment对象
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": "PLACEHOLDER_NAMESPACE",  # 将在调用方法中设置正确的命名空间
                "labels": {
                    "app": name
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                            }
                        ]
                    }
                }
            }
        }
        
        # 添加端口配置
        if ports:
            container = deployment['spec']['template']['spec']['containers'][0]
            container['ports'] = []
            for port in ports:
                if port.get('containerPort'):
                    container['ports'].append({
                        "containerPort": int(port['containerPort']),
                        "protocol": port.get('protocol', 'TCP')
                    })
        
        # 添加环境变量
        if env:
            container = deployment['spec']['template']['spec']['containers'][0]
            container['env'] = []
            for env_var in env:
                if env_var.get('name') and env_var.get('value'):
                    container['env'].append({
                        "name": env_var['name'],
                        "value": env_var['value']
                    })
        
        # 添加卷挂载
        if volumes:
            container = deployment['spec']['template']['spec']['containers'][0]
            container['volumeMounts'] = []
            deployment['spec']['template']['spec']['volumes'] = []
            
            for i, volume in enumerate(volumes):
                if volume.get('name') and volume.get('mountPath'):
                    # 卷挂载
                    container['volumeMounts'].append({
                        "name": volume['name'],
                        "mountPath": volume['mountPath']
                    })
                    
                    # 卷定义
                    deployment['spec']['template']['spec']['volumes'].append({
                        "name": volume['name'],
                        "hostPath": {
                            "path": volume.get('volumePath', '/tmp'),
                            "type": "Directory"
                        }
                    })
        
        # 转换为YAML格式
        return yaml.dump(deployment, default_flow_style=False, allow_unicode=True)




if __name__ == "__main__":
    client = K8sClientSvc(k8s_controller="KUBE", kube_config="/home/projects/k8s-manage/config_187")
    print(client.get_namespace())
    client.namespace = "kube-system"
    print(client.get_deployments())
    print(client.get_pods())
    print(client.get_services())
