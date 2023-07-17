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
        self.key = self.Key()

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
            """查询用户余额，可用"""
            cmd = Query.work_home + f"{Query.chain_bin} q bank balances {addr} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))


    class Staking(object):  # 查询Staking

        @staticmethod
        def delegation(addr):
            """查询活期质押,可用"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking delegation {addr} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        # @staticmethod
        # def list_delegation():
        #     """所有活期质押信息"""
        #     cmd = Query.work_home + f"{Query.chain_bin} q srstaking list-delegation {Query.chain_id} {Query.connect_node}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_fixed_delegation():  # 固定委托列表,展示所有定期委托
            """查询所有定期委托，可用"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking list-fixed-delegation {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        # @staticmethod
        # def show_fixed_delegation(addr):  # 展示 固定质押 在活期内 传地址
        #     """活期内周期质押信息"""
        #     cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-fixed-delegation {addr} {Query.chain_id} {Query.connect_node}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def kyc_by_region(region_id):  # KYC 用户表示, 用户归属区
            """查询某个区域内的KYC列表，可用"""
            cmd = Query.work_home + f"{Query.chain_bin} query staking kyc-by-region {region_id} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_kyc(addr):
            """查看地址是否为kyc用户,不是将返回错误,可用"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking show-kyc {addr} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd, strip=False)
            if res.stdout:
                return Result.yaml_to_dict(res.stdout)
            else:
                return res.stderr

        @staticmethod
        def list_kyc():
            """查询KYC列表"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking list-kyc {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_fixed_deposit():
            """查询定期储存"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking list-fixed-deposit {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_id(addr, deposit_id):
            cmd = Query.work_home + f"{Query.chain_bin} q staking show-fixed-deposit {addr} {deposit_id} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_addr(addr, query_type):
            cmd = Query.work_home + f"{Query.chain_bin} q staking show-fixed-deposit-by-acct {addr} {query_type} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_region(region_id, query_type):
            cmd = Query.work_home + f"{Query.chain_bin} q staking show-fixed-deposit-by-region {region_id} {query_type} {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_region():
            """查询区域列表,可用"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking list-region {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        # @staticmethod
        # def show_region(region_id):
        #     cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-region {region_id} {Query.chain_id} {Query.connect_node}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        # @staticmethod
        # def show_region_by_name(region_name):
        #     cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-region-by-name {region_name} {Query.chain_id} {Query.connect_node}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def validators_list():
            """查询验证者节点列表"""
            cmd = Query.work_home + f"{Query.chain_bin} q staking validators {Query.chain_id} {Query.connect_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        # validate 参数是 operator_address
        # @staticmethod
        # def show_validator(validator):
        #     cmd = Query.work_home + f"{Query.chain_bin} q srstaking show-validator {validator} {Query.chain_id} {Query.connect_node}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))

        # @staticmethod
        # def params():
        #     cmd = Query.work_home + f"{Query.chain_bin} q srstaking params {Query.chain_id} {Query.connect_node}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Result.yaml_to_dict(Query.ssh_client.ssh(cmd))
    class Key(object):
        @staticmethod
        def keys_list():
            """
            查询本地用户列表
            """
            cmd = Query.work_home + f"{Query.chain_bin} keys list {Query.chain_bin} {Query.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return  Result.yaml_to_dict(Query.ssh_client.ssh((cmd)))
        @staticmethod
        def address_of_name(username=None):
            """
            根据用户名称导出用户的地址
            :param username: 用户的名称
            :return: 用户的地址
            """

            cmd = Query.work_home + f"{Query.chain_bin} keys show {username} -a {Query.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            # resp_info = Tx.ssh_client.ssh(cmd)

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
            logger.info(f"response status_code: {response.status_code}")
            assert response.status_code == 200
            return response.json()['tx_response']

    class Bank:
        @staticmethod
        def query_balances(addr):
            """接口文档查询用户余额，可以用"""
            url = HttpQuery.api_url + HttpQuery.query_bank_balances.format(address=addr)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            assert response.status_code == 200
            # 返回int格式，方便计算
            # return int(response.json().get('balances')[0]['amount'])
            if not response.json().get('balances'):
                return 0
            else:
                return int(response.json().get('balances')[0]['amount'])

    class Staking:
        @staticmethod
        def region(region_id=None):
            """
            查询区域信息
            :param region_id: 查询指定region_id的区域信息
            :param region_name: 查询指定region_name的区域信息
            :param region_id and region_name 都不传,默认查询所有区域信息
            """
            if region_id is not None:
                url = HttpQuery.api_url + HttpQuery.query_region_id.format(regionId=region_id)
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

            url = HttpQuery.api_url + HttpQuery.query_delegation.format(delegator_addr=addr)
            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            logger.info(f"response: {response}")
            assert response.status_code == 200

            return response.json().get('delegation_response').get('delegation')

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
            return response.json().get("validators")

        @staticmethod
        def kyc(addr=None):
            if addr is None:
                url =  HttpQuery.api_url + HttpQuery.query_kycs
            else:
                url = HttpQuery.api_url + HttpQuery.query_kyc.format(account=addr)

            logger.info(f"{inspect.stack()[0][3]}: {url}")
            response = HttpQuery.client.get(url=url)
            if response.status_code == 200:
                return response.json()
            else:
                return None

        @staticmethod
        def fixed_deposit(addr=None):
            if addr is None:
                url = HttpQuery.api_url + HttpQuery.query_deposits
            else:
                url = HttpQuery.api_url + HttpQuery.query_deposit.format(account=addr)

            logger.info(f"{inspect.stack()[0][3]}: {url}")
            respose = HttpQuery.client.get(url=url)
            return respose.json().get('FixedDeposit')

        @staticmethod
        def fixed_deposit_rate(month=None):

            url = HttpQuery.api_url + "/cosmos/staking/v1beta1/fixed_deposit_interest_rate"
            logger.info((f"{inspect.stack()[0][3]}: {url}"))
            respose = HttpQuery.client.get(url=url)
            if month is None:
                return respose.json().get('FixedDepositAnnualRate')
            else:
                return respose.json().get('FixedDepositAnnualRate').get(f'annualRate_{month}_months')


if __name__ == '__main__':
    # q = HttpQuery()
    # r3 = q.staking.region()
    # print(r3)
    # print(q.Bank.query_balances(addr=Query.super_addr))
    q_ssh =Query()

    # print(q_ssh.Staking.validators_list()) # 验证者列表
    # print(q_ssh.Staking.list_region()) # 区列表
    # print(q_ssh.Staking.list_kyc()) # KYC
    # print(q_ssh.Staking.list_fixed_delegation()) # 定期
    # print(q_ssh.Staking.delegation("me1qsx0a3ysfmvum803gqf7qwn9rznzk7cdunlxne")) # 活期委托
    # print(q_ssh.Staking.kyc_by_region(region_id="jpn"))
    # print(q_ssh.Staking.list_fixed_deposit())
    hq = HttpQuery()
    print(hq.Staking.delegation(addr="me13a4rmm64wetlatj5z6jcfxkxtraxdcm8jl0z8u"))
    # print(hq.Tx.query_tx(tx_hash="36B83E7A30FB8D45FB24860E95EC95968F566CFAF4E5020EFA58936B475C25F6"))
    # v = hq.Staking.validator()
    # print(v)
    # l = [i.get('description').get('moniker') for i in v]
    # print(l)
    # r = hq.Staking.region()
    # print(r.get('region'))
    # for i in r.get('region'):
    #     print(i.get('name'))
    # l = [i.get('name') for i in hq.Staking.region().get('region')]
    # print(r)
    # print(r)
    # print(hq.Staking.kyc(addr="me1q6v4ud6dy0dh3k0jnpva287n7m3wlv3w2qgnwc"))
    # l = hq.Staking.fixed_deposit(addr="me10xujye2ceftjakuzhx6pg7ecaj7x0qrrg0kexa")
    # print(l)
    # ll = [i.get('id') for i in hq.Staking.fixed_deposit(addr="me10xujye2ceftjakuzhx6pg7ecaj7x0qrrg0kexa")]
    # print(ll)
    # print(hq.Staking.fixed_deposit_rate())
    # print(q_ssh.Bank.query_balances("me1f5mcf4cw8av4jzh2zygnjcmvsqgygac77zsrtu"))

    pass
