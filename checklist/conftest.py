# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import unitcases


@pytest.fixture(scope="session")
def setup_create_region():
    logger.info("fixture: setup_create_region")
    region = unitcases.Region()
    region_admin_info, region_id, region_name = region.test_create_region()
    yield region_admin_info, region_id, region_name

# # 更新一个不存在的region_name
# _, update_region_name = handle_name.create_region_id_and_name()
#
# update_region_data = [
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", region_name=update_region_name),
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", delegators_limit="10"),
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", fee_rate="0.1"),
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", totalStakeAllow="1000"),
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", userMaxDelegateAC="1000"),
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", userMinDelegateAC="2"),
#     dict(region_id=region_id, from_addr=region_admin_addr, fees="1", isUndelegate=True),  # 控制是否能提取永久质押开关
# ]
