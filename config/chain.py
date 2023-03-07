# -*- coding: utf-8 -*-


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
period = {
    1: "PERIOD_1_MONTHS",
    3: "PERIOD_3_MONTHS",
    6: "PERIOD_6_MONTHS",
    12: "PERIOD_12_MONTHS",
    24: "PERIOD_24_MONTHS",
    48: "PERIOD_48_MONTHS",
}
