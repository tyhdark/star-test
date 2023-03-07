# -*- coding: utf-8 -*-
"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/3/6 14:26
@Version :  V1.0
@Desc    :  None
"""
import pytest
from loguru import logger

from x.query import Query
from x.tx import Tx

logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P1
class TestBank:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", [dict(from_addr="sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh",
                                           to_addr="sil155mv39aqtl234twde44wrjdd5phxx28mg46u3p",
                                           amount="100", fees="1")])
    def test_send(self, data):
        # 新创建区 需要等待一个块高才能认证KYC，即区金库要有余额
        tx_info = self.tx.bank.send_tx(data["from_addr"], data["to_addr"], data["amount"], data["fees"], True)
        logger.info(f"Sent transaction:{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0

