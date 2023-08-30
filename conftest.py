# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.name import RegionInfo
from tools.compute import Compute
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

region = unitcases.Region()
kyc = unitcases.Kyc()
validator = unitcases.Validator()
base = unitcases.Base()
keys = unitcases.Keys()
bank = unitcases.Bank()


# @pytest.fixture(scope="session")
# def setup_create_region():
#     logger.info("fixture: setup_create_region")
#     region_admin_info, region_id, region_name = region.test_create_region()
#     yield region_admin_info, region_id, region_name
@pytest.fixture(scope="session")
def setup_create_region():
    """创建区，拿出区id出来"""
    logger.info("fixture: setup_create_region")
    region_id = region.test_create_region()
    yield region_id


@pytest.fixture(scope="session")
def setup_create_validator_and_region():
    logger.info("fixture: setup_create_validator_and_region")
    node_name = validator.test_create_validator()
    logger.info(f"node_name是：{node_name}")
    # 根据上面创建出来的节点，创建区
    region_id = region.test_create_region(node_name=node_name)
    logger.info(f"region_id是：{region_id}")
    return node_name, region_id


@pytest.fixture(scope="function")
def setup_create_region_and_kyc_user():
    logger.info("fixture: setup_create_region_and_kyc_user")
    region_admin_info, region_id, region_name = region.test_create_region()
    region_admin_addr = region_admin_info['address']

    kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    user_info = kyc.test_new_kyc_user(**kyc_data)
    user_addr = user_info['address']

    yield region_admin_addr, region_id, region_name, user_addr


@pytest.fixture(scope="function")
def get_region_id_existing():
    """获取链上存在的区id"""
    region_id = RegionInfo.region_for_id_existing()
    return region_id


@pytest.fixture()
def get_treasury_balances():
    """获取国库余额"""
    # 拿到国库地址，
    treasury_addr = base.q.Account.auth_account(pool_name="treasury_pool")
    treasury_balance = base.hq.Bank.query_balances(addr=treasury_addr)
    treasury_balance2 = base.q.Bank.query_balances(addr=treasury_addr)
    # 查询国库余额
    yield treasury_balance
    treasury_balance2 = base.hq.Bank.query_balances(addr=treasury_addr)
    pass


# 一个生成器函数，用于生成测试数据
def get_balance(user_id):
    # 这里可以实际调用接口获取余额
    # 这里为了演示简单，直接返回一个示例值
    return user_id * 100


# 定义一个带有 yield 语句的 fixture，每次调用会返回一个不同的值
@pytest.fixture
def balance():
    user_ids = [1, 2, 3]  # 这里可以根据需要定义不同的用户ID
    for user_id in user_ids:
        yield get_balance(user_id)


@pytest.fixture
def creat_one_nokyc():
    """ 创建一个非KYC用户，给他转钱，然后删除这个用户，返回地址和金额"""
    # 在测试之前执行的操作
    print("Setup============")
    user_addr_a = (kyc.test_add())["address"]
    amount = 10
    # user_addr_b = (kyc.test_add())["address"]
    bank_addr = (kyc.test_show(user_name="test_bank"))["address"]
    # time.sleep(2)
    kyc.tx.Bank.send_tx(from_addr=bank_addr, to_addr=user_addr_a, amount=amount)
    time.sleep(5)
    # user_balances_a = kyc.hq.Bank.query_balances(addr=user_addr_a)

    # 返回测试函数前的上下文，类似于 setup 方法
    yield user_addr_a, Compute.to_u(amount)
    kyc.test_delete_key(addr=user_addr_a)
    # kyc.test_delete_key(addr=user_addr_b)

    # 在测试之后执行的操作
    print("creat_two_user_and_delete_Teardown_用户已删除")


@pytest.fixture
def creat_two_nokyc():
    """ 创建两个非KYC用户，且给A用户转钱,删除这两个用户"""
    # 在测试之前执行的操作
    print("Setup")
    user_addr_a = (kyc.test_add())["address"]
    user_addr_b = (kyc.test_add())["address"]
    bank_addr = (kyc.test_show(user_name="test_bank"))["address"]
    amount = 5
    # time.sleep(2)
    kyc.tx.Bank.send_tx(from_addr=bank_addr, to_addr=user_addr_a, amount=amount)
    time.sleep(5)
    # user_balances_a = kyc.hq.Bank.query_balances(addr=user_addr_a)

    # 返回测试函数前的上下文，类似于 setup 方法
    yield user_addr_a, user_addr_b, Compute.to_u(amount)
    kyc.test_delete_key(addr=user_addr_a)
    kyc.test_delete_key(addr=user_addr_b)

    # 在测试之后执行的操作
    print("creat_two_user_and_delete_Teardown_用户已删除")


@pytest.fixture
def creat_one_kyc():
    """创建一个KYC用户，转账，最后会删掉"""
    print("Setup")
    amount = 10
    user_addr_a = kyc.test_new_kyc_user()
    time.sleep(6)
    bank_addr = (kyc.test_show(user_name="test_bank"))["address"]
    kyc.tx.Bank.send_tx(from_addr=bank_addr, to_addr=user_addr_a, amount=amount)
    time.sleep(5)
    # kyc.tx.Bank.send_tx(from_addr=bank_addr, to_addr=user_addr_a, amount=amount)

    # 返回测试函数前的上下文，类似于 setup 方法
    yield user_addr_a, Compute.to_u(amount)
    kyc.test_delete_key(addr=user_addr_a)
    # kyc.test_delete_key(addr=user_addr_b)

    # 在测试之后执行的操作
    print("creat_one_addr_and_send_del_Teardown_用户已删除")


@pytest.fixture()
def creat_one_kyc_region():
    # 创建kyc用户，返回kyc用户的地址，区id 和余额 删掉用户
    amount = 10
    user_addr = kyc.test_new_kyc_user()
    time.sleep(6)
    bank_addr = (kyc.test_show(user_name="test_bank"))["address"]
    kyc.tx.Bank.send_tx(from_addr=bank_addr, to_addr=user_addr, amount=amount)
    time.sleep(6)
    # 拿区id出来
    region_id = kyc.hq.Staking.kyc(addr=user_addr)['kyc']['regionId']
    yield user_addr, Compute.to_u(amount), region_id

    # 然后删除该用户
    user_name = kyc.q.Key.name_of_addre(addr=user_addr)
    kyc.tx.Keys.delete(user_name=user_name)
    print("creat_kyc_user_Teardown_用户已删除   ")


@pytest.fixture(scope='class')
def create_no_kyc_send_money():
    """
    创建一个非kyc用户，超管给用户转100mec
    :return: user_addr
    """
    user_name = "user_tyh_01"
    user_addr = keys.test_add("user_tyh_01")['address']
    time.sleep(base.tx.sleep_time)
    send_data = dict(from_addr=base.tx.super_addr, to_addr=user_addr, amount=100)
    bank.test_send(**send_data)
    logger.info("----------------------->创建")
    yield user_addr
    logger.info("----------------------->删除")
    base.tx.keys.delete(user_name)


pass

# if __name__ == '__main__':
# print(get_region_id_existing())
