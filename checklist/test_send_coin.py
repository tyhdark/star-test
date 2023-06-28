# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute, WaitBlock
from tools.parse_response import HttpResponse


@pytest.mark.P0
class TestSendCoin(object):
    test_region = unitcases.Region()
    test_fixed = unitcases.Fixed()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    test_keys = unitcases.Keys()
    base_cfg = test_bank.tx

    def test_ag_to_ac(self, setup_create_region):
        logger.info("TestSendCoin/test_ag_to_ac")
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info['address']

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info['address']

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=500)
        self.test_bank.test_send(**send_data)

        region_info = HttpResponse.get_region(region_id)
        region_base_addr = region_info['region']['baseAccountAddr']
        base_uc_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['uc'])
        base_ug_balance = HttpResponse.get_balance_unit(region_base_addr, self.base_cfg.coin['ug'])
        logger.info(f"base_uc_balance: {base_uc_balance}, base_ug_balance: {base_ug_balance}")

        fixed_data = dict(amount=200, period=self.base_cfg.period[1], from_addr=user_addr)
        self.test_fixed.test_create_fixed_deposit(**fixed_data)

        # 验证用户余额
        user_balance_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
        assert int(user_balance_uc['amount']) == Compute.to_u(500 - 200 - self.base_cfg.fees)

        # 验证区金库信息
        region_fixed_addr = region_info['region']['fixedDepositAccountAddr']
        fixed_balance_uc = HttpResponse.get_balance_unit(region_fixed_addr, self.base_cfg.coin['uc'])
        assert int(fixed_balance_uc['amount']) == Compute.to_u(200)

        # 查用户定期信息
        user_fixed_info = HttpResponse.get_fixed_deposit_by_addr(user_addr, self.base_cfg.fixed_type['all'])
        fixed_list = user_fixed_info['FixedDeposit']
        fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
        _fixed_id = fixed_info['id']
        _fixed_end_height = fixed_info['end_height']
        user1_fixed_info = [i for i in fixed_list if i['account'] == user_addr][0]
        assert int(user1_fixed_info['amount']) == Compute.to_u(200)

        # 需要wait-block
        logger.info(f'{"到期赎回质押":*^50s}')
        WaitBlock.wait_block_for_height(height=_fixed_end_height)
        u_fees = Compute.to_u(self.base_cfg.fees)

        fixed_data = dict(deposit_id=_fixed_id, from_addr=user_addr)
        self.test_fixed.test_withdraw_fixed_deposit(**fixed_data)

        logger.info(f'{"返回质押本金+定期收益, 并且无定期质押":*^50s}')
        resp_user_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
        assert int(resp_user_uc['amount']) == int(fixed_balance_uc['amount']) + Compute.to_u(200) - u_fees
        resp_user_ug = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['ug'])
        # 计算定期收益 0.06 * 1 / 12 * (200 * 1000000) * 400 = 400000000ug  区金库:1100000000ug
        uac = Compute.to_u(Compute.interest(200, 1, self.base_cfg.annual_rate[1]))
        uag = Compute.ag_to_ac(number=uac, reverse=True)
        assert int(resp_user_ug['amount']) == uag

        # ag to ac
        ag = Compute.to_u(uag, reverse=True)
        ag_data = dict(ag_amount=ag, from_addr=user_addr)
        self.test_kyc.tx.Staking.ag_to_ac(**ag_data)

        # check balances
        to_uac = Compute.ag_to_ac(uag)
        resp2_user_uc = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
        assert int(resp2_user_uc['amount']) == int(resp_user_uc['amount']) - u_fees + to_uac

    def test_transfer(self, setup_create_region):
        logger.info("TestSendCoin/test_transfer")
        region_admin_addr, region_id, region_name, _ = setup_create_region

        user_addr = self.test_keys.test_add()

        region_admin_balance = HttpResponse.get_balance(region_admin_addr, self.base_cfg.coin['uc'])

        data = dict(from_addr=f"{region_admin_addr}", to_addr=f"{user_addr}", amount="10", fees="1")
        tx_info = self.test_bank.tx.bank.send_tx(**data)
        logger.info(f"Sent transaction:{tx_info}")
        resp = self.test_bank.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0

        region_admin_balance2 = HttpResponse.get_balance(region_admin_addr, self.base_cfg.coin['uc'])
        expect_data = int(region_admin_balance['amount']) - calculate.to_usrc(10) - (calculate.to_usrc(1) * 0.5)
        assert region_admin_balance2['amount'] == str(int(expect_data))

        user_balance2 = HttpResponse.get_balance(user_addr, self.base_cfg.coin['uc'])
        assert user_balance2['amount'] == str(calculate.to_usrc(10))

    def test_fee_rate(self):
        """测试交易手续费收取比例"""
        region_admin_addr, region_id, _ = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=f"{user_addr}", amount="500", fees="1")
        self.test_bank.test_send(send_data)

        start_region = HttpResponse.get_balance(region_admin_addr, self.base_cfg.coin['uc'])

        send_data = dict(from_addr=user_addr, to_addr=region_admin_addr, amount=100, fees=1)
        self.test_bank.test_send(send_data)

        end_region = HttpResponse.get_balance(region_admin_addr, self.base_cfg.coin['uc'])
        user_balance = HttpResponse.get_balance(user_addr, self.base_cfg.coin['uc'])

        assert int(end_region['amount']) - int(start_region['amount']) == calculate.to_usrc(1) / 2 + calculate.to_usrc(
            100)
        assert int(user_balance['amount']) == calculate.to_usrc(500 - 100 - 1)
