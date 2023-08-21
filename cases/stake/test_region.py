# -*- coding: utf-8 -*-
import inspect
import time

from loguru import logger

from cases import unitcases
from tools.name import RegionInfo, ValidatorInfo
from x.query import Query, HttpQuery
from x.tx import Tx
from tools.compute import Compute
from config.chain import config, GasLimit, Fees


# 单元测试region模块


class TestRegion(object):
    tx = Tx()
    hq = HttpQuery()
    q = Query()
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_validator = unitcases.Validator()
    base_cfg = test_bank.tx
    user_addr = None

    def test_already_bind_validator_create_region(self):
        """
        用已绑定的验证者去创建区
        """
        logger.info("TestRegion/test_already_bind_validator_create_region")
        # 传入错误的参数创建区
        region_data = dict(region_name=RegionInfo.region_name_for_create(), node_name="test")
        rep = self.tx.staking.create_region(**region_data)
        assert "Error" in rep

        # 传入错误的区名称
        # Error: input
        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=True)
        res = self.tx.staking.create_region(region_name="XXX",
                                            node_name=node_name_var)
        assert "Error" in res

        # 用已绑定的验证者去创建区 提示code=1173 failed to execute message; message index: 0: kyc region bonded validator
        # duplicates: input validator duplicates with already bonded validators
        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=True)
        res = self.tx.staking.create_region(region_name=RegionInfo.region_name_for_create(),
                                            node_name=node_name_var)
        assert res['code'] == 1173

        # 根据区id查到这个区的信息
        region_id = RegionInfo.region_for_id_existing()
        rep = self.q.staking.show_region(region_id)
        assert region_id == rep['region']['regionId']

    def test_un_bind_validator_create_region(self):
        """
        未绑定的验证者去创建区
        """
        logger.info("TestRegion/test_un_bind_validator_create_region")
        # 传入错误的参数创建区
        region_data = dict(region_name=RegionInfo.region_name_for_create(), node_name="test")
        rep = self.tx.staking.create_region(**region_data)
        assert "Error" in rep

        # 传入错误的区名称
        # Error: input
        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        assert len(node_name_var) != 0, f"Not available validator"

        res = self.tx.staking.create_region(region_name="XXX",
                                            node_name=node_name_var)
        assert "Error" in res

        # # 没绑定的验证者创建已存在的区
        # region_name = RegionInfo.region_for_id_existing()
        # node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        # res = self.tx.staking.create_region(region_name,
        #                                     node_name=node_name_var)

        # # 没绑定的验证者创建区
        # region_name = RegionInfo.region_name_for_create()
        # node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        # res = self.tx.staking.create_region(region_name,
        #                                     node_name=node_name_var)
        #
        # time.sleep(self.tx.sleep_time)
        # tx_resp = self.hq.tx.query_tx(region_info['txhash'])
        # assert tx_resp['code'] == 0, f"test_create_region failed, resp: {tx_resp}"
        #
        # # 根据区id查到这个区的信息
        # region_id = region_name.lower()
        # rep = self.q.staking.show_region(region_id)
        # assert region_id == rep['region']['regionId']
