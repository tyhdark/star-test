# -*- coding: utf-8 -*-
import inspect
import time

from loguru import logger

from cases import unitcases
from tools.parse_response import HttpResponse
from x.query import Query, HttpQuery
from x.tx import Tx
from tools.compute import Compute


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
        # 用户1给2转 50 费率=0 的时候 不成功 code:13
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2, amount=user_send_amount, fees=0)
        resp = self.tx.bank.send_tx(**send_data)
        assert 13 == resp['code']

        # 用户1给2转 50 费率<100 的时候 不成功 code:13
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2, amount=user_send_amount, fees=80)
        resp = self.tx.bank.send_tx(**send_data)
        assert 13 == resp['code']

        # 用户1给2转 50 费率是负数 的时候 不成功 code:13 参数报invalid
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2, amount=user_send_amount, fees=-10)
        resp = self.tx.bank.send_tx(**send_data)
        assert "invalid" in resp

        # 用户1给2转 50 费率不是数字类型 的时候 不成功 code:13 参数报invalid
        send_data = dict(from_addr=user_addr1, to_addr=user_addr2, amount=user_send_amount, fees="x")
        resp = self.tx.bank.send_tx(**send_data)
        assert "invalid" in resp

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

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=10, fees=50)
        resp = self.tx.staking.delegate(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=0)
        resp = self.tx.staking.delegate(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=-10)
        resp = self.tx.staking.delegate(**del_data)
        assert "invalid" in resp

        del_data = dict(from_addr=user_addr, amount=10, fees="xy")
        resp = self.tx.staking.delegate(**del_data)
        assert "invalid" in resp

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

        del_data = dict(from_addr=user_addr, amount=10, fees=50)
        resp = self.tx.staking.undelegate_nokyc(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=0)
        resp = self.tx.staking.undelegate_nokyc(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=-10)
        resp = self.tx.staking.undelegate_nokyc(**del_data)
        assert "invalid" in resp

        del_data = dict(from_addr=user_addr, amount=10, fees="xy")
        resp = self.tx.staking.undelegate_nokyc(**del_data)
        assert "invalid" in resp

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

        del_data = dict(from_addr=user_addr, amount=10, fees=50)
        resp = self.tx.staking.undelegate_kyc(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=0)
        resp = self.tx.staking.undelegate_kyc(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=-10)
        resp = self.tx.staking.undelegate_kyc(**del_data)
        assert "invalid" in resp

        del_data = dict(from_addr=user_addr, amount=10, fees="xy")
        resp = self.tx.staking.undelegate_kyc(**del_data)
        assert "invalid" in resp

        # 200的手续费  但前的余额 = 本来的钱-活期委托的10-手续费+赎回活期委托的10 -200的手续费
        del_data = dict(from_addr=user_addr, amount=10, fees=200)
        self.tx.staking.undelegate_kyc(**del_data)

        time.sleep(self.tx.sleep_time)

        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount)-self.base_cfg.fees-200+1

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

        deposit_data = dict(from_addr=user_addr, amount=10, fees=50)
        resp = self.tx.staking.deposit_fixed(**deposit_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=0)
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=-10)
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert "invalid" in resp

        del_data = dict(from_addr=user_addr, amount=10, fees="xy")
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert "invalid" in resp

        # 定期委托10  费率是200
        del_data = dict(from_addr=user_addr, amount=10, fees=200)
        self.tx.staking.deposit_fixed(**del_data)

        time.sleep(self.tx.sleep_time)

        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(100-10)-200

    def test_withdraw_fixed_fee(self):
        """
        验证定期提取下修改fees
        """
        logger.info("TestFee/test_withdraw_fixed_fee")
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员

        # 给用户发钱
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        deposit_data = dict(from_addr=user_addr, amount=10, fees=50)
        resp = self.tx.staking.deposit_fixed(**deposit_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=0)
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert 13 == resp['code']

        del_data = dict(from_addr=user_addr, amount=10, fees=-10)
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert "invalid" in resp

        del_data = dict(from_addr=user_addr, amount=10, fees="xy")
        resp = self.tx.staking.deposit_fixed(**del_data)
        assert "invalid" in resp
