"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 16:35
@Version :  V1.0
@Desc    :  None
"""
from tools.host import Host


class BaseClass(object):
    ssh_info = dict(ip="192.168.0.206", port=22, username="xingdao", password="12345678")
    ssh_client = Host(**ssh_info)

    ssh_home = "cd /home/xingdao/chaintest && "
    channel = ssh_client.create_invoke_shell()
