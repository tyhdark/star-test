# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import unitcases
from tools.name import RegionInfo

region = unitcases.Region()
kyc = unitcases.Kyc()


@pytest.fixture(scope="session")
def setup_create_region():
    logger.info("fixture: setup_create_region")
    region_admin_info, region_id, region_name = region.test_create_region()
    yield region_admin_info, region_id, region_name


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
def setup_update_region_data():
    region_admin_info, region_id, region_name = region.test_create_region()
    region_admin_addr = region_admin_info['address']
    # 获取链上不存在的region_name
    _, update_region_name = RegionInfo.create_region_id_and_name()

    update_region_data = [
        dict(region_id=region_id, from_addr=region_admin_addr, region_name=update_region_name),
        dict(region_id=region_id, from_addr=region_admin_addr, delegators_limit=10),
        dict(region_id=region_id, from_addr=region_admin_addr, fee_rate=0.1),
        dict(region_id=region_id, from_addr=region_admin_addr, totalStakeAllow=1000),
        dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=1000),
        dict(region_id=region_id, from_addr=region_admin_addr, userMinDelegateAC=2),
        dict(region_id=region_id, from_addr=region_admin_addr, isUndelegate=True),  # 控制永久质押开关 True为可提取
    ]
    yield update_region_data