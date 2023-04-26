# -*- coding: utf-8 -*-
import inspect
import time

from loguru import logger

from tools import handle_resp_data
from x.base import BaseClass


class Query(BaseClass):

    def __init__(self):
        self.block = self.Block()
        self.tx = self.Tx()
        self.bank = self.Bank()
        self.staking = self.Staking()
        self.mint = self.Mint()

    class Block(object):

        @staticmethod
        def query_block(height=""):
            cmd = Query.ssh_home + f"{Query.chain_bin} q block {height} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            if height:
                return handle_resp_data.handle_yaml_to_dict(res)
            else:
                resp = handle_resp_data.handle_yaml_to_dict(res)
                block_height = resp['block']['header']['height']
                return block_height

    class Tx(object):

        @staticmethod
        def query_tx(tx_hash):
            """查询 tx_hash """
            cmd = Query.ssh_home + f"{Query.chain_bin} q tx {tx_hash} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            time.sleep(5)
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

    class Bank(object):

        @staticmethod
        def query_balances(addr):
            """查询 addr 余额"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q bank balances {addr} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

    class Staking(object):

        @staticmethod
        def show_delegation(addr):
            """查询活期质押"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-delegation {addr} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            time.sleep(5)
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_delegation():
            """所有活期质押信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking list-delegation {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def list_fixed_delegation():
            """所有活期内周期质押信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking list-fixed-delegation {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_delegation(addr):
            """活期内周期质押信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-fixed-delegation {addr} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def kyc_by_region(region_id):
            """查询区域KYC列表"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking kyc-by-region {region_id} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def show_kyc(addr):
            """查看地址是否为kyc用户，不是将返回错误"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-kyc {addr} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd, strip=False)
            if res.stdout:
                return handle_resp_data.handle_yaml_to_dict(res.stdout)
            else:
                return res.stderr

        @staticmethod
        def list_kyc():
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking list-kyc {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def list_fixed_deposit():
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking list-fixed-deposit {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_id(addr, deposit_id):
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-fixed-deposit {addr} {deposit_id} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_addr(addr, query_type):
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-fixed-deposit-by-acct {addr} {query_type} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_region(region_id, query_type):
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-fixed-deposit-by-region {region_id} {query_type} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_region():
            """查询区域列表"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking list-region {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def show_region(region_id):
            """区金库信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-region {region_id} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_region_by_name(region_name):
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-region-by-name {region_name} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_validator():
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking list-validator {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        # validate 参数是 operator_address
        @staticmethod
        def show_validator(validator):
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking show-validator {validator} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def params():
            cmd = Query.ssh_home + f"{Query.chain_bin} q srstaking params {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

    class Mint(object):

        @staticmethod
        def params():
            """Query the current minting parameters"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q mint params {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))


if __name__ == '__main__':
    q = Query()
    # r = q.staking.show_region("bfdf8d44bc9211ed83a91e620a42e349")
    # r1 = q.staking.show_region_by_name("CZE")
    # from deepdiff import DeepDiff
    #
    # res = DeepDiff(r, r1)
    # r2 = q.staking.params()
    # r3 = q.mint.params()
    # print(r3)

    res = q.Block.query_block()
    pass
