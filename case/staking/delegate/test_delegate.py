# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from config import chain
from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestDelegate:
    tx = Tx()
    q = Query()

    def test_delegate(self, data):
        del_info = self.tx.staking.delegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    def test_withdraw(self, data):
        withdraw_info = self.tx.staking.withdraw(data["region_user_addr"], data["fees"])
        logger.info(f"withdraw_info :{withdraw_info}")
        resp = self.q.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0

    def test_undelegate(self, data):
        del_info = self.tx.staking.undelegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        time.sleep(1)
        assert resp['code'] == 0

    def test_exit_delegate(self, data):
        del_info = self.tx.staking.exit_delegate(data["from_addr"], data["delegator_address"], data["fees"])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", [dict(region_user_addr="gea1522w9wrvw47uwfzgfjp4q3c5s76s9ln8vdkwdj", amount=10,
                                           term=chain.delegate_term[1], fees=1)])
    def test_delegate_fixed(self, data):
        del_info = self.tx.staking.delegate_fixed(data["region_user_addr"], data["amount"], data["term"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", [dict(region_user_addr="gea1pkxkzrxzfvg9gkdzy8pxh5tjwqzhkj8ry6aw2u", amount=10,
                                           fees=1)])
    def test_delegate_infinite(self, data):
        del_info = self.tx.staking.delegate_infinite(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data",
                             [dict(from_addr="gea1ls3p7ygf4082uyma98aamkyqeft3r7pp2mmmvx", fixed_delegation_id=0,
                                   fees=1)])
    def test_undelegate_fixed(self, data):
        """提取定期内周期质押"""
        del_info = self.tx.staking.undelegate_fixed(data["from_addr"], data["fixed_delegation_id"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", [dict(region_user_addr="gea1d5vqzra2gtglz59sauq0u0whxrg8a9xy2gqwgr", amount=2,
                                           fees=1)])
    def test_undelegate_infinite(self, data):
        del_info = self.tx.staking.undelegate_infinite(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0
