# -*- coding: utf-8 -*-
import random

import pytest
from loguru import logger

from config import chain
from tools import handle_query
from x.query import Query
from x.tx import Tx


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    tx = Tx()
    q = Query()
    handle_q = handle_query.HandleQuery()

    @pytest.mark.parametrize("data", chain.validator_data)
    def test_create_validator(self, data):
        tx_resp = self.tx.staking.create_validator(**data)
        logger.info(f"create_validator tx_resp: {tx_resp}")
        tx_resp = self.q.tx.query_tx(tx_resp['txhash'])
        assert tx_resp['code'] == 0

    def test_update_validator(self, setup_create_region):
        region_admin_addr, region_id, region_name, update_region_data = setup_create_region

        validator_list = self.handle_q.get_validator_list()['validator']
        num = 0
        while True:
            validator_info = random.choice(validator_list)
            num += 1
            if validator_info["RegionName"] == "Global":
                break
            if num > 5:
                raise RuntimeError('query validator_list not find valid RegionName')

        operator_address = validator_info["operator_address"]
        validator_data = dict(operator_address=operator_address, region_name=region_name,
                              from_addr=chain.super_addr, fees=1)
        tx_resp = self.tx.staking.update_validator(**validator_data)
        logger.info(f"update_validator tx_resp: {tx_resp}")
        tx_resp = self.q.tx.query_tx(tx_resp['txhash'])
        assert tx_resp['code'] == 0

    # TODO
    #  1.节点异常作弊场景
    #  2.各节点手续费收费标准不一致
