from config.chain import config
from tools.host import Host


class BaseClass(object):
    ssh_client = Host(**config["host"])
    channel = ssh_client.create_invoke_shell()

    # chain base config
    work_home = config["chain"]["work_dir"]
    chain_id = config["chain"]["chain_id"]
    chain_bin = config["chain"]["chain_bin"]
    connect_node = config["chain"]["connect_node"]
    super_addr = config["chain"]["super_addr"]
    keyring_backend = config["chain"]["keyring_backend"]
    coin = config["chain"]["token_unit"]
