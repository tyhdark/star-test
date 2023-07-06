# -*- coding: utf-8 -*-
import inspect
import time

import httpx
from loguru import logger

from tools.console import Result
from x.base import BaseClass
"""查询用的,查询各种信息,  (第四)
查询区块
转账交易
库
质押权益
铸造厂
"""

class Query(BaseClass):
    """
    查询类
    """

    def __init__(self):
        self.block = self.Block()
        self.tx = self.Tx()
        self.bank = self.Bank()
        self.staking = self.Staking()
        self.mint = self.Mint()

    class Block(object):

        @staticmethod
        def query_block(height=""):
            cmd = Query.work_home + f"{Query.chain_bin} q block {height} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            if height:
                return Result.yaml_to_dict(res)
            else:
                resp = Result.yaml_to_dict(res)
                block_height = resp['block']['header']['height']
                return block_height

    class Tx(object):

        @staticmethod
        def query_tx(tx_hash):
            cmd = Query.work_home + f"{Query.chain_bin} q tx {tx_hash} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

    class Bank(object):

        @staticmethod
        def query_balances(addr):
            cmd = Query.work_home + f"{Query.chain_bin} q bank balances {addr} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))


    class Staking(object):  # 权益质押

        @staticmethod
        def show_delegation(addr):
            """查询活期质押"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-delegation {addr} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_delegation():
            """所有活期质押信息"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-delegation {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_fixed_delegation():  # 固定委托列表,展示所有活期内周期质押信息
            """所有活期内周期质押信息"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-fixed-delegation {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_delegation(addr):  # 展示 固定质押 在活期内 传地址
            """活期内周期质押信息"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-fixed-delegation {addr} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def kyc_by_region(region_id):  # KYC 用户表示, 用户归属区
            """查询区域KYC列表"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking kyc-by-region {region_id} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_kyc(addr):
            """查看地址是否为kyc用户,不是将返回错误"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-kyc {addr} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd, strip=False)
            if res.stdout:
                return Result.yaml_to_dict(res.stdout)
            else:
                return res.stderr

        @staticmethod
        def list_kyc():
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-kyc {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_fixed_deposit():
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-fixed-deposit {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_id(addr, deposit_id):
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-fixed-deposit {addr} {deposit_id} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_addr(addr, query_type):
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-fixed-deposit-by-acct {addr} {query_type} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_region(region_id, query_type):
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-fixed-deposit-by-region {region_id} {query_type} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_region():
            """查询区域列表"""
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-region {Query.chain_id} {Query.connect_node}"
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-region {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_region(region_id):
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-region {region_id} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_region_by_name(region_name):
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-region-by-name {region_name} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_validator():
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-validator {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        # validate 参数是 operator_address
        @staticmethod
        def show_validator(validator):
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-validator {validator} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def params():
            cmd = Query.work_home + f"{Query.chain_bin} q srstaking params {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

    class Mint(object):

        @staticmethod
        def params():
            """Query the current minting parameters"""
            cmd = Query.work_home + f"{Query.chain_bin} q mint params {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))


class HttpQuery(BaseClass):
    client = httpx.Client()

    def __init__(self):
        self.block = self.Block()
        self.tx = self.Tx()
        self.bank = self.Bank()
        self.staking = self.Staking()

    class Block:
        @staticmethod
        def query_block(height=None):
            if height is None:
                url = HttpQuery.api_url + HttpQuery.query_block_latest
            else:
                url = HttpQuery.api_url + HttpQuery.query_block.format(height=height)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            assert response.status_code == 200
            return response.json()['block']

    class Tx:
        @staticmethod
        def query_tx(tx_hash):
            url = HttpQuery.api_url + HttpQuery.query_tx_hash.format(hash=tx_hash)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            logger.debug(f"response: {response}")
            assert response.status_code == 200
            return response.json()['tx_response']

    class Bank:
        @staticmethod
        def query_balances(addr):
            url = HttpQuery.api_url + HttpQuery.query_bank_balances.format(address=addr)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            assert response.status_code == 200
            return response.json()['balances']

    class Staking:
        @staticmethod
        def region(region_id=None, region_name=None):
            """
            查询区域信息
            :param region_id: 查询指定region_id的区域信息
            :param region_name: 查询指定region_name的区域信息
            :param region_id and region_name 都不传,默认查询所有区域信息
            """
            if region_id is not None:
                url = HttpQuery.api_url + HttpQuery.query_region_id.format(id=region_id)
            elif region_name is not None:
                url = HttpQuery.api_url + HttpQuery.query_region_name.format(name=region_name)
            else:
                url = HttpQuery.api_url + HttpQuery.query_regions
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            assert response.status_code == 200
            return response.json()

        @staticmethod
        def delegation(addr=None):
            """
            查询委托信息
            :param addr: 传入addr 查询某个地址委托,不传查询所有委托
            """
            if addr is None:
                url = HttpQuery.api_url + HttpQuery.query_delegations
            else:
                url = HttpQuery.api_url + HttpQuery.query_delegation.format(addr=addr)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            logger.info(f"response: {response}")
            assert response.status_code == 200
            return response.json()['delegation']

        @staticmethod
        def validator(addr=None):
            if addr is None:
                url = HttpQuery.api_url + HttpQuery.query_validators
            else:
                url = HttpQuery.api_url + HttpQuery.query_validator.format(address=addr)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            logger.info(f"response: {response}")
            assert response.status_code == 200
            return response.json()['validator']


if __name__ == '__main__':
    q = HttpQuery()
    r3 = q.staking.region()
    print(r3)
    pass
