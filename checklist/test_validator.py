# -*- coding: utf-8 -*-
import random
import time

import pytest
from loguru import logger

from config.chain import config
from tools.parse_response import HttpResponse
from x.query import Query
from x.tx import Tx

# logger.add("logs/case_{time}.log", rotation="500MB")

validator_data = [
    dict(
        pubkey='\'{"type": "tendermint/PubKeyEd25519","value": "asficaxnM8TGS+v9snwnnxhJidFbJ3Sn1GXTAR7xslE="}\'',
        moniker="node16",
        from_addr=config['chain']['super_addr'],
    ),
]


@pytest.mark.P0
class TestRegionInfo:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", validator_data)
    def test_create_validator(self, data):
        tx_resp = self.tx.staking.create_validator(**data)
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

    # TODO
    #  1.节点异常作弊场景
    #  2.各节点手续费收费标准不一致
