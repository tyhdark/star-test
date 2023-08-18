# -*- coding: utf-8 -*-
import inspect
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

with open('test_fee.yml', 'r') as file:
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
    base_cfg = test_bank.tx
    user_addr = None

    @pytest.fixture(scope='class')
    def setup_class_get_kyc_user_info(self):
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
        # 给用户发钱
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        self.user_addr = user_addr
        logger.info("TestFee/get_kyc_user_info----------------->创建一个kyc")

        yield user_addr

        # 删除用户
        self.test_key.test_delete_key(user_addr)
        logger.info("TestFee/get_kyc_user_info----------------->删除一个kyc")

    @pytest.fixture()
    def get_error_user_info(self):
        # 初始化数据 让 user1_tyh 满足异常测试的情况 既有余额、也有活期、定期委托
        logger.info("TestFee/get_kyc_info")
        user_name = "user1_tyh"
        user_addr = self.q.Key.address_of_name(username=user_name)
        region_id = "ita"
        if user_addr is None:
            # 创建用户
            user_info = unitcases.Keys().test_add(user_name)
            user_addr = user_info['address']
            # 管理员给用户转钱 100
            send_data = dict(from_addr=BaseClass.super_addr, to_addr=user_addr, amount=100)
            self.tx.bank.send_tx(**send_data)
            time.sleep(2)
            # 做kyc认证
            region_id_variable = RegionInfo.region_for_id_existing()
            kyc_data = dict(user_addr=user_addr, region_id=region_id_variable)
            resp = self.tx.staking.new_kyc(**kyc_data)
            time.sleep(2)
            assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
            # 定期委托10
            del_data = dict(from_addr=user_addr, amount=10, month=24)
            self.tx.staking.deposit_fixed(**del_data)
            yield user_addr, region_id
        else:
            yield user_addr, region_id

    @pytest.mark.parametrize("test_fee", test_data)
    def test_fee_error(self, test_fee, get_error_user_info):
        """验证各种场景下fees 传入错误、异常参数的情况"""
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

    def test_send_fee(self):
        """
        验证send下修改fees
        """
        logger.info("TestFee/test_send_fee")
        user_info1 = self.test_key.test_add()
        user_addr1 = user_info1['address']
        user_info2 = self.test_key.test_add()
        user_addr2 = user_info2['address']

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        # 管理员给用户转钱 100
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr1, amount=send_amount)
        self.test_bank.test_send(**send_data)

        user_send_amount = 50

        # 用户1给2转 50 费率=200 的时候
        test_fess = 200
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2, amount=user_send_amount, fees=test_fess)
        self.test_bank.test_send(**send_data)

        # 当前用户1余额是 转账后只减200的手续费
        user1_balance = HttpResponse.get_balance_unit(user_addr1)
        assert user1_balance == Compute.to_u(send_amount - user_send_amount) - test_fess

        # 当前用户2余额是 50
        user2_balance = HttpResponse.get_balance_unit(user_addr2)
        assert user2_balance == Compute.to_u(user_send_amount)

        # 转账手续费+转账金额>当前余额的情况 code = 1146 金额不足  'failed to execute message;
        # message index: 0: 0umec is smaller than 100000000umec: insufficient funds'
        test_fess = Compute.to_u(100)
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2, amount=10, fees=test_fess)
        resp = self.tx.bank.send_tx(**send_data)
        assert 1146 == resp['code']

        user1_balance = HttpResponse.get_balance_unit(user_addr1)
        # 转账手续费+转账金额=当前余额的情况
        test_fess = Compute.to_u(20)
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2,
                         amount=Compute.to_u(user1_balance - test_fess, reverse=True), fees=test_fess)
        self.test_bank.test_send(**send_data)

        user1_balance = HttpResponse.get_balance_unit(user_addr1)
        assert user1_balance == 0

        # 删除用户
        self.test_key.test_delete_key(user_addr1)
        self.test_key.test_delete_key(user_addr2)

    def test_delegate_fee(self):
        """
        验证delegate下修改fees
        """
        logger.info("TestFee/test_delegate_fee")
        user_info = self.test_key.test_add()
        user_addr = user_info['address']

        user1_info = self.test_key.test_add()
        user_addr1 = user1_info['address']

        user2_info = self.test_key.test_add()
        user2_addr = user2_info['address']

        # send to user
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        # send to user1
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr1, amount=send_amount)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr1, amount=10, fees=100.49)
        resp = self.tx.staking.delegate(**del_data)
        assert 0 == resp['code']

        time.sleep(self.tx.sleep_time)
        user_balance = HttpResponse.get_balance_unit(user_addr1)
        assert user_balance == Compute.to_u(send_amount - 10) - 100

        # send to user2
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user2_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user2_addr, amount=10, fees=100.99)
        resp = self.tx.staking.delegate(**del_data)
        assert 0 == resp['code']

        time.sleep(self.tx.sleep_time)
        user_balance = HttpResponse.get_balance_unit(user2_addr)
        assert user_balance == Compute.to_u(send_amount - 10) - 100

        # 手续费是200的时候能成功交易，手续费正常扣除200
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=200)
        self.test_del.test_delegate(**del_data)

        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - 200

        # 手续费是100.45 的时候能成功交易，手续费正常扣除100  为什么这里只扣了99？
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=100.55)
        self.test_del.test_delegate(**del_data)

        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount - delegate_amount) - 200 - 99

        # 委托手续费+委托金额>当前余额的情况
        test_fess = Compute.to_u(100)
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=test_fess)
        resp = self.tx.staking.delegate(**del_data)
        assert 1146 == resp['code']

        # 89999800
        user_balance = HttpResponse.get_balance_unit(user_addr)
        # 委托手续费+委托金额=当前余额的情况
        test_fess = Compute.to_u(5)
        # 89999800 - 5000000 = 84999800   这里delegate 84.9998mec 被取整数
        del_data = dict(from_addr=user_addr, amount=Compute.to_u(user_balance - test_fess, reverse=True),
                        fees=test_fess)
        self.test_del.test_delegate(**del_data)
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == 2

        # 删除用户
        self.test_key.test_delete_key(user_addr)
        self.test_key.test_delete_key(user_addr1)
        self.test_key.test_delete_key(user2_addr)

    def test_no_kyc_un_delegate_fee(self):
        """
        验证no_kyc_un_delegate下修改fees
        """
        logger.info("TestFee/test_no_kyc_un_delegate_fee")
        user_info = self.test_key.test_add()
        user_addr = user_info['address']

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        # 委托10
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=100)
        self.test_del.test_delegate(**del_data)

        # 当前活期委托数据应该等于委托数据
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

        # 赎回10 休眠一下免得查的金额是赎回之前的
        del_data = dict(from_addr=user_addr, amount=5)
        self.tx.staking.undelegate_nokyc(**del_data)

        time.sleep(self.tx.sleep_time)

        # 金额一致 100-10 -手续费*2 -1  手动计算结果要算上赎回时产生的收益1  因为是非kyc用户所以赎回的钱不会马上到帐
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - self.base_cfg.fees * 2 + 1

        # 赎回3 休眠一下免得查的金额是赎回之前的
        test_fees = 200
        del_data = dict(from_addr=user_addr, amount=3, fees=test_fees)
        self.tx.staking.undelegate_nokyc(**del_data)

        time.sleep(self.tx.sleep_time)

        # 金额一致 100-（10 -手续费）-10 - 200  手动计算结果要算上赎回时产生的收益1
        old_user_balance = user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - self.base_cfg.fees * 2 - test_fees + 1

        # 赎回 委托手续费=当前余额的情况
        test_fees = user_balance
        del_data = dict(from_addr=user_addr, amount=2, fees=test_fees)
        self.tx.staking.undelegate_nokyc(**del_data)

        time.sleep(self.tx.sleep_time)

        # 这个时候产生的收益已经被全部提取，用户余额已经全部被当手续费扣完
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == 0

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def test_kyc_un_delegate_fee(self):
        """
        验证kyc_un_delegate下修改fees
        """
        logger.info("TestFee/test_kyc_un_delegate_fee")
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        # 委托10
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount, fees=100)
        self.test_del.test_delegate(**del_data)

        # 200的手续费  但前的余额 = 本来的钱-活期委托的10-手续费+赎回活期委托的10 -200的手续费
        del_data = dict(from_addr=user_addr, amount=10, fees=200)
        self.tx.staking.undelegate_kyc(**del_data)

        time.sleep(self.tx.sleep_time)

        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount) - self.base_cfg.fees - 200 + 1

        # # 取回
        # del_data = dict(from_addr=user_addr, amount=10)
        # resp = self.tx.staking.undelegate_kyc(**del_data)

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def test_deposit_fixed_fee(self):
        """
        验证定期质押下修改fees
        """
        logger.info("TestFee/test_deposit_fixed_fee")
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        # 给用户发钱
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        # 定期委托10  费率是200
        del_data = dict(from_addr=user_addr, amount=10, fees=200)
        self.tx.staking.deposit_fixed(**del_data)

        time.sleep(self.tx.sleep_time)

        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(100 - 10) - 200

        time.sleep(self.tx.sleep_time)
        # 定期提取10  费率是200
        user_fixed_info_end = HttpResponse.get_fixed_deposit_by_addr_hq(addr=user_addr)
        myid = user_fixed_info_end[0]['id']
        withdraw = dict(from_addr=user_addr, fixed_delegation_id=myid, fees=200)
        resp = self.tx.staking.withdraw_fixed(**withdraw)
        time.sleep(self.tx.sleep_time)
        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0

        # 用户定期委托10 赎回10 有效的手续费都是200
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(100) - 400

    @pytest.mark.parametrize("deposit_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_withdraw_fixed_fee(self, setup_class_get_kyc_user_info, deposit_fees):
        """
        验证定期提取下修改fees
        """
        logger.info("TestFee/test_withdraw_fixed_fee")
        user_addr = setup_class_get_kyc_user_info

        before_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 定期委托10
        del_data = dict(from_addr=user_addr, amount=10, month=48)
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0

        # 定期提取10  费率是200

        user_fixed_info_end = HttpResponse.get_fixed_deposit_by_addr_hq(addr=user_addr)
        withdraw = dict(from_addr=user_addr, fixed_delegation_id=user_fixed_info_end[0]['id'], fees=deposit_fees)
        resp = self.tx.staking.withdraw_fixed(**withdraw)
        time.sleep(self.tx.sleep_time)

        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1144的code
        user_balance = HttpResponse.get_balance_unit(user_addr)
        if deposit_fees > user_balance:
            time.sleep(self.tx.sleep_time)
            assert resp['code'] == 1144
            return

        assert self.hq.tx.query_tx(resp['txhash'])['code'] == 0
        after_user_balance = HttpResponse.get_balance_unit(user_addr)
        # 手续费忽略小数  这个需要减去定期委托用掉的100手续费
        assert before_user_balance - self.base_cfg.fees - after_user_balance == int(deposit_fees)

    @pytest.mark.parametrize("kyc_fees", (Compute.to_u(990000000), 100, 100.0, 100.1, 100.49, 100.9, 200))
    def test_kyc_fee(self, kyc_fees):
        """
        验证kyc下修改fees
        """
        user_addr = self.test_key.test_add()['address']
        try:
            region_id_variable = RegionInfo.region_for_id_existing()
        except Exception as e:
            assert 0, "No region, please create region!"
        before_super_balance = HttpResponse.get_balance_unit(self.base_cfg.super_addr)
        kyc_data = dict(user_addr=user_addr, region_id=region_id_variable, fees=kyc_fees)
        resp = self.tx.staking.new_kyc(**kyc_data)

        # 如果传入的手续费数据大于管理员本金就判断交易无法成功且返回1146的code
        super_balance = HttpResponse.get_balance_unit(self.base_cfg.super_addr)
        if kyc_fees > super_balance:
            time.sleep(self.tx.sleep_time)
            assert resp['code'] == 1146
            return

        time.sleep(self.tx.sleep_time)
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
