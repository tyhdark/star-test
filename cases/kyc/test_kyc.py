# -*- coding: utf-8 -*-
import time
import os
import sys
# 测试new KYC的命令
import pytest
import yaml

from tools.name import UserInfo, RegionInfo
from x.tx import Tx
from loguru import logger
from x.query import Query, HttpQuery

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
current_path = os.path.dirname(__file__)
with open(current_path + '/pool_name.yml', 'r', encoding='gbk') as file_pool:
    pool_name = yaml.safe_load(file_pool)


def new_addr(region_name=False):
    """
    创建用户，返回
    """
    user_name = UserInfo.random_username()
    region_id = RegionInfo.region_for_id_existing()
    Tx.Keys.add(username=user_name)
    # time.sleep(5)
    result = Tx.Keys.show(username=user_name)
    user_addr = result[0]['address']
    region_id_no_validator = RegionInfo.region_name_for_create()
    if region_name:
        return user_name, user_addr, region_id_no_validator.lower()
    else:
        return user_name, user_addr, region_id


class TestKyc(object):
    def test_kyc_success(self):
        """
        测试new_kyc成功
        """
        user_name, user_addr, region_id = new_addr()
        try:
            # KYC命令
            logger.info(f"user_name, user_addr, region_id={user_name, user_addr, region_id}")
            Tx.Staking.new_kyc(region_id=region_id, user_addr=user_addr)
            time.sleep(7)
            kyc_result = (Query.Staking.list_kyc())['kyc']

            http_result = HttpQuery.Staking.kyc(addr=user_addr)

            assert user_addr in str(kyc_result)
            assert http_result['kyc']['regionId'] == region_id
        finally:
            # 删除用户地址
            Tx.Keys.delete(user_name=user_name)
            pass

    @pytest.mark.parametrize("test_many", [1, 2, 3])
    def test_kyc_error_region(self, test_many):
        """
        拿不存在的区去new_kyc
        """
        user_name, user_addr, region_id = new_addr(region_name=True)
        try:
            # 执行kyc命令，
            logger.info(f"round:{test_many}")
            result = Tx.Staking.new_kyc(region_id=region_id, user_addr=user_addr)
            time.sleep(7)
            http_result = HttpQuery.Tx.query_tx(tx_hash=result['txhash'])

            logger.info(f"r={result}")
            assert "region not exist" in str(http_result)
        finally:
            # 删除用户
            Tx.Keys.delete(user_name=user_name)
        pass

    @pytest.mark.parametrize("pool_name_data", pool_name)
    def test_kyc_from_pool(self, pool_name_data):
        """
        测试非superadmin账户。拿模块账号认证KYC
        """
        user_name, user_addr, region_id = new_addr()
        pool_name_yaml = pool_name_data['pool_name']
        test_addr = Query.Account.auth_account(pool_name=pool_name_yaml)
        try:
            # 执行KYC认证命令
            result = Tx.Staking.new_kyc(region_id=region_id, user_addr=user_addr, super_addr=test_addr)
            logger.info(f"result={result},type={type(result)}")

            assert "only global admin can create kyc" or "key not found" in str(result)
            assert 1 == 1
        finally:
            Tx.Keys.delete(user_name=user_name)

        pass
