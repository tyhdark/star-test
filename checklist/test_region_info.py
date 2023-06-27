# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import package
from tools import handle_query


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    test_region = package.RegionPackage()
    handle_q = handle_query.HandleQuery()

    def test_update_region(self, setup_create_region):
        """测试修改区域信息"""
        logger.info("TestRegionInfo/test_update_region")
        logger.info(f"setup_update_region:{setup_create_region}")
        region_admin_addr, region_id, region_name, update_region_data = setup_create_region
        for i in update_region_data:
            logger.info(f"request: {i}")
            self.test_region.test_update_region(i)
        # TODO assert

    # TODO 水位异常场景测试
