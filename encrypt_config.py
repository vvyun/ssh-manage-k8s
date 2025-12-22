"""
配置文件加密工具
用于加密现有的 .clusters.yaml 文件
"""
import yaml
import os
from crypto_utils import crypto_manager


def encrypt_existing_config():
    """加密现有的配置文件"""
    config_file = '.clusters.yaml'
    backup_file = '.clusters.yaml.bak'
    
    if not os.path.exists(config_file):
        print(f"配置文件不存在: {config_file}")
        return
    
    # 备份原文件
    print("正在备份原配置文件...")
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已备份到: {backup_file}")
    
    # 读取配置
    print("正在读取配置...")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if not config or 'clusters' not in config:
        print("配置文件格式错误")
        return
    
    # 加密SSH配置
    print("正在加密SSH配置...")
    encrypted_count = 0
    for cluster_name, cluster_info in config['clusters'].items():
        if 'ssh_config' in cluster_info:
            if 'password' in cluster_info['ssh_config']:
                password = cluster_info['ssh_config']['password']
                
                # 检查是否已经加密
                if not password or password.startswith('ENC:'):
                    print(f"  {cluster_name}: 已经加密或密码为空，跳过")
                    continue
                
                # 加密密码
                cluster_info['ssh_config'] = crypto_manager.encrypt_ssh_config(
                    cluster_info['ssh_config']
                )
                encrypted_count += 1
                print(f"  {cluster_name}: 已加密")
    
    # 保存加密后的配置
    if encrypted_count > 0:
        print(f"\n正在保存加密后的配置...")
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        print(f"成功加密 {encrypted_count} 个集群配置")
        print(f"\n重要提示:")
        print(f"1. 加密密钥文件: .crypto.key")
        print(f"2. 请妥善保管密钥文件，丢失后无法解密配置")
        print(f"3. 原配置已备份到: {backup_file}")
    else:
        print("\n没有需要加密的配置")


def decrypt_and_show_config():
    """解密并显示配置（仅用于验证）"""
    config_file = '.clusters.yaml'
    
    if not os.path.exists(config_file):
        print(f"配置文件不存在: {config_file}")
        return
    
    print("正在读取并解密配置...")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if not config or 'clusters' not in config:
        print("配置文件格式错误")
        return
    
    print("\n解密后的配置:")
    print("-" * 60)
    
    for cluster_name, cluster_info in config['clusters'].items():
        print(f"\n集群: {cluster_name}")
        if 'ssh_config' in cluster_info:
            decrypted_config = crypto_manager.decrypt_ssh_config(cluster_info['ssh_config'])
            print(f"  主机: {decrypted_config.get('hostname', 'N/A')}")
            print(f"  用户: {decrypted_config.get('username', 'N/A')}")
            print(f"  密码: {decrypted_config.get('password', 'N/A')}")
            print(f"  端口: {decrypted_config.get('port', 22)}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'show':
        decrypt_and_show_config()
    else:
        encrypt_existing_config()
