"""
读取配置文件的连接参数用户名密码和ssh命令 (第二)
"""
from config import chain
from tools.host import Host


class BaseClass(object):
    ssh_info = chain.ssh_info["config"]
    ssh_client = Host(**ssh_info)  # 传参自动转成字典

    ssh_home = chain.ssh_info["home"]  # home根目录
    chain_id = chain.chain_id  # 定义链id required必要
    chain_bin = chain.chain_bin  # 定义链目录,required必要
    custom_node = chain.custom_node  # 定义常用节点,required必要
    super_addr = chain.super_addr  # 定义超管
    keyring_backend = chain.keyring_backend  # 后端Key
    coin = chain.coin  # 币的键值对
    channel = ssh_client.create_invoke_shell()  # 定义虚拟链接频道
