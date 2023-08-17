# -*- coding: utf-8 -*-
import time

import pytest
import yaml

from tools.compute import Compute
from tools.rewards import Reward
from x.tx import Tx
from cases import unitcases
from loguru import logger
from x.query import Query, HttpQuery

with open('./test_fixed.yml', 'r') as file:
    test_data = yaml.safe_load(file)
test_kyc = unitcases.Kyc()


# new_kyc且给kyc用户转钱
def new_kyc_and_send(region=False):
    amount = 10
    user_address = test_kyc.test_new_kyc_user()
    print(f"user_info={user_address}")

    test_bank_addr = Query.Key.address_of_name(username="test_bank")
    print(f"test_bank_addr={test_bank_addr},user_address={user_address}")
    Tx.Bank.send_tx(from_addr=test_bank_addr, to_addr=user_address, amount=amount)
    # 拿Kyc的区id
    region_id = HttpQuery.Staking.kyc(addr=user_address)['kyc']['regionId']
    if region is True:
        return user_address, amount, region_id
    else:
        return user_address, amount

    # user_name = Query.Key.name_of_addre(addr=user_address)
    # Tx.Keys.delete(user_name=user_name)
    # yield 0


def delete_addr(user_addr):
    user_name = Query.Key.name_of_addre(addr=user_addr)
    Tx.Keys.delete(user_name=user_name)
    return 0


class TestFixed:
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    base_cfg = test_bank.tx

    # new一个KYC
    def test_new_kyc(self):
        user_name = "test_wang_fixed"
        Tx.Keys.add(username=user_name)
        user_addr = Query.Key.address_of_name(username=user_name)

        user_info = self.test_kyc.test_new_kyc_user(addr=user_addr)  # 随机生成一个KYC用户
        logger.info(f"")
        return user_info

    # 拿到这个KYC
    def test_get_kyc_info(self):
        user_name = "test_wang_fixed"
        user_addr = Query.Key.address_of_name(username=user_name)
        # print('u=',user_addr)
        region_id = "nga"
        assert 1 == 1

        return user_addr, region_id

    # 发起定期委托，
    @pytest.mark.parametrize("test_fixed", test_data)
    def test_fixed_success_amount_and_mouth(self, test_fixed):
        """发起定期委托： 正常金额测试 这里需要完善的是随机拿一个KYC用户"""
        # 准备数据
        user_addr, send_amount, region_id = new_kyc_and_send(region=True)
        try:
            # send_addr = Query.Key.address_of_name(username="test_bank")
            amount = "{:.10f}".format(test_fixed['success_amount'])
            mouth = test_fixed['mouth']
            # 给这个账户转一笔钱，
            # Tx.Bank.send_tx(from_addr=send_addr, to_addr=user_addr, amount=float(amount) + 1)
            start_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            # 正常发起一次定期
            user_fixed_list_start = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            region_fixed_list_start = (Query.Staking.show_fixed_deposit_by_region(region_id=region_id))['FixedDeposit']
            all_fixed_list_start = HttpQuery.Staking.fixed_deposit()
            # 发起委托
            result = Tx.Staking.deposit_fixed(from_addr=user_addr, amount=amount, month=mouth)
            # logger.info(f"result = {result}")
            # 查看自己的定期列表有没有新增定期 6
            user_fixed_list_end = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            #  查看区域定期委托列表有没有新增
            region_fixed_list_end = (Query.Staking.show_fixed_deposit_by_region(region_id=region_id))['FixedDeposit']
            # 查看全网定期委托列表有没有增加
            all_fixed_list_end = HttpQuery.Staking.fixed_deposit()
            # 查看用户结束余额
            end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            logger.info(f"end_balance={end_balance}")
            # 断言1：自己定期列表
            assert len(user_fixed_list_end) == len(user_fixed_list_start) + 1
            # 断言2： 区域定期委托列表
            assert len(region_fixed_list_end) == len(region_fixed_list_start) + 1
            # 断言3：全网定期委托列表
            assert len(all_fixed_list_end) == len(all_fixed_list_start) + 1
            # 断言3： 用户结束余额==开始余额-委托金额-手续费
            assert end_balance == start_balance - Compute.to_u(float(amount)) - 100
        finally:
            # 提取自己的定期打扫数据，删除用户打扫数据
            # fixed_info = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            user_fixed_list_end=HttpQuery.Staking.fixed_deposit(addr=user_addr)
            latest_id = max([i['id'] for i in user_fixed_list_end])
            Tx.Staking.withdraw_fixed(from_addr=user_addr, fixed_delegation_id=latest_id)
            delete_addr(user_addr=user_addr)
        pass

    # 测试最小金额
    @pytest.mark.parametrize("test_fixed", test_data)
    def test_fixed_min_or_max_amount(self, test_fixed):
        """发起定期，最大（超过自身余额）或者最小（小于0.01mec）金额测试"""
        user_addr, region_id = self.test_get_kyc_info()
        # 发起定期委托
        amount = "{:.10f}".format(test_fixed['min_amount'])

        mouth = test_fixed['mouth']

        result = Tx.Staking.deposit_fixed(from_addr=user_addr, amount=amount, month=mouth)
        logger.info(f"result={result}")

        assert "amount is less than 0.01ME" or "fixed deposit amount error" in str(result)
        pass

    # 测试最大月份
    @pytest.mark.parametrize("test_fixed", [2, 4, 5, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21])
    def test_fixed_error_mouth(self, test_fixed):
        user_addr, region_id = self.test_get_kyc_info()
        mouth = test_fixed
        # 发起定期委托
        result = Tx.Staking.deposit_fixed(from_addr=user_addr, amount=mouth, month=mouth)
        # logger.info(f"result={result}")
        assert "parameter error" in str(result)

        pass

    # 测试非KYC用户发起定期委托
    def test_fixed_no_kyc(self):
        """测试非KYC用户发起定期委托 这里需要补充一下，一个非KYC、还有superadmin 还有 其他的各种账户"""
        # 发起定期
        user_addr = Query.Key.address_of_name(username="testname003")
        send_addr = Query.Key.address_of_name(username="test_bank")
        # 给这个用户转钱，防止没钱
        Tx.Bank.send_tx(from_addr=send_addr, to_addr=user_addr, amount=1)
        # 用户发起定期委托
        result = Tx.Staking.deposit_fixed(from_addr=user_addr, amount="1", month="1")
        # logger.info(f"result={result}")
        assert "only kyc user can do fixed deposit" in str(result)

        pass

    @pytest.mark.parametrize("test_fixed", [1, 2, 3])
    def test_fixed_value(self, test_fixed):
        # v = test_fixed['fixed']['f']
        logger.info(f"v={test_fixed}")
        assert 1 == 1
        pass


class TestFixedWithdraw:
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    base_cfg = test_bank.tx

    # new_kyc 且给kyc用户转钱

    # 正常提取定期，计算收益
    def test_withdraw_expire(self):
        # 用户发起定期委托
        # fixed_data = dict(from_addr=user_addr,)
        user_addr, send_amount = new_kyc_and_send()
        # user_addr = user_info
        # send_amount = send_amount_info
        fixed_amount = send_amount - 1
        month = 1
        try:

            Tx.Staking.deposit_fixed(from_addr=user_addr, month=month, amount=fixed_amount)
            start_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            # 查询自己的定期委托，拿出fixed_id
            fixed_info = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            fixed_id = max([i['id'] for i in fixed_info])
            # 等待1分钟
            time.sleep(60)
            # 用户提取定期委托
            Tx.Staking.withdraw_fixed(from_addr=user_addr, fixed_delegation_id=fixed_id)
            # 查询用户余额
            end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            # 用户到账和手动计算
            rate = HttpQuery.Staking.fixed_deposit_rate(month=month)
            reward = Reward.fixed_reward(rate=rate, month=month, amount=fixed_amount)
            logger.info(f"end_balance={end_balance}")
            assert end_balance == start_balance + Compute.to_u(fixed_amount) - 100 + reward
        # new_kyc_and_send_delete()
        finally:
            delete_addr(user_addr=user_addr)
        pass

    #  提取未到期的定期
    def test_withdraw_no_expire(self):
        user_addr, send_amount = new_kyc_and_send()
        amount = send_amount - 1
        # 查询用户余额
        try:
            start_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            user_fixed_list_start = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            all_fixed_list_start = HttpQuery.Staking.fixed_deposit()

            # 先发起一笔定期
            Tx.Staking.deposit_fixed(from_addr=user_addr, amount=amount, month="1")
            # 查出用户定期id 拿到用户的委托id
            fixed_info = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            latest_id = max([i['id'] for i in fixed_info])

            # 然后提取一笔定期
            Tx.Staking.withdraw_fixed(from_addr=user_addr, fixed_delegation_id=latest_id)
            # 获取用户余额
            end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            user_fixed_list_end = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            all_fixed_list_end = HttpQuery.Staking.fixed_deposit()

            # 断言1 ：用户余额
            assert end_balance == start_balance - 100 - 100
            # 断言2：用户委托列表
            assert len(user_fixed_list_start) == len(user_fixed_list_end)
            # 断言3：全网委托列表
            assert len(all_fixed_list_start) == len(all_fixed_list_end)
        finally:
            delete_addr(user_addr=user_addr)

        pass

    # 输入已经提取过的id
    def test_deposit_id_done(self):
        user_addr, send_amount = new_kyc_and_send()
        amount = 0.01
        # 查询用户余额
        try:
            start_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            user_fixed_list_start = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            all_fixed_list_start = HttpQuery.Staking.fixed_deposit()

            # 先发起一笔定期
            Tx.Staking.deposit_fixed(from_addr=user_addr, amount=amount, month="1")
            # 查出用户定期id 拿到用户的委托id
            fixed_info = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            latest_id = max([i['id'] for i in fixed_info])

            # 然后提取一笔定期
            Tx.Staking.withdraw_fixed(from_addr=user_addr, fixed_delegation_id=latest_id)
            # 然后再提取一笔
            repeat_withdraw_info = Tx.Staking.withdraw_fixed(from_addr=user_addr, fixed_delegation_id=latest_id)
            # 获取用户余额

            end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
            user_fixed_list_end = HttpQuery.Staking.fixed_deposit(addr=user_addr)
            all_fixed_list_end = HttpQuery.Staking.fixed_deposit()
            # 断言响应
            assert "fixed deposit not found" in str(repeat_withdraw_info)
            # 断言用户余额
            assert end_balance == start_balance - 100
            # 断言个人和区域委托列表没有任何变化
            assert len(user_fixed_list_start) == len(user_fixed_list_end)
            assert len(all_fixed_list_start) == len(all_fixed_list_end)
        finally:
            delete_addr(user_addr=user_addr)

    # 换一个人提取定期
    def test_deposit_withdraw_payee_error(self):
        user_addr = "me1m8yxlprg75d5esvlv23u9nyzanax2wu44yjmls"
        user_addr2 = "me1m63cs3c4zmfl7amecg9xc0sd6ynh5jk70475f0"
        amount = 0.01
        # 查询用户余额
        user_fixed_list_start = HttpQuery.Staking.fixed_deposit(addr=user_addr)
        # region_fixed_list_start = (Query.Staking.show_fixed_deposit_by_region(region_id=region_id))['FixedDeposit']
        all_fixed_list_start = HttpQuery.Staking.fixed_deposit()

        # 先发起一笔定期
        Tx.Staking.deposit_fixed(from_addr=user_addr, amount=amount, month="1")
        # 查出用户定期id 拿到用户的委托id
        fixed_info = HttpQuery.Staking.fixed_deposit(addr=user_addr)
        latest_id = max([i['id'] for i in fixed_info])

        # 然后提取一笔定期
        withdraw_info = Tx.Staking.withdraw_fixed(from_addr=user_addr2, fixed_delegation_id=latest_id)
        print(withdraw_info)
        # 获取用户余额

        end_balance = HttpQuery.Bank.query_balances(addr=user_addr)
        user_fixed_list_end = HttpQuery.Staking.fixed_deposit(addr=user_addr)
        all_fixed_list_end = HttpQuery.Staking.fixed_deposit()
        assert "only depositor can withdraw (fixed deposit payee error): do fixed withdraw error" in str(withdraw_info)
        # 断言个人和区域委托列表没有任何变化
        assert len(user_fixed_list_end) == len(user_fixed_list_start) + 1
        assert len(all_fixed_list_end) == len(all_fixed_list_start) + 1
        # 提取定期打扫数据
        Tx.Staking.withdraw_fixed(from_addr=user_addr, fixed_delegation_id=latest_id)

    def test_delete(self):
        user_addr, send_amount = new_kyc_and_send()
        print("user_addr, send_amount", user_addr, send_amount)
        time.sleep(3)
        r = new_kyc_and_send()
        print(r)
        pass
