# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestDelegate:
    tx = Tx()
    q = Query()

    # @pytest.mark.parametrize("data", test_data.Delegate.delegation_data)
    def test_delegate(self, data):
        del_info = self.tx.staking.delegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    # @pytest.mark.parametrize("data", test_data.Delegate.withdraw_data)
    def test_withdraw(self, data):
        time.sleep(5)
        withdraw_info = self.tx.staking.withdraw(data["region_user_addr"], data["fees"], data["gas"])
        logger.info(f"withdraw_info :{withdraw_info}")
        resp = self.q.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0

    # @pytest.mark.parametrize("data", test_data.Delegate.un_delegation_data)
    def test_undelegate(self, data):
        del_info = self.tx.staking.undelegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        time.sleep(1)
        assert resp['code'] == 0

    # @pytest.mark.parametrize("data", test_data.Delegate.exit_delegation_data)
    def test_exit_delegate(self, data):
        del_info = self.tx.staking.exit_delegate(data["from_addr"], data["delegator_address"], data["fees"],
                                                 data['from_super'])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0
