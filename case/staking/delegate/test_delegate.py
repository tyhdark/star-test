# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestDelegate:
    tx = Tx()
    q = Query()

    @pytest.mark.parametrize("data", [dict(region_user_addr="sil1c0xgtqgxpm6ptxnawh3klfpgm4dprvjmxn0dqx")])
    def test_delegate(self, data):
        del_info = self.tx.staking.delegate(data["region_user_addr"], 10, 1)
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", [dict(region_user_addr="sil1c0xgtqgxpm6ptxnawh3klfpgm4dprvjmxn0dqx")])
    def test_undelegate(self, data):
        del_info = self.tx.staking.undelegate(data["region_user_addr"], 2, 1)
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data",
                             [dict(from_addr="sil1quqx4dqd3e7qsv9wnufnqdkgmuks5xxn8qzag8",
                                   delegator_address="sil1c0xgtqgxpm6ptxnawh3klfpgm4dprvjmxn0dqx")])
    def test_exit_delegate(self, data):
        del_info = self.tx.staking.exit_delegate(data["from_addr"], data["delegator_address"], 1)
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", [dict(addr="sil1c0xgtqgxpm6ptxnawh3klfpgm4dprvjmxn0dqx")])
    def test_withdraw(self, data):
        withdraw_info = self.tx.staking.withdraw(data["addr"], 1)
        logger.info(f"withdraw_info :{withdraw_info}")
        resp = self.q.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0

    @pytest.mark.parametrize("data", [dict(addr="sil1c0xgtqgxpm6ptxnawh3klfpgm4dprvjmxn0dqx")])
    def test_show_delegate(self, data):
        del_info = self.q.staking.show_delegate(data["addr"])
        logger.info(f"show_delegate :{del_info['delegation']}")

    def test_list_region(self):
        region_info = self.q.staking.list_region()
        logger.info(f"region_info :{region_info}")

    @pytest.mark.parametrize("data", [dict(region_id="bfdf8d44bc9211ed83a91e620a42e349")])
    def test_kyc_by_region(self, data):
        kyc_info = self.q.staking.kyc_by_region(data["region_id"])
        logger.info(f"kyc_info :{kyc_info}")

