# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute
from x.query import HttpQuery, Query
from x.tx import Tx


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    test_validator = unitcases.Validator()
    test_keys = unitcases.Keys()
    tx = Tx()
    hq = HttpQuery()
    q = Query()
    base_cfg = test_bank.tx
    # DefaultTotalStakeAllow 100000 * 400 = 40000000
    default_stake_allow_ac = Compute.as_to_ac(base_cfg.region_as)
    tx_charge = int(float(default_stake_allow_ac) * 0.0001)
    gas_limit = 200000 * (tx_charge + 10)
    fees = tx_charge + 10  # 本次tx多给10个代币,防止fees不足

    # def test_update_region(self, setup_update_region_data):
    #     """测试修改区域信息"""
    #     logger.info("TestRegionInfo/test_update_region")
    #
    #     for data in setup_update_region_data:
    #         logger.info(f"update_region_data: {data}")
    #         self.test_region.test_update_region(**data)

    # # 水位异常场景测试
    # # 1.水位和regionAS一致
    # def test_stake_allow_eq_region_as(self, setup_create_region_and_kyc_user):
    #     region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user
    #     kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**kyc_data)
    #     user_addr2 = user_info['address']
    #
    #     # update region
    #     data = dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=self.default_stake_allow_ac)
    #     self.test_region.test_update_region(**data)
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
    #                      amount=self.default_stake_allow_ac + self.base_cfg.fees, gas=self.gas_limit, fees=self.fees)
    #     send_data2 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2,
    #                       amount=self.default_stake_allow_ac + self.base_cfg.fees, gas=self.gas_limit, fees=self.fees)
    #     self.test_bank.test_send(**send_data)
    #     self.test_bank.test_send(**send_data2)
    #
    #     del_data = dict(from_addr=user_addr, amount=self.default_stake_allow_ac - 1)
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_delegate(**del_data)
    #     assert "'code': 2018" in str(ex.value)  # ErrRegionTotalStakeAllow parameter error

    # # 2.水位是regionAS 80%
    # def test_stake_allow_eq_region_as_80(self, setup_create_region_and_kyc_user):
    #     region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user
    #
    #     data = dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=self.default_stake_allow_ac)
    #     self.test_region.test_update_region(**data)
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
    #                      amount=self.default_stake_allow_ac, gas=self.gas_limit, fees=self.fees)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=int(self.default_stake_allow_ac * 0.5))
    #     self.test_del.test_delegate(**del_data)
    #
    #     # update stake_allow = region_as * 80%
    #     data = dict(region_id=region_id, from_addr=region_admin_addr,
    #                 totalStakeAllow=int(self.base_cfg.region_as * 0.8))
    #     self.test_region.test_update_region(**data)
    #
    #     kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**kyc_data)
    #     user_addr2 = user_info['address']
    #
    #     send_data2 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2,
    #                       amount=self.default_stake_allow_ac, gas=self.gas_limit, fees=self.fees)
    #     self.test_bank.test_send(**send_data2)
    #
    #     del_data = dict(from_addr=user_addr2, amount=int(self.default_stake_allow_ac * 0.3))
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_delegate(**del_data)
    #     assert "'code': 2018" in str(ex.value)
    #
    #     # 0.3+0.5-2(2个kyc) = 0.8
    #     del_data = dict(from_addr=user_addr2, amount=int(self.default_stake_allow_ac * 0.3) - 2)
    #     self.test_del.test_delegate(**del_data)
    #
    #     # 达到水位之后 可以继续kyc 但是不能继续委托
    #     kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     _ = self.test_kyc.test_new_kyc_user(**kyc_data)
    #
    #     del_data = dict(from_addr=user_addr2, amount=1)
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_delegate(**del_data)
    #     assert "'code': 2018" in str(ex.value)

    def test_region_max_delegate(self):
        """
        验证区的活期委托限制 可用委托余额= tokens - delegation_amount (umec)
        @Desc:
           - 前置条件是有node5 绑定的区，且区的 tokens值已经调整到比较小
           - user 在node5绑定的区做了kyc认证
           - user 进行活期委托 delegate_amount <= tokens - delegation_amount
           + expect: 委托成功

           - 前置条件是有node5 绑定的区，且区的 tokens值已经调整到比较小
           - user 在node5绑定的区做了kyc认证
           - user 进行活期委托 delegate_amount > tokens - delegation_amount
           + expect: 委托不成功 code = 52
        """
        logger.info("test_region/test_region_max_delegate")
        try:
            validator = self.test_validator.find_validator_by_node_name('node5')
        except Exception:
            pytest.skip("无法查询到node5对应的验证者节点，请确认node5是否已经创建对应的验证者节点")

        user_name = "tyh_node5_test1"
        # tyh_node5_test1 存在就不用再创建了
        if user_name is None:
            user_addr = self.test_keys.test_add(user_name)['address']
            send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr, amount=100)
            self.test_bank.test_send(**send_data)
            operator_address = validator['operator_address']
            region_id = self.test_region.get_region_id_by_operator_address(operator_address)

            logger.info(f"当前验证者节点的node={validator['description']['moniker']}")
            logger.info(f"当前验证者节点的tokens={validator['tokens']}")
            logger.info(f"当前验证者节点的kyc_amount={validator['kyc_amount']}")
            logger.info(f"当前验证者节点剩余的可kyc={int(validator['tokens']) - int(validator['kyc_amount'])}")
            logger.info(f"user_name={user_name}")
            kyc_data = dict(user_addr=user_addr, region_id=region_id)
            resp = self.tx.staking.new_kyc(**kyc_data)
            txhash = self.hq.tx.query_tx(resp['txhash'])
            code = txhash['code']
            assert code == 0
        else:
            user_addr = self.q.key.address_of_name(user_name)
            resp = self.q.staking.show_kyc(user_addr)
            if "NotFound" in resp:
                pytest.skip(f"{user_name},已创建，但是不是node5的kyc用户，请重新创建数据")

        max_delegate = int(validator['tokens']) - int(validator['delegation_amount'])
        logger.info(f"当前验证者节点剩余的可委托余额={max_delegate}")

        if max_delegate > Compute.to_u(1):
            # 委托小于验证者节点的最大可用委托金额
            delegate_data = dict(from_addr=user_addr, amount=Compute.to_u(max_delegate, True) - 1)
            resp = self.tx.staking.delegate(**delegate_data)
            txhash = self.hq.tx.query_tx(resp['txhash'])
            code = txhash['code']
            assert code == 0

            # 委托等于验证者节点最大可用金额的的金额
            validator = self.test_validator.find_validator_by_node_name('node5')
            max_delegate = int(validator['tokens']) - int(validator['delegation_amount'])
            logger.info(f"当前验证者节点剩余的可委托余额={max_delegate}")
            delegate_data = dict(from_addr=user_addr, amount=Compute.to_u(max_delegate, True))
            resp = self.tx.staking.delegate(**delegate_data)
            txhash = self.hq.tx.query_tx(resp['txhash'])
            code = txhash['code']

        # 委托大于验证者节点最大可用金额的的金额
        validator = self.test_validator.find_validator_by_node_name('node5')
        max_delegate = int(validator['tokens']) - int(validator['delegation_amount'])
        logger.info(f"当前验证者节点剩余的可委托余额={max_delegate}")
        delegate_data = dict(from_addr=user_addr, amount=Compute.to_u(max_delegate, True) + 1)
        resp = self.tx.staking.delegate(**delegate_data)
        txhash = self.hq.tx.query_tx(resp['txhash'])
        code = txhash['code']
        assert code == 52

        # 赎回，方便下次操作
        # 赎5的回活期委托
        un_del_amount = 3
        un_del_data = dict(from_addr=user_addr, amount=un_del_amount)
        resp = self.test_del.test_undelegate_kyc(**un_del_data)
        txhash = self.hq.tx.query_tx(resp['txhash'])
        code = txhash['code']
        assert code == 0

    def test_region_max_kyc(self):
        """
        验证区的kyc限制 可用KYC余额= tokens - kyc_amount   (umec)
        @Desc:
           - 前置条件是有node5 绑定的区，且区的 tokens值已经调整到比较小
           - user 新用户做kyc认证 区的id为node5绑定的区 tokens - kyc_amount =0
                or tokens - kyc_amount >0 or tokens - kyc_amount < 0
           + expect: 只有tokens - kyc_amount>=min_self_stake 的时候才能kyc成功，否则提示code=1150
        """
        user_name = 'tyh_add'
        user_addr = self.test_keys.test_add(user_name)['address']
        try:
            validator = self.test_validator.find_validator_by_node_name('node5')
        except Exception:
            pytest.skip("无法查询到node5对应的验证者节点，请确认node5是否已经创建对应的验证者节点")
        operator_address = validator['operator_address']
        region_id = self.test_region.get_region_id_by_operator_address(operator_address)
        kyc_data = dict(user_addr=user_addr, region_id=region_id)
        resp = self.tx.staking.new_kyc(**kyc_data)
        txhash = self.hq.tx.query_tx(resp['txhash'])
        code = txhash['code']
        if int(validator['tokens']) - int(validator['kyc_amount']) > 0:
            assert code == 0
        else:
            assert code == 1150
        self.tx.keys.delete(user_name)


