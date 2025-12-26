import paramiko
import logging


class SSHClient:
    def __init__(self, hostname, username, password=None, key_path=None, port=22):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.client = None
        self.sftp = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """建立SSH连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_path:
                key = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    pkey=key,
                )
            else:
                self.client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                )

            self.logger.info(f"成功连接到 {self.hostname}")
            return True

        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            return False

    def execute_command(self, command):
        """执行单个命令"""
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()

            return {
                "success": True,
                "output": output,
                "error": error,
                "exit_code": stdout.channel.recv_exit_status(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_file(self, local_path, remote_path):
        """上传文件"""
        try:
            self.sftp = self.client.open_sftp()
            self.sftp.put(local_path, remote_path)
            self.logger.info(f"成功上传文件 {local_path} 到 {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"上传文件失败: {e}")
            return False

    def remove_file(self, remote_path):
        """删除远程文件"""
        try:
            self.sftp = self.client.open_sftp()
            self.sftp.remove(remote_path)
            self.logger.info(f"成功删除远程文件 {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"删除远程文件失败: {e}")
            return False

    def execute_script(self, local_script_path, remote_path="/tmp/script.sh"):
        """上传并执行本地脚本"""
        try:
            # 上传脚本
            self.sftp = self.client.open_sftp()
            self.sftp.put(local_script_path, remote_path)

            # 设置权限
            self.execute_command(f"chmod +x {remote_path}")

            # 执行脚本
            result = self.execute_command(f"bash {remote_path}")

            # 清理（可选）
            self.execute_command(f"rm {remote_path}")

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def disconnect(self):
        """断开连接"""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        self.logger.info(f"已断开与 {self.hostname} 的连接")


# # 使用示例
# if __name__ == "__main__":
#     ssh = SSHClient(
#         hostname='your_server_ip',
#         username='your_username',
#         password='your_password'  # 或使用 key_path='path/to/key.pem'
#     )
#
#     if ssh.connect():
#         # 执行简单命令
#         result = ssh.execute_command('ls -la')
#         print(result['output'])
#
#         # 执行本地脚本
#         result = ssh.execute_script('local_script.sh')
#         print(f"脚本执行结果: {result['output']}")
#
#         ssh.disconnect()
