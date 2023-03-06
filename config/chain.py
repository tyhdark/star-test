# -*- coding: utf-8 -*-
"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/3/6 16:42
@Version :  V1.0
@Desc    :  None
"""

ssh_info = {
    "config": dict(ip="192.168.0.206", port=22, username="xingdao", password="12345678"),
    "home": "cd /home/xingdao/chaintest && "
}

chain_id = "--chain-id=srspoa"
super_addr = "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh"
role = {
    0: "KYC_ROLE_ADMIN",
    1: "KYC_ROLE_USER",
}
