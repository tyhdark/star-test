# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from config import test_data
from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestBank:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", test_data.Bank.tx_info)
    def test_send(self, data):
        # 新创建区 需要等待一个块高才能认证KYC，即区金库要有余额
        tx_info = self.tx.bank.send_tx(data["from_addr"], data["to_addr"], data["amount"], data["fees"], True)
        logger.info(f"Sent transaction:{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0
