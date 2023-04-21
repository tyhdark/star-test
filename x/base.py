from config import chain
from tools.host import Host


class BaseClass(object):
    ssh_info = chain.ssh_info["config"]
    ssh_client = Host(**ssh_info)

    ssh_home = chain.ssh_info["home"]
    chain_id = chain.chain_id  # required
    chain_bin = chain.chain_bin  # required
    custom_node = chain.custom_node  # required
    super_addr = chain.super_addr
    keyring_backend = chain.keyring_backend
    coin = chain.coin
    channel = ssh_client.create_invoke_shell()
