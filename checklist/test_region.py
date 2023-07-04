# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    base_cfg = test_bank.tx
    # DefaultTotalStakeAllow 100000 * 400 = 40000000
    default_stake_allow_ac = Compute.as_to_ac(base_cfg.region_as)
    tx_charge = int(float(default_stake_allow_ac) * 0.0001)
    gas_limit = 200000 * (tx_charge + 10)
    fees = tx_charge + 10  # 本次tx多给10个代币,防止fees不足

    def test_update_region(self, setup_update_region_data):
        """测试修改区域信息"""
        logger.info("TestRegionInfo/test_update_region")

        for data in setup_update_region_data:
            logger.info(f"update_region_data: {data}")
            self.test_region.test_update_region(**data)

    # 水位异常场景测试
    # 1.水位和regionAS一致
    def test_stake_allow_eq_region_as(self, setup_create_region_and_kyc_user):
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user
        kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**kyc_data)
        user_addr2 = user_info['address']

        # update region
        data = dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=self.default_stake_allow_ac)
        self.test_region.test_update_region(**data)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
                         amount=self.default_stake_allow_ac + self.base_cfg.fees, gas=self.gas_limit, fees=self.fees)
        send_data2 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2,
                          amount=self.default_stake_allow_ac + self.base_cfg.fees, gas=self.gas_limit, fees=self.fees)
        self.test_bank.test_send(**send_data)
        self.test_bank.test_send(**send_data2)

        del_data = dict(from_addr=user_addr, amount=self.default_stake_allow_ac - 1)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_delegate(**del_data)
        assert "'code': 2018" in str(ex.value)  # ErrRegionTotalStakeAllow parameter error

    # 2.水位是regionAS 80%
    def test_stake_allow_eq_region_as_80(self, setup_create_region_and_kyc_user):
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        data = dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=self.default_stake_allow_ac)
        self.test_region.test_update_region(**data)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
                         amount=self.default_stake_allow_ac, gas=self.gas_limit, fees=self.fees)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=int(self.default_stake_allow_ac * 0.5))
        self.test_del.test_delegate(**del_data)

        # update stake_allow = region_as * 80%
        data = dict(region_id=region_id, from_addr=region_admin_addr,
                    totalStakeAllow=int(self.base_cfg.region_as * 0.8))
        self.test_region.test_update_region(**data)

        kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**kyc_data)
        user_addr2 = user_info['address']

        send_data2 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2,
                          amount=self.default_stake_allow_ac, gas=self.gas_limit, fees=self.fees)
        self.test_bank.test_send(**send_data2)

        del_data = dict(from_addr=user_addr2, amount=int(self.default_stake_allow_ac * 0.3))
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_delegate(**del_data)
        assert "'code': 2018" in str(ex.value)

        # 0.3+0.5-2(2个kyc) = 0.8
        del_data = dict(from_addr=user_addr2, amount=int(self.default_stake_allow_ac * 0.3) - 2)
        self.test_del.test_delegate(**del_data)

        # 达到水位之后 可以继续kyc 但是不能继续委托
        kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        _ = self.test_kyc.test_new_kyc_user(**kyc_data)

        del_data = dict(from_addr=user_addr2, amount=1)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_delegate(**del_data)
        assert "'code': 2018" in str(ex.value)
