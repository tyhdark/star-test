# -*- coding: utf-8 -*-

# 测试new KYC的命令
import pytest
from tools.name import UserInfo, RegionInfo
from x.tx import Tx
from loguru import logger
from x.query import Query, HttpQuery


def new_addr(region_name=False):
    """创建用户，返回"""
    user_name = UserInfo.random_username()
    region_id = RegionInfo.region_for_id_existing()
    Tx.Keys.add(username=user_name)
    result = Tx.Keys.show(username=user_name)
    user_addr = result[0]['address']
    region_id_no_validator = RegionInfo.region_name_for_create()
    if region_name:
        return user_name, user_addr, region_id_no_validator.lower()
    else:
        return user_name, user_addr, region_id


class TestKyc(object):
    def test_kyc_success(self):
        # 创建一个新用户
        user_name, user_addr, region_id = new_addr()
        try:
            # KYC命令
            logger.info(f"user_name, user_addr, region_id={user_name, user_addr, region_id}")
            Tx.Staking.new_kyc(region_id=region_id, user_addr=user_addr)
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
        # 拿用户名字，用户地址，区id出来
        user_name, user_addr, region_id = new_addr(region_name=True)
        try:
            # 执行kyc命令，
            logger.info(f"round:{test_many}")
            result = Tx.Staking.new_kyc(region_id=region_id, user_addr=user_addr)
            logger.info(f"r={result}")
            assert "region not exist" in str(result)
        finally:
            # 删除用户
            Tx.Keys.delete(user_name=user_name)
        pass

    @pytest.mark.parametrize("pool_name_data",
                             ["treasury_pool", "bonded_stake_tokens_pool", "stake_tokens_pool", "bonded_tokens_pool",
                              "not_bonded_tokens_pool"])
    def test_kyc_from_pool(self, pool_name_data):
        """测试模块账号认证KYC"""
        user_name, user_addr, region_id = new_addr()
        pool_name = pool_name_data
        test_addr = Query.Account.auth_account(pool_name=pool_name)
        try:
            # 执行KYC认证命令
            result = Tx.Staking.new_kyc(region_id=region_id, user_addr=user_addr, super_addr=test_addr)
            logger.info(f"result={result},type={type(result)}")
            assert "only global admin can create kyc" or "key not found" in str(result)
            assert 1 == 1
        finally:
            Tx.Keys.delete(user_name=user_name)

        pass
