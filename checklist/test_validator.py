# -*- coding: utf-8 -*-
import random
import time
from pathlib import Path

import httpx
import pytest
import yaml
from loguru import logger

from cases import unitcases
from tools.compute import Compute, WaitBlock
from tools.parse_response import HttpResponse
from x.query import Query
from x.tx import Tx

# logger.add("logs/case_{time}.log", rotation="500MB")
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data/data.yml"


def read_file(filepath):
    filepath = Path(filepath)
    with filepath.open("r") as f:
        content = f.read()
    data = yaml.safe_load(content)
    return data


validator_data = read_file(DATA_FILE)


# TODO
#  1.节点异常作弊场景
#  2.各节点手续费收费标准不一致

@pytest.mark.P1
class TestValidator:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", validator_data)
    def test_create_validator(self, data):
        if not data["moniker"] == "node1":
            pub_key = f'\'{{"type": "tendermint/PubKeyEd25519", "value": "{data["pub_key"]["value"]}"}}\''
            # pub_key='\'{"type": "tendermint/PubKeyEd25519","value": "asficaxnM8TGS+v9snwnnxhJidFbJ3Sn1GXTAR7xslE="}\'',
            data["from_addr"] = self.tx.super_addr
            tx_resp = self.tx.staking.create_validator(pub_key=pub_key, moniker=data["moniker"],
                                                       from_addr=data["from_addr"])
            logger.info(f"create_validator tx_resp: {tx_resp}")
            time.sleep(self.tx.sleep_time)
            tx_resp = self.q.tx.query_tx(tx_resp['txhash'])
            assert tx_resp['code'] == 0

    def test_update_validator(self, setup_create_region):
        region_admin_info, region_id, region_name = setup_create_region

        validator_list = HttpResponse.get_validator_list()
        while True:
            Global_list = [i for i in validator_list if i["RegionName"] == "Global"]
            if Global_list:
                validator_info = random.choice(Global_list)
                break
            else:
                raise RuntimeError('query validator_list not find valid RegionName')

        operator_address = validator_info["operator_address"]
        val_data = dict(operator_address=operator_address, region_name=region_name, from_addr=self.tx.super_addr)
        tx_resp = self.tx.staking.update_validator(**val_data)
        logger.info(f"update_validator tx_resp: {tx_resp}")
        time.sleep(self.tx.sleep_time)
        tx_resp = self.q.tx.query_tx(tx_resp['txhash'])
        assert tx_resp['code'] == 0

    def test_batch_new_validator(self):
        cmd_list = []
        # 先处理validator_data数据
        for data in validator_data:
            if not data["moniker"] == "node1":
                pub_key = f'\'{{"@type": "/cosmos.crypto.ed25519.PubKey", "key": "{data["pub_key"]["value"]}"}}\''
                data["from_addr"] = self.tx.super_addr
                cmd = self.tx.staking.new_validator_cmd(pub_key=pub_key, moniker=data["moniker"],
                                                        from_addr=data["from_addr"])
                cmd_list.append(cmd)

    def test_batch_new_validator(self):
        cmd_list = []
        # 先处理validator_data数据
        for data in validator_data:
            if not data["moniker"] == "node1":
                pub_key = f'\'{{"type": "tendermint/PubKeyEd25519", "value": "{data["pub_key"]["value"]}"}}\''
                data["from_addr"] = self.tx.super_addr
                cmd = self.tx.staking.new_validator_cmd(pub_key=pub_key, moniker=data["moniker"],
                                                        from_addr=data["from_addr"])
                cmd_list.append(cmd)

        # 获取发送账户的sequence
        address = self.tx.super_addr
        url = f"{self.tx.api_url}/cosmos/auth/v1beta1/accounts/{address}"
        sequence = httpx.get(url).json()["account"]["sequence"]
        # 为cmd_list 中的每个元素都加上 -s=sequence
        # 下标0 -s=sequence 下标1 -s=sequence+1
        for i in range(len(cmd_list)):
            cmd_list[i] = cmd_list[i] + f" -s={int(sequence) + i}"

        result = [self.tx.ssh_client.ssh(cmd) for cmd in cmd_list]
        logger.info(f"batch_new_validator result: {result}")
        pass
        # 获取发送账户的sequence
        address = self.tx.super_addr
        url = f"{self.tx.api_url}/cosmos/auth/v1beta1/accounts/{address}"
        sequence = httpx.get(url).json()["account"]["sequence"]
        # 为cmd_list 中的每个元素都加上 -s=sequence
        # 下标0 -s=sequence 下标1 -s=sequence+1
        for i in range(len(cmd_list)):
            cmd_list[i] = cmd_list[i] + f" -s={int(sequence) + i}"

        result = [self.tx.ssh_client.ssh(cmd) for cmd in cmd_list]
        logger.info(f"batch_new_validator result: {result}")
        pass

    # TODO
    #  1.节点异常作弊场景
    #  2.各节点手续费收费标准不一致


class TestVali(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    base_cfg = test_bank.tx
    tx = Tx()
    q = Query()

    def test_more_owner(self):
        """
        一个人拥有多个节点
        """
        # 创建用户接收节点
        # 第一个节点售卖
        # 第二个节点售卖
        # 节点内发生交易，
        # 测试手续费走向
        pass

    def test_low_kyc(self):
        """
        将节点的tokens值降到目前现有kyc的人数以下。
        """
        # 查看节点kyc人数
        operator_addr = "mevaloper1hwr5wg9j8jcqxap0zrwgw4rwau84c6slmwpdk3"
        vail_info = HttpResponse.get_validator_delegate(
            validator_addr=operator_addr)
        logger.info(f"vail_info={vail_info}")
        tokens, kyc_amount = int(vail_info['tokens']), int(vail_info['kyc_amount'])
        # kyc_amount = 42
        # amount = Compute.to_u((tokens - kyc_amount)+Compute.to_u(100),reverse=True)
        # 999998000000-42000000=999956000000
        amount = 36

        # 减少tokens
        unstake_data = dict(operator_address=operator_addr, stake_or_unstake="unstake", amount=amount)
        result = self.tx.Staking.validator_stake_unstake(**unstake_data)
        logger.info(f"result={result}")
        # 断言报错
        http_result = HttpResponse.get_tx_hash(tx_hash=result['txhash'])
        logger.info(f"http_result={result}")
        # assert "error" in http_result
        assert 1 == 1
        pass
        #

    def test_kyc_test(self):
        """
        修改节点的tokens值，然后new_kyc不成功，然后提高节点的tokens，new kyc成功
        """
        # 查看节点的tokens人数
        operator_addr = "mevaloper1hwr5wg9j8jcqxap0zrwgw4rwau84c6slmwpdk3"
        vail_info = HttpResponse.get_validator_delegate(validator_addr=operator_addr)
        logger.info(f"vail_info={vail_info}")
        tokens, kyc_amount = int(vail_info['tokens']), int(vail_info['kyc_amount'])
        amount = Compute.to_u((tokens - kyc_amount), reverse=True)
        # 修改节点的tokens刚好等于现在kyc人数。
        unstake_data = dict(operator_address=operator_addr, stake_or_unstake="unstake", amount=amount)
        result = self.tx.Staking.validator_stake_unstake(**unstake_data)
        logger.info(f"result={result}")
        region_list = HttpResponse.get_regin_list()

        region_id = [region['regionId'] for region in region_list['region'] if region['operator_address'] == operator_addr][0]

        # new kyc 应该是不成功的
        #  创建一个用户，然后拿用户地址去kyc
        kyc_addr=(self.test_key.test_add(user_name="test_kyc_001"))['address']

        # kyc_result = self.test_kyc.test_new_kyc_user(region_id=region_id) 'failed to execute message; message index: 0: too many unbonding stake entries
        #   for (staker, validator) tuple'
        kyc_result = self.tx.Staking.new_kyc(region_id=region_id,user_addr=kyc_addr)

        HttpResponse.get_tx_hash(tx_hash=kyc_result['txhash'])

        assert 1 == 1
        # 提高节点的tokens，
        # stake_data = dict(operator_address=operator_addr, stake_or_unstake="stake", amount=amount)
        # result = self.tx.Staking.validator_stake_unstake(**unstake_data)
        # 再new kyc
        # self.test_kyc.test_new_kyc_user(region_id=region_id)

        # 应该是成功的
        pass


def test_delegate(self, creat_one_kyc):
    """
    修改节点的tokens值，然后委托超出tokens值的金额，，然后再增加tokens值，再发起对应的委托

    """
    user_addr, amount = creat_one_kyc
    pass
