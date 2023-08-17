# -*- coding: utf-8 -*-
# import inspect
# import time
#
import time

import pytest
import yaml
from loguru import logger
#
# from tools.name import UserInfo, RegionInfo, ValidatorInfo
from tools.compute import Compute
from tools.mint import Mint
from x.query import Query, HttpQuery
from x.tx import Tx

with open('test_send.yml', 'r') as file:
    test_data = yaml.safe_load(file)

import time


def outer(func):
    def inner(*args, **kwargs):
        print(1)
        func()
        print(2)

    return inner


class TestSend(object):
    def test_send(self):
        # 正常转账
        Tx.Bank.send_tx(from_addr="1", to_addr="1", amount=1)
        # 查询有没有到账
        # 查询有没有减少
        # 异常的
        pass

    @staticmethod
    def get_treasury(get_treasury_balances):
        treasury_balances = get_treasury_balances
        return treasury_balances
        # treasury_balances2 = get_treasury_balances
        # yield treasury_balances2

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_admin_success(self, test_send):
        """转账正确金额"""
        # 先查询管理员余额
        amount = "{:.10f}".format(test_send['success_amount'])
        logger.info(f"type={type(amount)}")
        start_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库余额
        treasury_addr = Query.Account.auth_account()
        treasury_start_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_start_balance={treasury_start_balance}")
        # 发起转账
        result = Tx.Bank.send_to_admin(amount=amount)
        # logger.info(f"logo:{result}")
        # 查询管理员余额
        end_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_end_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_end_balance={treasury_end_balance}")
        # 断言1 余额有没有变化
        assert result['code'] == test_send['code']
        assert end_balance == start_balance + Compute.to_u(float(amount)) - 100
        assert treasury_end_balance == treasury_start_balance - Compute.to_u(
            number=float(amount)) + 100 + Mint.calculate_treasury_reward()
        # 断言2 交易有没有成功
        # assert 1 == 1
        pass

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_admin_error_min(self, test_send):
        """转账错误金额"""
        # 先查询管理员余额
        amount = "{:.20f}".format(test_send['min_amount'])
        start_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库余额
        treasury_addr = Query.Account.auth_account()
        treasury_start_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_start_balance={treasury_start_balance}")
        # 发起转账
        result = Tx.Bank.send_to_admin(amount=amount)
        # logger.info(f"logo:{result}")
        # 查询管理员余额
        end_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_end_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_end_balance={treasury_end_balance}")
        # 断言1 余额有没有变化
        assert "Error" in result  # 断言1 报错
        assert end_balance == start_balance  # 断言：管理员余额没有变化
        assert treasury_end_balance == treasury_start_balance  # 断言，国库金额没有变化

    # @pytest.mark.parametrize("test_case", test_data)
    def test_send_to_admin_error_max(self):
        """转账错误金额"""
        # 先查询管理员余额
        amount = "1000000000000000"
        start_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库余额
        treasury_addr = Query.Account.auth_account()
        treasury_start_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_start_balance={treasury_start_balance}")
        # 发起转账
        result = Tx.Bank.send_to_admin(amount=amount)

        # logger.info(f"logo:{type(result)}")
        # 查询管理员余额
        end_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_end_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_end_balance={treasury_end_balance}")
        # 断言1 余额有没有变化
        assert "is smaller" in str(result)  # 断言1 报错
        assert end_balance == start_balance - 100  # 断言：管理员的交易上链了，仍然要付手续费，
        assert treasury_end_balance == treasury_start_balance + 100 + Mint.calculate_treasury_reward()  # 断言，国库金额没有变化

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_admin_error_from(self, test_send):
        other_name = test_send.get('test_name')

        other_addr = Query.Account.auth_account(pool_name=other_name)

        # 发起转账
        result = Tx.Bank.send_to_admin(amount=1, superadmin=other_addr)

        assert "Error" in result
        pass

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_treasury_success(self, test_send):
        amount = "{:.10f}".format(test_send['success_amount'])
        # 查询管理员开始余额
        admin_balance_start = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        logger.info(f"admin_balance_start={admin_balance_start}")
        # 查询国库开始余额
        treasury_addr = Query.Account.auth_account(pool_name="treasury_pool")
        treasury_balance_start = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_balance_start={treasury_balance_start}")
        # 往国库转钱的接口，三种情况，第一种正常场景，第二种小于1umec，第三种大于余额的情况，第四种剩下的钱够支付手续费但是支付手续费之后不够转的金额
        result = Tx.Bank.send_to_treasury(amount=amount)
        # logger.info(f"result={result}")
        # 查询管理员结束余额
        admin_balance_end = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库结束余额
        treasury_balance_end = HttpQuery.Bank.query_balances(addr=treasury_addr)
        # 判断交易是否成功上链
        assert 0 == result['code']
        # 判断管理员的钱有没有减少，
        assert admin_balance_end == admin_balance_start - Compute.to_u(number=float(amount)) - 100

        # 判断国库的钱有没有加
        assert treasury_balance_end == treasury_balance_start + Compute.to_u(
            number=float(amount)) + 100 + Mint.calculate_treasury_reward()
        pass

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_treasury_min(self, test_send):
        amount = "{:.20f}".format(test_send['min_amount'])
        # amount = "0.0000009"
        # 查询管理员开始余额
        admin_balance_start = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        logger.info(f"admin_balance_start={admin_balance_start}")
        # 查询国库开始余额
        treasury_addr = Query.Account.auth_account(pool_name="treasury_pool")
        treasury_balance_start = HttpQuery.Bank.query_balances(addr=treasury_addr)
        logger.info(f"treasury_balance_start={treasury_balance_start}")
        # 往国库转钱的接口，三种情况，第一种正常场景，第二种小于1umec，第三种大于余额的情况，第四种剩下的钱够支付手续费但是支付手续费之后不够转的金额
        result = Tx.Bank.send_to_treasury(amount=amount)
        # logger.info(f"result={result}")
        # 查询管理员结束余额
        admin_balance_end = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库结束余额
        treasury_balance_end = HttpQuery.Bank.query_balances(addr=treasury_addr)
        # 判断交易是否成功上链
        assert "Error" in result  # 断言1 报错
        assert admin_balance_end == admin_balance_start  # 断言：管理员余额没有变化
        assert treasury_balance_end == treasury_balance_start  # 断言，国库金额没有变化

    def test_send_to_treasury_max(self):
        amount = "100000000000000000"
        # 发起转账
        result = Tx.Bank.send_to_treasury(amount=amount)
        logger.info(f"result={result}")
        assert "is smaller than" in str(result)

        pass

    # @pytest.mark.xfail
    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_treasury_form(self, test_send):
        # 测试--from命令 其他人发起这个命令可以吗？
        # 先查国库开始金额
        other_name = test_send.get('test_name')
        # treasury_addr=HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_balance_start = HttpQuery.Bank.query_balances(
            addr=Query.Account.auth_account(pool_name="treasury_pool"))

        # 拿到其他人的地址
        other_addr = Query.Account.auth_account(pool_name=other_name)
        logger.info(f"other_addr={other_addr}")

        # 发起转账
        result = Tx.Bank.send_to_treasury(amount=1, super_addr=other_addr)

        # result=Tx.Bank.send_to_treasury(amount=1)
        # logger.info(f"result={result}")
        # 断言报错在不在里面
        # assert "key not found" in result
        # 查询国库金额有没有变化
        treasury_balance_end = HttpQuery.Bank.query_balances(
            addr=Query.Account.auth_account(pool_name="treasury_pool"))

    # @outer
    def test_to_treasury_form_test(self):
        # time.sleep(5)
        assert 1 == 1

        pass
