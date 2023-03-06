"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 16:35
@Version :  V1.0
@Desc    :  None
"""
from config import chain
from tools.host import Host


class BaseClass(object):
    ssh_info = chain.ssh_info["config"]
    ssh_client = Host(**ssh_info)

    ssh_home = chain.ssh_info["home"]
    chain_id = chain.chain_id
    channel = ssh_client.create_invoke_shell()
