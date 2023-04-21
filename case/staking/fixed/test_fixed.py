# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestFixed:
    tx = Tx()
    q = Query()

    def test_create_fixed_deposit(self, data):
        tx_info = self.tx.staking.create_fixed_deposit(data["amount"], data["period"], data["from_addr"], data["fees"],
                                                       data["gas"])
        logger.info(f"do_fixed_deposit tx_info :{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0

    def test_withdraw_fixed_deposit(self, data):
        tx_info = self.tx.staking.withdraw_fixed_deposit(data["deposit_id"], data["from_addr"], data["fees"],
                                                         data["gas"])
        logger.info(f"do_fixed_withdraw tx_info :{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0
