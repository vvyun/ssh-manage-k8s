"""
加密工具模块
用于加密和解密敏感配置信息
"""
import base64
import os

from cryptography.fernet import Fernet


class CryptoManager:
    """加密管理器"""
    
    def __init__(self, key_file='.crypto.key'):
        """
        初始化加密管理器
        :param key_file: 密钥文件路径
        """
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_generate_key(self):
        """加载或生成加密密钥"""
        if os.path.exists(self.key_file):
            # 从文件加载密钥
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # 生成新密钥
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            print(f"已生成新的加密密钥文件: {self.key_file}")
            return key
    
    def encrypt(self, data):
        """
        加密数据
        :param data: 要加密的字符串
        :return: 加密后的字符串（Base64编码）
        """
        if not data:
            return data
        
        # 将字符串转换为bytes
        data_bytes = data.encode('utf-8')
        
        # 加密
        encrypted_bytes = self.cipher.encrypt(data_bytes)
        
        # 转换为Base64字符串以便存储
        encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return f"ENC:{encrypted_str}"
    
    def decrypt(self, data):
        """
        解密数据
        :param data: 要解密的字符串（以ENC:开头）
        :return: 解密后的字符串
        """
        if not data:
            return data
        
        # 检查是否是加密数据
        if not isinstance(data, str) or not data.startswith('ENC:'):
            # 未加密的数据直接返回
            return data
        
        try:
            # 移除ENC:前缀
            encrypted_str = data[4:]
            
            # 从Base64解码
            encrypted_bytes = base64.b64decode(encrypted_str)
            
            # 解密
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # 转换为字符串
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            return decrypted_str
        except Exception as e:
            print(f"解密失败: {e}")
            return data
    
    def encrypt_ssh_config(self, ssh_config):
        """
        加密SSH配置中的敏感信息
        :param ssh_config: SSH配置字典
        :return: 加密后的配置字典
        """
        if not ssh_config:
            return ssh_config
        
        encrypted_config = ssh_config.copy()
        
        # 加密密码
        if 'password' in encrypted_config and encrypted_config['password']:
            encrypted_config['password'] = self.encrypt(encrypted_config['password'])
        
        # 如果有其他敏感字段也可以加密
        # 例如: username, hostname等
        
        return encrypted_config
    
    def decrypt_ssh_config(self, ssh_config):
        """
        解密SSH配置中的敏感信息
        :param ssh_config: SSH配置字典
        :return: 解密后的配置字典
        """
        if not ssh_config:
            return ssh_config
        
        decrypted_config = ssh_config.copy()
        
        # 解密密码
        if 'password' in decrypted_config and decrypted_config['password']:
            decrypted_config['password'] = self.decrypt(decrypted_config['password'])
        
        return decrypted_config


# 创建全局加密管理器实例
crypto_manager = CryptoManager()
