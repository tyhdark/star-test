# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestBank:
    tx = Tx()
    q = Query()

    # @pytest.mark.parametrize("data", test_data.Bank.tx_info)
    def test_send(self, data):
        logger.info("TestBank/test_send")
        tx_info = self.tx.bank.send_tx(data["from_addr"], data["to_addr"], data["amount"], data["fees"], True)
        logger.info(f"Sent transaction:{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0
