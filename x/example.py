# -*- coding: utf-8 -*-

from node import Node, Keys, Query, Tx

node1 = Node("--node=tcp://192.168.0.207:26657")


def keys():
    key_add_cmd = node1.generate_keys_cmd(Keys.add("python-user-1"))
    key_add = node1.executor(key_add_cmd)
    print(key_add)

    key_show_cmd = node1.generate_keys_cmd(Keys.show("python-user-1"))
    key_show = node1.executor(key_show_cmd)
    print(key_show)


def query():
    bal_cmd = node1.generate_query_cmd(Query.Bank.balances("me1nuyzepf9euy4u8s7n6f3c3lmfdh0gt4qjx24j4"))
    bal = node1.executor(bal_cmd)
    print(bal)

    # 各类提供help查看支持的方法
    print(Query.Bank.help())


def tx():
    init_send_cmd = Tx.Bank.send(
        "me16kgchstxh398tgprvduqjfyaa7atpvnd2mx7t7",
        "me1nuyzepf9euy4u8s7n6f3c3lmfdh0gt4qjx24j4",
        "10mec"
    )
    send_cmd = node1.generate_tx_cmd(init_send_cmd) + "-b=block"

    send = node1.executor(send_cmd)
    print(send)


def kyc():
    new_kyc_dict = {
        "from": node1.superadmin,
    }
    new_kyc_args = ["me1nuyzepf9euy4u8s7n6f3c3lmfdh0gt4qjx24j4", "arm", ]
    init_kyc_cmd = Tx.Staking.new_kyc(*new_kyc_args, **new_kyc_dict)
    tx_kyc_cmd = node1.generate_tx_cmd(init_kyc_cmd)
    result = node1.executor(tx_kyc_cmd)
    print(result)  # {'code': 0, 'txhash': '51AD13DC999D91F2106E62ABF86FD7B6F81AD4BDE212B98067A771D02809FC71'}


def delete_kyc():
    print(node1.executor(node1.generate_keys_cmd(Keys.add("test-0001"))))

    print("-------------------")

    key_delete_cmd = "echo 'y' | " + node1.generate_keys_cmd(Keys.delete("test-0001"))
    node1.executor(key_delete_cmd)


if __name__ == '__main__':
    # keys()
    # query()
    # tx()
    # kyc()
    delete_kyc()
    pass
