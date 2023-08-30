# -*- coding: utf-8 -*-
import os
import sys
import time

import pytest
import yaml
from loguru import logger

from cases import unitcases
from tools.compute import Compute, WaitBlock
from tools.parse_response import HttpResponse
from tools.rewards import Reward
from x.tx import Tx

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
current_path = os.path.dirname(__file__)
with open(current_path + '/test_validator.yml', 'r', encoding='gbk') as file:
    test_data = yaml.safe_load(file)


class TestVali(object):
    tx = Tx()

    def test_vali(self):
        """
        测试成功创建验证者节点，传入成功的参数进去  tendermint  Tendermint subcommands
        """
        # 数据准备
        # 创建节点
        Tx.Staking.create_validator()
        # 查询节点
        pass

    @pytest.mark.parametrize("stake_data", test_data)
    def test_vali_stake(self, stake_data):
        """
        测试增加验证者节点的stake值
        """
        moniker, amount = stake_data['moniker'], stake_data['amount']
        result_list = HttpResponse.get_validator_list()
        operator = [i['operator_address'] for i in result_list if i['description']['moniker'] == moniker][0]
        tokens_start = int((HttpResponse.get_validator_delegate(validator_addr=operator))['tokens'])
        unstake_data = dict(operator_address=operator, stake_or_unstake="stake", amount=amount)
        result = self.tx.Staking.validator_stake_unstake(**unstake_data)
        time.sleep(5)
        tokens_end = int((HttpResponse.get_validator_delegate(validator_addr=operator))['tokens'])

        assert tokens_end == tokens_start + Compute.to_u(amount)
        assert 1 == 1
        pass

    @pytest.mark.parametrize("stake_data", test_data)
    def test_vali_unstake(self, stake_data):
        """
        测试减少对应节点的stake值
        """
        moniker, amount = stake_data['moniker'], stake_data['amount']
        result_list = HttpResponse.get_validator_list()
        operator = [i['operator_address'] for i in result_list if i['description']['moniker'] == moniker][0]
        tokens_start = int((HttpResponse.get_validator_delegate(validator_addr=operator))['tokens'])
        unstake_data = dict(operator_address=operator, stake_or_unstake="unstake", amount=amount)
        result = self.tx.Staking.validator_stake_unstake(**unstake_data)
        time.sleep(5)
        tokens_end = int((HttpResponse.get_validator_delegate(validator_addr=operator))['tokens'])

        assert tokens_end == tokens_start - Compute.to_u(amount)
        assert 1 == 1
        pass

    @pytest.mark.parametrize("stake_data", test_data)
    def test_edit_validator(self, stake_data):
        """
        测试修改节点的归属人地址（售卖节点）
        """
        moniker = stake_data['moniker']
        username = stake_data['owner']
        # moniker = "node4"
        # username = "owner2"
        owner_addr = HttpResponse.q.Key.address_of_name(username=username)

        result_list = HttpResponse.get_validator_list()
        operator = [i['operator_address'] for i in result_list if i['description']['moniker'] == moniker][0]
        # 查询开始信息
        owner_start = HttpResponse.get_validator_delegate(validator_addr=operator)['owner_address']
        owner_data = dict(operator_address=operator, owner_address=owner_addr)
        # 修改归属人
        result = self.tx.Staking.edit_validator(**owner_data)
        time.sleep(5)
        # 查询信息看看有没有更改
        owner_end = HttpResponse.get_validator_delegate(validator_addr=operator)['owner_address']
        assert owner_end == owner_addr
        assert 1 == 1

        pass
    @pytest.mark.parametrize("stake_data", test_data)
    def test_edit_validator_pool(self,stake_data):
        """
        测试把节点的归属地址（售卖节点）卖给模块地址
        """
        # moniker = stake_data['moniker']
        # username = stake_data['owner']
        moniker = "node4"
        # username = "owner2"
        pool_name = "mint"
        pool_name = stake_data['pool_name']

        owner_addr = HttpResponse.q.Account.auth_account(pool_name=pool_name)
        result_list = HttpResponse.get_validator_list()
        operator = [i['operator_address'] for i in result_list if i['description']['moniker'] == moniker][0]
        # 查询开始信息
        owner_start = HttpResponse.get_validator_delegate(validator_addr=operator)['owner_address']
        logger.info(f"owner_start={owner_start}")

        owner_data = dict(operator_address=operator, owner_address=owner_addr)
        # 修改归属人
        result = self.tx.Staking.edit_validator(**owner_data)
        time.sleep(5)
        # 查询信息看看有没有更改
        owner_end = HttpResponse.get_validator_delegate(validator_addr=operator)['owner_address']
        logger.info(f"owner_end={owner_end}")
        assert owner_end == owner_addr
        assert 1 == 1
        result2=self.tx.Staking.new_kyc(region_id="gtm",user_addr="me1y4hf2w37ryxer2c2rekgyfp3q6wdjqna5t3wt5")
        time.sleep(5)
        http_result=HttpResponse.hq.tx.query_tx(tx_hash=result2['txhash'])
        logger.info(f"http_result={http_result}")
        assert "register kyc airdop failed" in str(http_result)

        pass
