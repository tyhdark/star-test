# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from config import test_data
from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestDelegate:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", test_data.Delegate.region_user_list)
    def test_delegate(self, data):
        del_info = self.tx.staking.delegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", test_data.Delegate.region_user_list)
    def test_undelegate(self, data):
        del_info = self.tx.staking.undelegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        time.sleep(1)
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", test_data.Delegate.exit_delegate_list)
    def test_exit_delegate(self, data):
        del_info = self.tx.staking.exit_delegate(data["from_addr"], data["delegator_address"], data["fees"],
                                                 data['from_super'])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", test_data.Delegate.region_user_list)
    def test_withdraw(self, data):
        time.sleep(5)
        withdraw_info = self.tx.staking.withdraw(data["region_user_addr"], 1)
        logger.info(f"withdraw_info :{withdraw_info}")
        resp = self.q.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0
