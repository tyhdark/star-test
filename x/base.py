"""
读取配置文件的连接参数用户名密码和ssh命令 (第二)
"""
from config import chain
from tools.host import Host


class BaseClass(object):
    # ssh_info = chain.ssh_info_me["config"]
    # ssh_info = chain.ssh_info_tg["config"]
    ssh_info = chain.ssh_info_meuser["config"]
    # 定义根目录
    ssh_home = chain.ssh_info_meuser["home"]  # home根目录
    # ssh_home = chain.ssh_info_tg["home"]  # home根目录
    # 实例化类，把ip地址等传参给类的属性
    # ssh_client = Host(**ssh_info)

    """定义flag里的--chain-id=me-chain"""
    chain_id = chain.chain_id_mueser

    # chain_id = chain.chain_id  # 定义链id required必要
    """定义./me-chain"""
    chain_bin = chain.chain_bin_mesuer  # 定义链目录,required必要

    # chain_bin = chain.chain_bin  # 定义链目录,required必要
    custom_node = chain.custom_node  # 定义常用节点,required必要

    # 超管这个是变化的
    super_addr = chain.super_addr  # 定义超管
    """定义--keyring-backend=test"""
    keyring_backend = chain.keyring_backend  # 后端Key

    coin = chain.coin_meuser  # 币的键值对

    # channel = ssh_client.create_invoke_shell()   # 建立ssh链接，调用shell

    # 重新部署链之后，初始时需要用到的一些数据
    node_name = chain.node_name
    to_account = chain.to_account
    region_id = chain.region_id
    region_name = chain.region_name
    amout = chain.amout
    # ssh_info = chain.ssh_info["config"]
    test_new_kyc_name = chain.test_new_kyc_nacme

    ssh_client = Host(**ssh_info)

    # ssh_home = chain.ssh_info["home"]
    # chain_id = chain.chain_id  # required
    # chain_bin = chain.chain_bin  # required
    # custom_node = chain.custom_node  # required
    # super_addr = chain.super_addr
    # keyring_backend = chain.keyring_backend
    # coin = chain.coin
    channel = ssh_client.create_invoke_shell()

    """
    # ssh_info = chain.ssh_info["config"]
    ssh_info = chain.ssh_info_meuser["config"]

    ssh_client = Host(**ssh_info)  # 实例化类，把ip地址等传参给类的属性

    ssh_home = chain.ssh_info["home"]  # home根目录
    chain_id = chain.chain_id  # 定义链id required必要
    chain_bin = chain.chain_bin  # 定义链目录,required必要
    custom_node = chain.custom_node  # 定义常用节点,required必要
    super_addr = chain.super_addr  # 定义超管
    keyring_backend = chain.keyring_backend  # 后端Key
    coin = chain.coin  # 币的键值对
    channel = ssh_client.create_invoke_shell()  # 定义虚拟链接频道
    """
