# -*- coding: utf-8 -*-
import random
import time
from pathlib import Path

import httpx
import pytest
import yaml
from loguru import logger

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
