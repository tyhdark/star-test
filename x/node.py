# -*- coding: utf-8 -*-
import inspect

from loguru import logger

from config.config import app_chain
from tools.console import Result, Interaction
from tools.host import Host


class Meta(type):
    def __init__(cls, name, bases, attrs):
        cls.module = name.lower()
        super().__init__(name, bases, attrs)

    def build_command(cls, sub_module, *args, **kwargs):
        args_str = " ".join(map(str, args))
        kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{cls.module} {sub_module} {args_str} {kwargs_str} "


class Query(metaclass=Meta):
    class Block(metaclass=Meta):

        @classmethod
        def block(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {args} {kwargs_str} "

    class Tx(metaclass=Meta):

        @classmethod
        def tx(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {args} {kwargs_str} "

    class Bank(metaclass=Meta):
        sub_module = dict(balances="balances")

        @classmethod
        def balances(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['balances']} {args} {kwargs_str} "

    class Staking(metaclass=Meta):
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
        def delegation(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['delegation']} {args} {kwargs_str} "

        @classmethod
        def delegations_to(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['delegations_to']} {args} {kwargs_str} "

        @classmethod
        def historical_info(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['historical_info']} {args} {kwargs_str} "

        @classmethod
        def kyc_by_region(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['kyc_by_region']} {args} {kwargs_str} "

        @classmethod
        def list_fixed_deposit(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['list_fixed_deposit']} {args} {kwargs_str} "

        @classmethod
        def list_kyc(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['list_kyc']} {args} {kwargs_str} "

        @classmethod
        def list_region(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['list_region']} {args} {kwargs_str} "

        @classmethod
        def list_siid(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['list_siid']} {args} {kwargs_str}"

        @classmethod
        def params(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Query.module} {cls.module} {cls.sub_module['params']} {args} {kwargs_str} "

        @classmethod
        def show_fixed_deposit(cls, fixed_deposit_id, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_fixed_deposit']} {fixed_deposit_id} {args}"

        @classmethod
        def show_fixed_deposit_by_acct(cls, account_addr, fixed_deposit_id, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_fixed_deposit_by_acct']} {account_addr} {fixed_deposit_id} {args}"

        @classmethod
        def show_fixed_deposit_by_region(cls, region, fixed_deposit_id, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_fixed_deposit_by_region']} {region} {fixed_deposit_id} {args}"

        @classmethod
        def show_fixed_deposit_interest_rate(cls, fixed_deposit_id, interest_rate, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_fixed_deposit_interest_rate']} {fixed_deposit_id} {interest_rate} {args}"

        @classmethod
        def show_kyc(cls, account_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_kyc']} {account_addr} {args}"

        @classmethod
        def show_region(cls, region, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_region']} {region} {args}"

        @classmethod
        def show_siid(cls, siid, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['show_siid']} {siid} {args}"

        @classmethod
        def siid_by_account(cls, account_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['siid_by_account']} {account_addr} {args}"

        @classmethod
        def unbonding_delegation(cls, account_addr, validator_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['unbonding_delegation']} {account_addr} {validator_addr} {args}"

        @classmethod
        def validator(cls, validator_addr, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['validator']} {validator_addr} {args}"

        @classmethod
        def validators(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            return f"{Query.module} {cls.module} {cls.sub_module['validator']}   {args}"


class Tx(metaclass=Meta):
    class Bank(metaclass=Meta):
        sub_module = dict(
            send="send",
            multi_send="multi-send",
            send_to_admin="sendToAdmin",
            send_to_treasury="sendToTreasury",
        )

        @classmethod
        def send(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['send']} {args} {kwargs_str} "

        @classmethod
        def send_to_admin(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['send_to_admin']} {args} {kwargs_str} "

        @classmethod
        def send_to_treasury(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['send_to_treasury']} {args} {kwargs_str} "

    class Staking(metaclass=Meta):
        sub_module = dict(
            create_validator="create-validator",
            delegate="delegate",
            deposit_fixed="deposit-fixed",
            edit_validator="edit-validator",
            new_kyc="new-kyc",
            new_region="new-region",
            new_siid="new-siid",
            remove_region="remove-region",
            remove_siid="remove-siid",
            set_fixed_deposit_interest_rate="set-fixed-deposit-interest-rate",
            stake="stake",
            unkyc_unbond="unKycUnbond",
            unbond="unbond",
            unstake="unstake",
            withdraw_fixed="withdraw-fixed",
        )

        @classmethod
        def create_validator(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['create_validator']} {args} {kwargs_str} "

        @classmethod
        def delegate(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['delegate']} {args} {kwargs_str} "

        @classmethod
        def deposit_fixed(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['deposit_fixed']} {args} {kwargs_str} "

        @classmethod
        def edit_validator(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['edit_validator']} {args} {kwargs_str} "

        @classmethod
        def new_kyc(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['new_kyc']} {args} {kwargs_str} "

        @classmethod
        def new_region(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['new_region']} {args} {kwargs_str} "

        @classmethod
        def new_siid(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['new_siid']} {args} {kwargs_str} "

        @classmethod
        def remove_region(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['remove_region']} {args} {kwargs_str} "

        @classmethod
        def remove_siid(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['remove_siid']} {args} {kwargs_str} "

        @classmethod
        def set_fixed_deposit_interest_rate(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['set_fixed_deposit_interest_rate']} {args} {kwargs_str} "

        @classmethod
        def stake(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['stake']} {args} {kwargs_str} "

        @classmethod
        def unkyc_unbond(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['unkyc_unbond']} {args} {kwargs_str} "

        @classmethod
        def unbond(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['unbond']} {args} {kwargs_str} "

        @classmethod
        def unstake(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['unstake']} {args} {kwargs_str} "

        @classmethod
        def withdraw_fixed(cls, *args, **kwargs):
            args = " ".join(map(str, args))
            kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
            return f"{Tx.module} {cls.module} {cls.sub_module['withdraw_fixed']} {args} {kwargs_str} "


class Keys(metaclass=Meta):
    sub_module = dict(
        add="add",
        delete="delete",
        export="export",
        import_="import",
        list="list",
        migrate="migrate",
        mnemonic="mnemonic",
        parse="parse",
        rename="rename",
        show="show",
    )

    @classmethod
    def add(cls, *args, **kwargs):
        return cls.build_command(cls.sub_module['add'], *args, **kwargs)
        # return f"{cls.module} {cls.sub_module['add']} {args} {kwargs_str} "

    @classmethod
    def delete(cls, *args, **kwargs):
        args = " ".join(map(str, args))
        kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{cls.module} {cls.sub_module['delete']} {args} {kwargs_str} "

    @classmethod
    def export(cls, *args, **kwargs):
        args += ("--unarmored-hex", "--unsafe")
        args = " ".join(map(str, args))
        kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{cls.module} {cls.sub_module['export']} {args} {kwargs_str} "

    @classmethod
    def list(cls, *args, **kwargs):
        args = " ".join(map(str, args))
        kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{cls.module} {cls.sub_module['list']} {args} {kwargs_str} "

    @classmethod
    def show(cls, *args, **kwargs):
        args = " ".join(map(str, args))
        kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{cls.module} {cls.sub_module['show']} {args} {kwargs_str} "


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
        self.superadmin = self.__superadmin()
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

    def __superadmin(self):
        get_superadmin_addr = f"{self.config.Host.chain_work_path} keys show superadmin -a {self.config.Flags.keyring_backend}"
        return self.ssh_client.ssh(get_superadmin_addr)

    @property
    def base_cmd(self):
        return f"{self.config.Host.chain_work_path} "

    def generate_query_cmd(self, cmd: str):
        query_cmd = self.base_cmd + f"{self.config.Flags.node} {self.config.GlobalFlags.chain_id} "
        return query_cmd + cmd

    def generate_tx_cmd(self, cmd: str):
        tx_cmd = self.base_cmd + (f"{self.config.Flags.fees} {self.config.Flags.gas} "
                                  f"{self.config.Flags.yes} {self.config.Flags.keyring_backend} "
                                  f"{self.config.Flags.node} {self.config.GlobalFlags.chain_id} ")
        return tx_cmd + cmd

    def generate_keys_cmd(self, cmd: str):
        keys_cmd = self.base_cmd + f"{self.config.Flags.keyring_backend} "
        return keys_cmd + cmd

    def executor(self, cmd):
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        if "keys add" in cmd:
            _ = self.channel.send(cmd + "\n")
            resp_info = Interaction.ready(self.channel)
            if "existing" in resp_info:
                resp_info = Interaction.yes_or_no(self.channel)
            assert "**Important**" in resp_info
            return resp_info

        resp_info = self.ssh_client.ssh(cmd, strip=False)
        if resp_info.failed:
            logger.info(f"resp_info.stderr: {resp_info.stderr}")
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
    # send_cmd = Tx.Bank.send(
    #     "me16kgchstxh398tgprvduqjfyaa7atpvnd2mx7t7",
    #     "me12tr8ju53p7hp3t70hy9k83wvctut350etfn0d6",
    #     "100mec"
    # )
    # send_cmd += "-b=block"

    # keys_add = Keys.add("test-py-2")
    # keys_export = Keys.export("test-py-2")
    # keys_export = node1.generate_keys_cmd(keys_export)
    # keys_export = 'echo "y" | ' + keys_export
    # res2 = node1.executor(keys_export)
    # print(res2)
    # print(node1.executor(node1.generate_keys_cmd(Keys.list())))

    # new_kyc_dict = {
    #     "from": node1.superadmin,
    #     # "account": "me1xqzz674wqnzsdcqszmcwwe3u587jhhlwyyukdk",
    #     # "region_id": "ITA",
    #     # "inviteAccount": "",
    # }
    # new_kyc_args = ["me1xqzz674wqnzsdcqszmcwwe3u587jhhlwyyukdk", "arm", ]
    # res = Tx.Staking.new_kyc(*new_kyc_args, **new_kyc_dict)
    # cmd1 = node1.generate_tx_cmd(res) + "-b=block"
    # result = node1.executor(cmd1)
    #
    # print(result)
    # for arg in args:
    #     var = getattr(self.config.Flags, arg)
    #     base_cmd += var + " "

    key_cmd = Keys.add("test-py-3")
    key_add_cmd = node1.generate_keys_cmd(key_cmd)
    res = node1.executor(key_add_cmd)
    print(res)

    pass
