# -*- coding: utf-8 -*-
import pytest
from loguru import logger

from cases import unitcases


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    test_region = unitcases.Region()

    def test_update_region(self, setup_update_region_data):
        """测试修改区域信息"""
        logger.info("TestRegionInfo/test_update_region")

        for data in setup_update_region_data:
            logger.info(f"update_region_data: {data}")
            self.test_region.test_update_region(**data)

    # TODO 水位异常场景测试
