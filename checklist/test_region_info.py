# -*- coding: utf-8 -*-

import pytest
from loguru import logger

from case.staking.region.test_region import TestRegion
from tools import handle_query

logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    test_region = TestRegion()
    handle_q = handle_query.HandleQuery()

    def test_update_region(self, setup_update_region):
        """测试修改区域信息"""
        logger.info("TestRegionInfo/test_update_region")
        logger.info(f"setup_update_region:{setup_update_region}")
        region_admin_addr, region_id, update_region_data = setup_update_region
        for i in update_region_data:
            logger.info(f"request: {i}")
            self.test_region.test_update_region(i)
        pass
