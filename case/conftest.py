# -*- coding: utf-8 -*-
"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/3/7 09:36
@Version :  V1.0
@Desc    :  None
"""
import pytest

from case.staking.region.test_region import TestRegion


@pytest.fixture(scope="class")
def create_region_fixture():
    """查已存在的region, 不存在区则新建"""
    region_admin_addr, region_id = TestRegion()
    yield region_admin_addr, region_id
