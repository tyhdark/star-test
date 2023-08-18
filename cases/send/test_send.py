# -*- coding: utf-8 -*-

import os
import sys
import time

import pytest
import yaml
from loguru import logger

from tools.compute import Compute
from tools.mint import Mint
from x.query import Query, HttpQuery
from x.tx import Tx

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
current_path = os.path.dirname(__file__)
with open(current_path + '/test_send.yml', 'r', encoding='gbk') as file:
    test_data = yaml.safe_load(file)
with open(current_path + '/pool_name.yml', 'r', encoding='gbk') as file_pool:
    pool_name = yaml.safe_load(file_pool)


def treasury_balances():
    treasury_addr = Query.Account.auth_account()
    treasury_start_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
    return treasury_start_balance


class TestSend(object):

    # @staticmethod
    # def treasury_balances():
    #     treasury_addr = Query.Account.auth_account(pool_name="treasury_pool")
    #     treasury_start_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
    #     return treasury_start_balance

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_admin_success(self, test_send):
        """测试sendToAmin命令，输入正确的转账正确金额，"""

        amount = "{:.10f}".format(test_send['success_amount'])  # 转账金额

        admin_start_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)  # 先查询管理员余额

        treasury_addr = Query.Account.auth_account()  # 查询国库余额
        treasury_start_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)

        result = Tx.Bank.send_to_admin(amount=amount)  # 发起转账

        admin_end_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)  # 查询管理员余额
        treasury_end_balance = HttpQuery.Bank.query_balances(addr=treasury_addr)
        assert result['code'] == test_send['code']
        assert admin_end_balance == admin_start_balance + Compute.to_u(float(amount)) - 100  # 断言1 管理员余额有没有变化
        assert treasury_end_balance == treasury_start_balance - Compute.to_u(
            number=float(amount)) + 100 + Mint.calculate_treasury_reward()

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_admin_error_min(self, test_send):
        """测试sendToAmin命令，输入小于1u金额，"""
        # 先查询管理员余额
        amount = "{:.20f}".format(test_send['min_amount'])
        start_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_start_balance = treasury_balances()  # 查询国库余额
        result = Tx.Bank.send_to_admin(amount=amount)  # 发起转账
        end_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)  # 查询管理员余额
        treasury_end_balance = treasury_balances()
        assert "Error" in result  # 断言1 报错
        assert end_balance == start_balance  # 断言：管理员余额没有变化
        assert treasury_end_balance == treasury_start_balance  # 断言，国库金额没有变化

    # @pytest.mark.parametrize("test_case", test_data)
    def test_send_to_admin_error_max(self):
        """测试sendToAmin命令，输入大于余额的金额，"""

        amount = "1000000000000000"
        start_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)  # 先查询管理员余额
        treasury_start_balance = treasury_balances()
        time.sleep(1)  # 太快了收益可能没到账
        result = Tx.Bank.send_to_admin(amount=amount)
        end_balance = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_end_balance = treasury_balances()
        assert "is smaller" in str(result)  # 断言1 报错
        assert end_balance == start_balance - 100  # 断言：管理员的交易上链了，仍然要付手续费，

        assert treasury_end_balance == (treasury_start_balance + 100 + Mint.calculate_treasury_reward()) or (
                treasury_start_balance + 100 + (Mint.calculate_treasury_reward() * 2))  # 断言，国库金额没有变化

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_admin_error_from(self, test_send):
        """测试sendToAmin命令，--from=模块账号，"""
        other_name = test_send.get('test_name')
        other_addr = Query.Account.auth_account(pool_name=other_name)
        send_date = dict(amount=1, super_addr=other_addr)
        # 发起转账
        result = Tx.Bank.send_to_admin(**send_date)
        assert "Error" in result
        pass


class TestSendTreasury(object):
    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_treasury_success(self, test_send):
        """测试sendToTreasury命令，输入正确的转账正确金额，"""
        amount = "{:.10f}".format(test_send['success_amount'])
        admin_balance_start = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_balance_start = treasury_balances()
        result = Tx.Bank.send_to_treasury(amount=amount)
        admin_balance_end = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        treasury_balance_end = treasury_balances()
        assert 0 == result['code']
        assert admin_balance_end == admin_balance_start - Compute.to_u(number=float(amount)) - 100
        assert treasury_balance_end == treasury_balance_start + Compute.to_u(
            number=float(amount)) + 100 + Mint.calculate_treasury_reward()
        pass

    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_treasury_min(self, test_send):
        """测试sendToTreasury命令，输入小于1u金额，"""
        amount = "{:.20f}".format(test_send['min_amount'])
        # 查询管理员开始余额
        admin_balance_start = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库开始余额
        treasury_balance_start = treasury_balances()
        result = Tx.Bank.send_to_treasury(amount=amount)
        # 查询管理员结束余额
        admin_balance_end = HttpQuery.Bank.query_balances(addr=Tx.super_addr)
        # 查询国库结束余额
        treasury_balance_end = treasury_balances()
        # 判断交易是否成功上链
        assert "Error" in result  # 断言1 报错
        assert admin_balance_end == admin_balance_start  # 断言：管理员余额没有变化
        assert treasury_balance_end == treasury_balance_start  # 断言，国库金额没有变化

    def test_send_to_treasury_max(self):
        """测试sendToTreasury命令，输入大于余额金额，"""
        amount = "100000000000000000"
        # 发起转账
        result = Tx.Bank.send_to_treasury(amount=amount)
        logger.info(f"result={result}")
        assert "is smaller than" in str(result)

        pass

    # @pytest.mark.xfail
    @pytest.mark.parametrize("test_send", test_data)
    def test_send_to_treasury_form(self, test_send):
        """测试sendToTreasury命令，--from=模块账号，"""
        # 先查国库开始金额
        other_name = test_send.get('test_name')
        treasury_balance_start = treasury_balances()
        # 拿到其他人的地址
        other_addr = Query.Account.auth_account(pool_name=other_name)
        send_data = dict(amount=1, super_addr=other_addr)
        # 发起转账
        result = Tx.Bank.send_to_treasury(**send_data)
        treasury_balance_end = treasury_balances()
        # 断言报错在不在里面
        assert "key not found" in result
        # 查询国库金额有没有变化
        assert treasury_balance_start == treasury_balance_end


class TestSendTo(object):

    @pytest.mark.parametrize("test_send_data", test_data)
    def test_send_to_user_success(self, creat_user_and_delete, test_send_data):
        amount = "{:.10f}".format(test_send_data['success_amount'])
        user_addr_a, user_addr_b, user_balances_a_start = creat_user_and_delete
        # A用户给B用户转钱 在余额范围内
        send_data_test = dict(from_addr=user_addr_a, to_addr=user_addr_b, amount=amount)
        Tx.Bank.send_tx(**send_data_test)
        # 查看A用户余额
        user_balances_a_end = HttpQuery.Bank.query_balances(addr=user_addr_a)
        # 查看B用户余额
        user_balances_b_end = HttpQuery.Bank.query_balances(addr=user_addr_b)
        assert user_balances_a_end == user_balances_a_start - Compute.to_u(float(amount)) - 100
        assert user_balances_b_end == Compute.to_u(float(amount))
        pass

    @pytest.mark.parametrize("test_send_data", test_data)
    def test_send_to_user_min(self, creat_user_and_delete, test_send_data):
        """测试sendToAmin命令，输入小于1u金额，"""
        # 先查询管理员余额
        amount = "{:.20f}".format(test_send_data['min_amount'])
        # amount = "{:.20f}".format(0.0000001)
        user_addr_a, user_addr_b, user_balances_a_start = creat_user_and_delete
        # A用户给B用户转钱 在余额范围内
        send_data_test = dict(from_addr=user_addr_a, to_addr=user_addr_b, amount=amount)
        result = Tx.Bank.send_tx(**send_data_test)
        # 查看A用户余额
        user_balances_a_end = HttpQuery.Bank.query_balances(addr=user_addr_a)
        # 查看B用户余额
        user_balances_b_end = HttpQuery.Bank.query_balances(addr=user_addr_b)

        assert "Error" in result  # 断言1 报错
        assert user_balances_a_end == user_balances_a_start  # 断言：用户A的余额没变化，交易没上链
        assert user_balances_b_end == 0  # 断言，user_B的余额还是没钱
        pass

    def test_send_to_user_max(self, creat_user_and_delete):
        # amount = "{:.10f}".format(test_send_data['success_amount'])
        amount = "100"
        user_addr_a, user_addr_b, user_balances_a_start = creat_user_and_delete
        # A用户给B用户转钱 在余额范围内
        send_data_test = dict(from_addr=user_addr_a, to_addr=user_addr_b, amount=amount)
        result = Tx.Bank.send_tx(**send_data_test)
        # 查看A用户余额
        user_balances_a_end = HttpQuery.Bank.query_balances(addr=user_addr_a)
        # 查看B用户余额
        user_balances_b_end = HttpQuery.Bank.query_balances(addr=user_addr_b)
        assert "is smaller" in str(result)  # 断言1 报错
        assert user_balances_a_end == user_balances_a_start - 100

        assert user_balances_b_end == 0
        pass

    @pytest.mark.parametrize("pool", pool_name)
    def test_send_to_pool(self, pool):
        amount = "1"
        # user_addr_a, user_addr_b, user_balances_a_start = creat_user_and_delete

        user_addr_a = Query.Key.address_of_name(username="test_bank")
        other_addr = Query.Account.auth_account(pool_name=pool['pool_name'])
        # 给模块账户转钱
        send_data_test = dict(from_addr=user_addr_a, to_addr=other_addr, amount=amount)
        result = Tx.Bank.send_tx(**send_data_test)
        logger.info(f"result={result}")
        # 查看A用户余额
        # user_balances_a_end = HttpQuery.Bank.query_balances(addr=user_addr_a)
        # 查看B用户余额
        assert "is not allowed to receive funds: unauthorized" in str(result)  # 断言1 报错
        # assert user_balances_a_end == user_balances_a_start - 100

        pass
