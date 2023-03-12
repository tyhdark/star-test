# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from config import test_data
from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestFixed:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", test_data.Fixed.fixed_info)
    def test_fixed(self, data):
        tx_info = self.tx.staking.do_fixed_deposit(data["amount"], data["period"], data["from_addr"], data["fees"],
                                                   data["gas"])
        logger.info(f"do_fixed_deposit tx_info :{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", test_data.Fixed.fixed_withdraw_info)
    def test_fixed_withdraw(self, data):
        tx_info = self.tx.staking.do_fixed_withdraw(data["deposit_id"], data["from_addr"], data["fees"], data["gas"])
        logger.info(f"do_fixed_withdraw tx_info :{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0
