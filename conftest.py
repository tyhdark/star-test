# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.name import RegionInfo
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

region = unitcases.Region()
kyc = unitcases.Kyc()
validator = unitcases.Validator()
base = unitcases.Base()


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


# if __name__ == '__main__':
# print(get_region_id_existing())
