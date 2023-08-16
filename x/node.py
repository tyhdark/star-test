# -*- coding: utf-8 -*-
import inspect

from loguru import logger

from config.config import app_chain
from tools.console import Result
from tools.host import Host


class Query:
    type = "q"

    class Block:
        module = "block"

        @classmethod
        def block(cls, height="", *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {height} {args}"

    class Tx:
        module = "tx"

        @classmethod
        def tx(cls, tx_hash, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {tx_hash} {args}"

    class Bank:
        module = "bank"
        sub_module = dict(balances="balances")

        @classmethod
        def balances(cls, addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['balances']} {addr} {args}"

    class Staking:
        module = "staking"
        sub_module = dict(
            delegation="delegation",
            delegations_to="delegations-to",
            historical_info="historical-info",
            kyc_by_region="kyc-by-region",
            list_fixed_deposit="list-fixed-deposit",
            list_kyc="list-kyc",
            list_region="list-region",
            list_siid="list-siid",
            params="params",
            show_fixed_deposit="show-fixed-deposit",
            show_fixed_deposit_by_acct="show-fixed-deposit-by-acct",
            show_fixed_deposit_by_region="show-fixed-deposit-by-region",
            show_fixed_deposit_interest_rate="show-fixed-deposit-interest-rate",
            show_kyc="show-kyc",
            show_region="show-region",
            show_siid="show-siid",
            siid_by_account="siid-by-account",
            unbonding_delegation="unbonding-delegation",
            validator="validator",
            validators="validators", )

        @classmethod
        def delegation(cls, addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['delegation']} {addr} {args}"

        @classmethod
        def delegations_to(cls, validator_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['delegations_to']} {validator_addr} {args}"

        @classmethod
        def historical_info(cls, height, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['historical_info']} {height} {args}"

        @classmethod
        def kyc_by_region(cls, region, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['kyc_by_region']} {region} {args}"

        @classmethod
        def list_fixed_deposit(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['list_fixed_deposit']} {args}"

        @classmethod
        def list_kyc(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['list_kyc']} {args}"

        @classmethod
        def list_region(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['list_region']} {args}"

        @classmethod
        def list_siid(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['list_siid']} {args}"

        @classmethod
        def params(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['params']} {args}"

        @classmethod
        def show_fixed_deposit(cls, fixed_deposit_id, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_fixed_deposit']} {fixed_deposit_id} {args}"

        @classmethod
        def show_fixed_deposit_by_acct(cls, account_addr, fixed_deposit_id, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_fixed_deposit_by_acct']} {account_addr} {fixed_deposit_id} {args}"

        @classmethod
        def show_fixed_deposit_by_region(cls, region, fixed_deposit_id, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_fixed_deposit_by_region']} {region} {fixed_deposit_id} {args}"

        @classmethod
        def show_fixed_deposit_interest_rate(cls, fixed_deposit_id, interest_rate, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_fixed_deposit_interest_rate']} {fixed_deposit_id} {interest_rate} {args}"

        @classmethod
        def show_kyc(cls, account_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_kyc']} {account_addr} {args}"

        @classmethod
        def show_region(cls, region, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_region']} {region} {args}"

        @classmethod
        def show_siid(cls, siid, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['show_siid']} {siid} {args}"

        @classmethod
        def siid_by_account(cls, account_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['siid_by_account']} {account_addr} {args}"

        @classmethod
        def unbonding_delegation(cls, account_addr, validator_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['unbonding_delegation']} {account_addr} {validator_addr} {args}"

        @classmethod
        def validator(cls, validator_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['validator']} {validator_addr} {args}"

        @classmethod
        def validators(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.type} {cls.module} {cls.sub_module['validator']}   {args}"


class Tx:
    type = "tx"

    class Bank:
        module = "bank"
        sub_module = dict(
            send="send",
            multi_send="multi-send",
            send_to_admin="sendToAdmin",
            send_to_treasury="sendToTreasury",
        )

        @classmethod
        def send(cls, from_addr, to_addr, amount, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Tx.type} {cls.module} {cls.sub_module['send']} {from_addr} {to_addr} {amount} {args}"

        @classmethod
        def send_to_admin(cls, from_addr, amount, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Tx.type} {cls.module} {cls.sub_module['send_to_admin']} {from_addr} {amount} {args}"

        @classmethod
        def send_to_treasury(cls, from_addr, amount, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Tx.type} {cls.module} {cls.sub_module['send_to_treasury']} {from_addr} {amount} {args}"


class Node:
    ssh_client = Host(ip=app_chain.Host.ip, port=app_chain.Host.port,
                      username=app_chain.Host.username, password=app_chain.Host.password)
    channel = ssh_client.create_invoke_shell()
    config = app_chain

    def __init__(self, node: str):
        super().__init__()
        if "--node" not in node:
            node = f"--node={node}"
        self.config.Flags.node = node

        self.__init_instance_config()

    def update_config(self, attr: str, key: str, value: str):
        """
        If key exists in the attr object, replace the value. If no, add the value
        :param attr: 'ApplicationChain' object must have attr
        :param key:
        :param value:
        :return:
        """
        sub_cfg_gen = getattr(self.config, attr)
        found_key = False
        for i in sub_cfg_gen:
            if i[0] == key:
                setattr(sub_cfg_gen, key, value)
                found_key = True
                break
        if not found_key:
            setattr(sub_cfg_gen, key, value)

    def __init_instance_config(self):
        self.update_config("Flags", "fees", "--fees=100umec")
        self.update_config("Flags", "gas", "--gas=200000")

    @property
    def base_cmd(self):
        cmd = (f"{self.config.Host.work_dir} {self.config.Host.chain_bin} {self.config.Flags.node} "
               f"{self.config.GlobalFlags.chain_id} ")
        return cmd

    def generate_query_cmd(self, cmd: str):
        return self.base_cmd + cmd

    def generate_tx_cmd(self, cmd: str):
        tx_cmd = self.base_cmd + (f"{self.config.Flags.fees} {self.config.Flags.gas} "
                                  f"{self.config.Flags.yes} {self.config.Flags.keyring_backend} ")
        return tx_cmd + cmd

    def executor(self, cmd):
        resp_info = self.ssh_client.ssh(cmd, strip=False)
        if resp_info.failed:
            logger.info(f"{inspect.stack()[0][3]} resp_info.stderr: {resp_info.stderr}")
            return resp_info.stderr
        return Result.yaml_to_dict(resp_info.stdout)


if __name__ == '__main__':
    node1 = Node("--node=tcp://192.168.0.207:26657")
    # print(node1.base_cmd)
    #
    # q_block = Query.Block.block()
    #
    # print(node1.generate_query_cmd(q_block))
    #
    # q_balances = Query.Bank.balances("me12tr8ju53p7hp3t70hy9k83wvctut350etfn0d6")
    #
    # res = node1.executor(node1.generate_query_cmd(q_balances))
    # print(res)
    send_cmd = Tx.Bank.send(
        "me16kgchstxh398tgprvduqjfyaa7atpvnd2mx7t7",
        "me12tr8ju53p7hp3t70hy9k83wvctut350etfn0d6",
        "100mec"
    )
    send_cmd += "-b=block"
    res2 = node1.executor(node1.generate_tx_cmd(send_cmd))
    print(res2)
    # for arg in args:
    #     var = getattr(self.config.Flags, arg)
    #     base_cmd += var + " "
    pass
