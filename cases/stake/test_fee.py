# -*- coding: utf-8 -*-
import inspect
import os
import sys
import time

import pytest
import yaml
from loguru import logger

from cases import unitcases
from tools.parse_response import HttpResponse
from x.query import Query, HttpQuery
from x.tx import Tx
from tools.compute import Compute
from tools.name import RegionInfo, ValidatorInfo
from x.base import BaseClass

# with open('./cases/stake/test_fee.yml', 'r') as file:
#     test_data = yaml.safe_load(file)
# with open('test_fee.yml', 'r') as file:
#     test_data = yaml.safe_load(file)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
current_path = os.path.dirname(__file__)
with open(current_path + '/test_fee.yml', 'r') as file:
    test_data = yaml.safe_load(file)


# 单元测试fee模块模块


class TestFee(object):
    tx = Tx()
    hq = HttpQuery()
    q = Query()
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_validator = unitcases.Validator()
    test_fixed = unitcases.Fixed()
    test_fees = unitcases.Fees()
    base_cfg = test_bank.tx
    user_addr = None
    user_no_kyc_addr = None
    is_first_success = False
    func_is_end = True

    @pytest.fixture(scope="class")
    def setup_class_get_kyc_user_info(self):
        """
        :return: user_addr, user_no_kyc_addr
        """

        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info
        self.user_addr = user_addr
        time.sleep(self.tx.sleep_time)

        user_no_kyc_info = self.test_key.test_add()
        user_no_kyc_addr = user_no_kyc_info['address']
        self.user_no_kyc_addr = user_no_kyc_addr
        time.sleep(self.tx.sleep_time)

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1) * 2)  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        time.sleep(self.tx.sleep_time)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_no_kyc_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        logger.info("TestFee/get_kyc_user_info----------------->创建数据")
        time.sleep(self.tx.sleep_time)

        yield user_addr, user_no_kyc_addr

        # 删除用户
        self.test_key.test_delete_key(user_addr)
        self.test_key.test_delete_key(user_no_kyc_addr)
        logger.info("TestFee/get_kyc_user_info----------------->删除数据")

    @pytest.fixture(scope="class")
    def get_error_user_info(self):
        # 初始化数据 让 user4_tyh 满足异常测试的情况 既有余额、也有活期、定期委托
        logger.info("TestFee/get_kyc_info")
        user_name = "user_tyh"
        user_addr = self.q.Key.address_of_name(username=user_name)
        region_id = "nic"
        if user_addr is None:
            # 创建用户
            user_info = unitcases.Keys().test_add(user_name)
            user_addr = user_info['address']
            # 管理员给用户转钱 100
            send_data = dict(from_addr=BaseClass.super_addr, to_addr=user_addr, amount=100)
            self.tx.bank.send_tx(**send_data)
            time.sleep(self.tx.sleep_time)
            # 做kyc认证
            region_id_variable = RegionInfo.region_for_id_existing()
            kyc_data = dict(user_addr=user_addr, region_id=region_id_variable)
            resp = self.tx.staking.new_kyc(**kyc_data)
            time.sleep(self.tx.sleep_time)
            assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
            # 定期委托10
            del_data = dict(from_addr=user_addr, amount=10, month=24)
            self.tx.staking.deposit_fixed(**del_data)
            time.sleep(self.tx.sleep_time)
            yield user_addr, region_id
        else:
            yield user_addr, region_id

    @pytest.mark.parametrize("test_fee", test_data)
    def test_fee_error(self, test_fee, get_error_user_info):
        """
        验证各种场景下fees 传入错误、异常参数的情况
        @Desc:
           - test_data 错误的参数
           - get_error_user_info 创建的有余额、有委托的用户
           + expect: 返回包含Error的命令行提示
        """
        user_addr, region_id = get_error_user_info

        amount = 10
        # 验证转账
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr,
                         amount=amount, fees=test_fee['error_data'])
        resp = self.tx.bank.send_tx(**send_data)
        assert_resp(resp, test_fee)

        # 验证活期委托
        del_data = dict(from_addr=user_addr, amount=amount, fees=test_fee['error_data'])
        resp = self.tx.staking.delegate(**del_data)
        assert_resp(resp, test_fee)

        # 验证活期赎回
        un_del_data = dict(from_addr=user_addr, amount=amount, fees=test_fee['error_data'])
        resp = self.tx.staking.undelegate_kyc(**un_del_data)
        assert_resp(resp, test_fee)

        # 验证定期委托
        dep_data = dict(from_addr=user_addr, amount=amount, fees=test_fee['error_data'])
        resp = self.tx.staking.deposit_fixed(**dep_data)
        assert_resp(resp, test_fee)

        # 验证定期提取
        user_fixed_info_end = HttpResponse.get_fixed_deposit_by_addr_hq(addr=user_addr)
        withdraw_data = dict(from_addr=user_addr, fixed_delegation_id=user_fixed_info_end[0]['id'],
                             fees=test_fee['error_data'])
        resp = self.tx.staking.withdraw_fixed(**withdraw_data)
        assert_resp(resp, test_fee)

        # 验证kyc
        kyc_data = dict(user_addr=user_addr, region_id=region_id,
                        fees=test_fee['error_data'])
        resp = self.tx.staking.new_kyc(**kyc_data)
        assert_resp(resp, test_fee)

    @pytest.mark.parametrize("send_fees", (9999999999999, 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_send_fee(self, setup_class_get_kyc_user_info, send_fees):
        """
        验证send下修改fees
        @Desc:
           - user_addr_balance 资金转出方 的余额
           - user_no_kyc_addr_balance 资金接受方 的余额
           - send_fees 手续费
           - user_send_amount 转出资金金额
           - send_fees <= user_addr_balance - user_send_amount
           + expect: 交易成功 能查到手续费被扣减，手续费被分成：节点拥有者拥有10%，pm拥有10%，国库80%

           - user_addr_balance 资金转出方 的余额
           - user_no_kyc_addr_balance 资金接受方 的余额
           - send_fees 手续费
           - user_send_amount 转出资金金额
           - send_fees > user_addr_balance - user_send_amount
           + expect: 交易不成功 提示 coed = 1144
        """
        logger.info("TestFee/test_send_fee")

        user_addr, user_no_kyc_addr = setup_class_get_kyc_user_info

        before_user_balance = HttpResponse.get_balance_unit(user_addr)
        before_user_no_kyc_balance = HttpResponse.get_balance_unit(user_no_kyc_addr)
        before_pm_balance = HttpResponse.get_balance_unit(self.q.key.address_of_name('PM'))

        user_send_amount = 2
        send_data = dict(from_addr=user_addr, to_addr=user_no_kyc_addr, amount=user_send_amount, fees=send_fees)
        resp = self.tx.bank.send_tx(**send_data)
        time.sleep(self.tx.sleep_time)

        # 如果传入的手续费数据大于 余额减去交易金额后的值 交易无法成功且返回1144的code
        if send_fees > before_user_balance - user_send_amount:
            time.sleep(self.tx.sleep_time)
            assert resp['code'] == 1144
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        after_user_no_kyc_balance = HttpResponse.get_balance_unit(user_no_kyc_addr)
        # 手续费忽略小数
        assert before_user_balance - Compute.to_u(user_send_amount) - after_user_balance == int(send_fees)
        assert after_user_no_kyc_balance - Compute.to_u(user_send_amount) == before_user_no_kyc_balance
        after_pm_balance = HttpResponse.get_balance_unit(self.q.key.address_of_name('PM'))
        if self.test_fees.user_in_validator_owner_is_pm(user_addr):
            # 如果验证者节点的所有者是pm，pm获得手续费的20%
            assert after_pm_balance - before_pm_balance == self.base_cfg.fees * 0.2
        else:
            # 如果验证者节点的所有者不是pm，pm只获得手续费的10%
            assert after_pm_balance - before_pm_balance == self.base_cfg.fees * 0.1

    def test_node_update_rate_send_fees(self):
        """
        验证修改node minimum-gas-prices = "0.001umec"  这个值* 200000 = 200 这里最低手续费就是 200umec
        提示交易失败：insufficient fees; got: 100umec required: 200umec: insufficient fee
        """
        user_adr = self.q.key.address_of_name("user_tyh")
        before_user_balance = HttpResponse.get_balance_unit(user_adr)
        other_adr = self.q.key.address_of_name("user1_tyh")
        # 前置条件是把node7的gas费率调整成 0.001umec, 且 user_tyh 这个用户是node7的kyc用户
        send_data = dict(from_addr=user_adr, to_addr=other_adr, amount=2, fees=100, node_ip='localhost:14007')
        resp = self.tx.bank.send_tx(**send_data)
        logger.info(f"resp={resp}")
        assert resp['code'] == 13

    # @pytest.mark.parametrize("send_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    @pytest.mark.parametrize("send_fees", (Compute.to_u(990000000), 100.49, 100.9, 200))
    def test_kyc_delegate_fee(self, setup_class_get_kyc_user_info, send_fees):
        """
        验证delegate下修改fees
        """
        logger.info("TestFee/test_kyc_delegate_fee")

        user_addr, _ = setup_class_get_kyc_user_info
        before_user_balance = HttpResponse.get_balance_unit(user_addr)
        before_pm_balance = HttpResponse.get_balance_unit(self.q.key.address_of_name('PM'))

        user_delegate_amount = 2
        send_data = dict(from_addr=user_addr, amount=user_delegate_amount, fees=send_fees)
        kyc_resp = self.tx.staking.delegate(**send_data)
        time.sleep(self.tx.sleep_time)

        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1144的code
        if send_fees > before_user_balance - user_delegate_amount:
            time.sleep(self.tx.sleep_time)
            assert kyc_resp['code'] == 1144
            return

        assert self.hq.tx.query_tx(kyc_resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        after_user_delegate = HttpResponse.get_delegate(user_addr)['amount']

        # # after_user_no_kyc_balance = HttpResponse.get_balance_unit(user_no_kyc_addr)
        # 手续费忽略小数
        assert before_user_balance - Compute.to_u(user_delegate_amount) - after_user_balance == int(send_fees)
        # 断言当前存在的活期委托金额与操作活期委托的金额是一致的
        assert int(after_user_delegate) == Compute.to_u(user_delegate_amount)
        after_pm_balance = HttpResponse.get_balance_unit(self.q.key.address_of_name('PM'))
        if self.test_fees.user_in_validator_owner_is_pm(user_addr):
            # 如果验证者节点的所有者是pm，pm获得手续费的20%
            assert after_pm_balance - before_pm_balance == self.base_cfg.fees * 0.2
        else:
            # 如果验证者节点的所有者不是pm，pm只获得手续费的10%
            assert after_pm_balance - before_pm_balance == self.base_cfg.fees * 0.1

        # 赎回委托，避免数据污染
        un_del_data = dict(from_addr=user_addr, amount=user_delegate_amount)
        resp = self.tx.staking.undelegate_kyc(**un_del_data)
        time.sleep(self.tx.sleep_time)
        # 断言赎回成功
        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0

    # @pytest.mark.parametrize("send_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    @pytest.mark.parametrize("send_fees", (Compute.to_u(990000000), 100.49, 100.9))
    def test_un_kyc_delegate_fee(self, setup_class_get_kyc_user_info, send_fees):
        """
        验证delegate下修改fees
        """
        logger.info("TestFee/test_un_kyc_delegate_fee")

        _, user_addr = setup_class_get_kyc_user_info
        before_user_balance = HttpResponse.get_balance_unit(user_addr)

        user_delegate_amount = 2
        send_data = dict(from_addr=user_addr, amount=user_delegate_amount, fees=send_fees)
        resp = self.tx.staking.delegate(**send_data)
        time.sleep(self.tx.sleep_time)

        # 如果传入的手续费数据大于余额就判断交易无法成功且返回1146的code      为什么这里是1146？
        if send_fees > before_user_balance - user_delegate_amount:
            time.sleep(self.tx.sleep_time)
            assert resp['code'] == 1146
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        after_user_delegate = HttpResponse.get_delegate(user_addr)['unKycAmount']
        # # after_user_no_kyc_balance = HttpResponse.get_balance_unit(user_no_kyc_addr)
        # 手续费忽略小数

        assert before_user_balance - Compute.to_u(user_delegate_amount) - after_user_balance == int(send_fees)
        # 断言当前存在的活期委托金额与操作活期委托的金额是一致的
        assert int(after_user_delegate) == Compute.to_u(user_delegate_amount)

        # 赎回委托，避免数据污染
        un_del_data = dict(from_addr=user_addr, amount=user_delegate_amount)
        resp = self.tx.staking.undelegate_nokyc(**un_del_data)
        time.sleep(self.tx.sleep_time)
        # 断言赎回成功
        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        # assert after_user_no_kyc_balance - Compute.to_u(user_send_amount) == before_user_no_kyc_balance

    @pytest.mark.parametrize("un_delegate_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_no_kyc_un_delegate_fee(self, setup_class_get_kyc_user_info, un_delegate_fees):
        """
        验证no_kyc_un_delegate下修改fees
        """
        logger.info("TestFee/test_no_kyc_un_delegate_fee")

        _, user_addr = setup_class_get_kyc_user_info
        before_user_balance = HttpResponse.get_balance_unit(user_addr)

        # 委托1
        delegate_amount = 1
        del_data = dict(from_addr=user_addr, amount=delegate_amount)
        self.test_del.test_delegate(**del_data)

        time.sleep(self.tx.sleep_time)

        # 赎回1
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=un_delegate_fees)
        resp = self.tx.staking.undelegate_nokyc(**del_data)
        time.sleep(self.tx.sleep_time)

        # 如果传入的手续费数据大于余额就判断交易无法成功且返回1146的code      为什么这里是1146？
        user_balance = HttpResponse.get_balance_unit(user_addr)
        if un_delegate_fees > user_balance:
            time.sleep(self.tx.sleep_time)
            assert resp['code'] == 1146
            return

        resp_code = self.hq.tx.query_tx(resp['txhash'])['code']
        if resp_code == 27:
            pytest.skip("非Kyc用户只能赎回7次")

        assert resp_code == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)

        # 断言 交易之前的余额 - 委托金额1me - 默认手续费 - 赎回交易之后的余额 = 赎回交易的费用
        assert before_user_balance - Compute.to_u(delegate_amount) - self.base_cfg.fees - after_user_balance == int(
            un_delegate_fees)

    @pytest.mark.parametrize("un_delegate_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_kyc_un_delegate_fee(self, setup_class_get_kyc_user_info, un_delegate_fees):
        """
        验证kyc_un_delegate下修改fees
        """
        logger.info("TestFee/test_kyc_un_delegate_fee")

        user_addr, _ = setup_class_get_kyc_user_info
        before_user_balance = HttpResponse.get_balance_unit(user_addr)

        # 委托2
        delegate_amount = 1
        del_data = dict(from_addr=user_addr, amount=delegate_amount)
        self.test_del.test_delegate(**del_data)

        time.sleep(self.tx.sleep_time)

        # 赎回2
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=un_delegate_fees)
        resp = self.tx.staking.undelegate_kyc(**del_data)
        time.sleep(self.tx.sleep_time)
        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1144的code
        user_balance = HttpResponse.get_balance_unit(user_addr)
        if un_delegate_fees > user_balance:
            assert resp['code'] == 1144
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 断言手续费是否为最初的余额-掉定期委托的金额-使用的手续费 - 活期委托用掉的默认手续费
        # 这里+1是因为会产生一个1u的收益，但这个收益是不满1u的时候被预先给的，如果后续产生的收益0.0几没有补上成为1,后续只会产生0 ?有问题！

        # if self.is_first_success:
        #     income_amount = 0
        # else:
        #     income_amount = 1
        #     self.is_first_success = True
        # income_amount = 0
        #
        # assert before_user_balance - self.base_cfg.fees - after_user_balance + income_amount == int(un_delegate_fees)

    @pytest.mark.parametrize("deposit_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_deposit_fixed_fee(self, setup_class_get_kyc_user_info, deposit_fees):
        """
        验证定期质押下修改fees
        """
        logger.info("TestFee/test_deposit_fixed_fee")

        user_addr, _ = setup_class_get_kyc_user_info

        before_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 定期委托10
        del_data = dict(from_addr=user_addr, amount=2, month=48, fees=deposit_fees)
        resp = self.tx.staking.deposit_fixed(**del_data)
        time.sleep(self.tx.sleep_time)
        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1144的code
        user_balance = HttpResponse.get_balance_unit(user_addr)
        if deposit_fees > user_balance:
            assert resp['code'] == 1144
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 断言手续费是否为最初的余额-掉定期委托的金额-使用的手续费
        assert before_user_balance - after_user_balance - Compute.to_u(2) == int(deposit_fees)

        time.sleep(self.tx.sleep_time)

        # 委托的定期要赎回，避免污染数据
        user_fixed_info_end = HttpResponse.get_fixed_deposit_by_addr_hq(addr=user_addr)
        withdraw = dict(from_addr=user_addr, fixed_delegation_id=user_fixed_info_end[0]['id'])
        resp = self.tx.staking.withdraw_fixed(**withdraw)
        time.sleep(self.tx.sleep_time)
        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0

    @pytest.mark.parametrize("deposit_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_withdraw_fixed_fee(self, setup_class_get_kyc_user_info, deposit_fees):
        """
        验证定期提取下修改fees
        """
        logger.info("TestFee/test_withdraw_fixed_fee")
        user_addr, _ = setup_class_get_kyc_user_info

        before_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 定期委托10
        del_data = dict(from_addr=user_addr, amount=2, month=48)
        resp = self.tx.staking.deposit_fixed(**del_data)
        time.sleep(self.tx.sleep_time)
        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0

        user_fixed_info_end = HttpResponse.get_fixed_deposit_by_addr_hq(addr=user_addr)
        withdraw = dict(from_addr=user_addr, fixed_delegation_id=user_fixed_info_end[0]['id'], fees=deposit_fees)
        resp = self.tx.staking.withdraw_fixed(**withdraw)
        time.sleep(self.tx.sleep_time)

        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1144的code
        user_balance = HttpResponse.get_balance_unit(user_addr)
        if deposit_fees > user_balance:
            assert resp['code'] == 1144
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 手续费忽略小数  这个需要减去定期委托用掉的100手续费
        assert before_user_balance - self.base_cfg.fees - after_user_balance == int(deposit_fees)

    @pytest.mark.parametrize("create_region_fees", (Compute.to_u(9999999999999), 100.0, 100.1, 100.49, 100.9, 200))
    def test_create_region_fee(self, create_region_fees):
        """
        验证创建区的费用
        """
        if len(ValidatorInfo.validator_bind_node_for_region(bind=False)) == 0:
            pytest.skip("所有验证者都已被绑定")

        # 没绑定的验证者创建区
        region_name = RegionInfo.region_name_for_create()
        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        res = self.tx.staking.create_region(region_name,
                                            node_name=node_name_var, fees=create_region_fees)
        time.sleep(self.tx.sleep_time)
        after_sup_balance = HttpResponse.get_balance_unit(self.tx.super_addr)
        if create_region_fees > after_sup_balance:
            assert res['code'] == 1146
            return
        tx_resp = self.hq.tx.query_tx(res['txhash'])
        # 断言创建区成功
        assert tx_resp['code'] == 0, f"test_create_region failed, resp: {tx_resp}"

        # 根据区id查到这个区的信息
        region_id = region_name.lower()
        rep = self.q.staking.show_region(region_id)
        # 断言能查到这个区已被创建
        assert region_id == rep['region']['regionId']

    @pytest.mark.parametrize("kyc_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_kyc_fee(self, kyc_fees):
        """
        验证kyc下修改fees
        """
        user_addr = self.test_key.test_add()['address']
        try:
            variable_region_id = RegionInfo.region_for_id_existing()
        except Exception as e:
            pytest.skip("目前没有区可以使用，请先创建区")
        before_super_balance = HttpResponse.get_balance_unit(self.base_cfg.super_addr)
        kyc_data = dict(user_addr=user_addr, region_id=variable_region_id, fees=kyc_fees)
        resp = self.tx.staking.new_kyc(**kyc_data)
        time.sleep(self.tx.sleep_time)
        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1146的code
        super_balance = HttpResponse.get_balance_unit(self.base_cfg.super_addr)
        if kyc_fees > super_balance:
            assert resp['code'] == 1146
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_super_balance = HttpResponse.get_balance_unit(self.base_cfg.super_addr)
        # 手续费忽略小数
        assert before_super_balance - after_super_balance == int(kyc_fees)

        # 删除用户
        self.test_key.test_delete_key(user_addr)


def assert_resp(resp, test_fee):
    """
    判断返回的结果
    :param resp: 命令发出后的返回结果
    :param test_fee: yal 里的测试数据
    :return:
    """
    if isinstance(resp, dict):
        assert test_fee['error_return'] == resp['code']
    else:
        assert test_fee['error_return'] in resp
