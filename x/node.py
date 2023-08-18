# -*- coding: utf-8 -*-
import inspect
from typing import Callable

from loguru import logger

from config.config import app_chain
from ssh import Client, Result


class Meta(type):
    def __init__(cls, name, bases, attrs):
        cls.module = name.lower()
        super().__init__(name, bases, attrs)

        sub_module = attrs.get('sub_module', [])
        parent_module = attrs.get('parent_module', '')
        if isinstance(sub_module, list):
            for module in sub_module:
                method = cls.generate_method(parent_module, module)
                setattr(cls, module, classmethod(method))
        elif isinstance(sub_module, dict):
            for k, module in sub_module.items():
                method = cls.generate_method(parent_module, module)
                setattr(cls, k, classmethod(method))
        else:
            raise f"sub_module type error: {type(sub_module)}, expect list or dict"

    @staticmethod
    def generate_method(parent_module, sub_module) -> Callable[..., str]:
        def method(cls, *args, **kwargs):
            return cls.build_command(parent_module, sub_module, *args, **kwargs)

        return method

    def build_command(cls, parent_module, sub_module, *args, **kwargs):
        args_str = " ".join(map(str, args))
        kwargs_str = " ".join([f"--{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{parent_module} {cls.module} {sub_module} {args_str} {kwargs_str} "

    def __getattr__(cls, attr):
        raise AttributeError(f"'{cls.__name__}' class has no attribute '{attr}'")

    def help(cls):
        for attr_name in cls.sub_module:
            attr = getattr(cls, attr_name)
            if not callable(attr):
                raise TypeError(f"attribute '{attr_name}' is not callable")
        print(f"Available methods: {list(cls.sub_module)}")
        print(f"Example usage: {cls.__name__}.{list(cls.sub_module)[0]}('argument')")


class Keys(metaclass=Meta):
    sub_module = ["add", "delete", "export", "import", "list", "migrate", "mnemonic", "parse", "rename", "show"]


class Query(metaclass=Meta):
    sub_module = ["block", "tx"]

    class Bank(metaclass=Meta):
        parent_module = "query"
        sub_module = dict(
            balances="balances",
            denom_metadata="denom-metadata",
            total="total"
        )

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

    class Distribution(metaclass=Meta):
        parent_module = "query"
        sub_module = dict(
            rewards="rewards",
            params="params",
        )

    class Group(metaclass=Meta):
        parent_module = "query"
        sub_module = dict(
            group_info="group-info",
            group_members="group-members",
            groups_by_admin="groups-by-admin",
            groups_by_member="groups-by-member",
        )


class Tx(metaclass=Meta):
    class Bank(metaclass=Meta):
        parent_module = "tx"
        sub_module = dict(
            send="send",
            multi_send="multi-send",
            send_to_admin="sendToAdmin",
            send_to_treasury="sendToTreasury",
        )

    class Staking(metaclass=Meta):
        parent_module = "tx"
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

    class Distribution(metaclass=Meta):
        parent_module = "tx"
        sub_module = dict(
            withdraw_rewards="withdraw-rewards",
        )

    class Group(metaclass=Meta):
        parent_module = "tx"
        sub_module = dict(
            create_group="create-group",
            update_group="delete-group",
            leave_group="leave-group",
            update_group_member="update-group-member",
        )


class Node:
    ssh_client = Client(ip=app_chain.Host.ip, port=app_chain.Host.port,
                        username=app_chain.Host.username, password=app_chain.Host.password)
    config = app_chain

    def __init__(self, node: str):
        super().__init__()
        if "--node" not in node:
            node = f"--node={node}"
        self.config.Flags.node = node
        self.superadmin = self.__get_superadmin_addr()
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
        return f"{self.config.Host.chain_work_path} "

    def __get_superadmin_addr(self):
        get_superadmin_cmd = f"{self.base_cmd} keys show superadmin -a {self.config.Flags.keyring_backend}"
        return self.ssh_client.exec_cmd(get_superadmin_cmd)

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
            _ = self.ssh_client.channel.send(cmd + "\n")
            resp_info = self.ssh_client.Interactive.read_channel_data(self.ssh_client.channel)
            if "existing" in resp_info:
                resp_info = self.ssh_client.Interactive.input_yes_or_no(self.ssh_client.channel)
            assert "**Important**" in resp_info
            return resp_info

        resp_info = self.ssh_client.exec_cmd(cmd, strip=False)
        if resp_info.failed:
            logger.info(f"resp_info.stderr: {resp_info.stderr}")
            return resp_info.stderr
        return Result.yaml_to_dict(resp_info.stdout)


if __name__ == '__main__':
    pass
