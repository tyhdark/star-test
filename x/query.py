# -*- coding: utf-8 -*-
"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/3/6 14:33
@Version :  V1.0
@Desc    :  None
"""
import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_resp_data


class Query(BaseClass):

    def __init__(self):
        self.block = self.Block()
        self.tx = self.Tx()
        self.bank = self.Bank()
        self.region = self.Staking()

    class Block(object):

        @staticmethod
        def query_block(height=""):
            cmd = Query.ssh_home + f"./srs-poad q block {height}"
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
            cmd = Query.ssh_home + f"./srs-poad q tx {tx_hash}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            time.sleep(5)
            res = Query.ssh_client.ssh(cmd)
            time.sleep(1)
            return handle_resp_data.handle_yaml_to_dict(res)

    class Bank(object):

        @staticmethod
        def query_balances(addr):
            """查询 addr 余额"""
            cmd = Query.ssh_home + f"./srs-poad q bank balances {addr}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

    class Staking(object):

        @staticmethod
        def query_list_region():
            """查询区域列表"""
            cmd = Query.ssh_home + f"./srs-poad q srstaking list-region {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def show_region_vault(region_id):
            """区金库信息"""
            cmd = Query.ssh_home + f"./srs-poad q srstaking show-region {region_id} {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_fixed_deposit():
            cmd = Query.ssh_home + f"./srs-poad q srstaking list-fixed-deposit {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_id(deposit_id):
            cmd = Query.ssh_home + f"./srs-poad q srstaking show-fixed-deposit {deposit_id} {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_addr(addr):
            cmd = Query.ssh_home + f"./srs-poad q srstaking show-fixed-deposit-by-acct {addr} {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_kyc():
            cmd = Query.ssh_home + f"./srs-poad q srstaking list-kyc {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def show_kyc(addr):
            """查看地址是否为kyc用户，不是将返回错误"""
            cmd = Query.ssh_home + f"./srs-poad q srstaking show-kyc {addr} {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd, strip=False)
            if res.stdout:
                return handle_resp_data.handle_yaml_to_dict(res.stdout)
            else:
                return res.stderr

        @staticmethod
        def kyc_bonus(addr):
            """查询KYC用户注册所赠1src收益  可能在region 里面"""
            cmd = Query.ssh_home + f"./srs-poad q srstaking kyc-bonus {addr} {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def list_region_vault():
            """所有区金库信息  已重构 这个命令不确定是否还存在"""
            cmd = Query.ssh_home + f"./srs-poad q srvault list-region-vault {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)


if __name__ == '__main__':
    q = Query()
    r = q.block.query_block()
    print(r)
