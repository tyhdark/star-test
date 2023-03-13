# -*- coding: utf-8 -*-

ssh_info = {
    "config": dict(ip="XXXX", port=22, username="XXXX", password="XXXX"),
    "home": f"Project file path"
}

chain_id = "--chain-id=srspoa"
super_addr = "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh"
super_addr_home = " --home node1"

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
fixed_type = {
    0: "ALL_STATE",
    1: "NOT_EXPIRED",
    2: "EXPIRED"
}
