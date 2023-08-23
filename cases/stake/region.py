# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.name import RegionInfo, ValidatorInfo
from x.query import Query, HttpQuery
from x.tx import Tx


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

    def test_un_bind_validator_create_region(self):
        """
        未绑定的验证者去创建区
        @Desc:
           - validator 未绑定区的验证者
           - region 链上没有的区
           + expect: 1.如果所有验证者都绑定区忽略该用例
                     2.区创建成功，能正常查询到区id
        """
        logger.info("TestRegion/test_un_bind_validator_create_region")
        if len(ValidatorInfo.validator_bind_node_for_region(bind=False)) == 0:
            pytest.skip("所有验证者都已被绑定")

        # 没绑定的验证者创建区
        region_name = RegionInfo.region_name_for_create()
        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        res = self.tx.staking.create_region(region_name,
                                            node_name=node_name_var)
        time.sleep(self.tx.sleep_time)
        tx_resp = self.hq.tx.query_tx(res['txhash'])
        # 断言创建区成功
        assert tx_resp['code'] == 0, f"test_create_region failed, resp: {tx_resp}"

        # 根据区id查到这个区的信息
        region_id = region_name.lower()
        rep = self.q.staking.show_region(region_id)
        # 断言能查到这个区已被创建
        assert region_id == rep['region']['regionId']

    def test_show_region(self):
        """
        查询已存在的区
        @Desc:
           - exit_region_name 已存在的区
           + expect: 能正常查询到已存在的区相关信息
        """
        exit_region_name = (RegionInfo.region_for_id_existing()).upper()
        # 根据区id查到这个区的信息
        region_id = exit_region_name.lower()
        rep = self.q.staking.show_region(region_id)
        # 断言能查到这个区
        assert region_id == rep['region']['regionId']

    def test_already_bind_validator_create_region(self):
        """
        用已绑定的验证者去创建区
        @Desc:
           - validator 已经绑定区的验证者
           - region 链上没有的区
           + expect: 1.如果所有验证者都没绑定，没有满足该用例的条件，忽略该用例
                     2.验证者已经被绑定，无法创建区
        """
        logger.info("TestRegion/test_already_bind_validator_create_region")

        # 找出链上存在，且已经被绑定的
        no_bind_node = ValidatorInfo.validator_bind_node_for_region(bind=True)
        if len(no_bind_node) == 0:
            pytest.skip("所有的验证者都没有被绑定")

        region_name = RegionInfo.region_name_for_create()
        region_data = dict(region_name=region_name,
                           node_name=no_bind_node)
        resp = self.tx.staking.create_region(**region_data)
        # 断言 传入已绑定区的验证者
        assert 'already bonded validators' in self.hq.tx.query_tx(resp['txhash'])['raw_log']

        # resp = self.q.staking.show_region(region_name.lower())
        # assert 'NotFound' in resp

    @pytest.mark.parametrize("error_region_name", ("xxxx", "USa", "100.9", "TTT"))
    def test_un_bind_validator_create_region_error_region_name(self, error_region_name):
        """
        未绑定的验证者去创建区,传入错误的区名
        @Desc:
           - validator 未绑定区的验证者
           - error_region_name 异常的区名
           + expect: 1.如果所有验证者都绑定区忽略该用例
                     2.传入错误的区名无法创建区
        """
        logger.info("TestRegion/test_un_bind_validator_create_region_error_region_name")
        if len(ValidatorInfo.validator_bind_node_for_region(bind=False)) == 0:
            pytest.skip("所有验证者都已被绑定")

        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        assert len(node_name_var) != 0, f"Not available validator"

        res = self.tx.staking.create_region(region_name=error_region_name,
                                            node_name=node_name_var)
        # 断言 区名错误
        assert "regionName parameter error" in res

    def test_un_bind_validator_create_region_exit_region_name(self):
        """
        未绑定的验证者去创建区,传入已存在的区名
        @Desc:
           - validator 未绑定区的验证者
           - exit_region_name 已创建的取名
           + expect: 1.如果所有验证者都已绑定区，忽略该用例
                     2.传已创建的区名无法创建区1asdasda
        """
        logger.info("TestRegion/test_un_bind_validator_create_region_exit_region_name")
        if len(ValidatorInfo.validator_bind_node_for_region(bind=False)) == 0:
            pytest.skip("所有验证者都已被绑定")

        exit_region_name = (RegionInfo.region_for_id_existing()).upper()
        node_name_var = ValidatorInfo.validator_bind_node_for_region(bind=False)
        assert len(node_name_var) != 0, f"Not available validator"

        resp = self.tx.staking.create_region(region_name=exit_region_name,
                                             node_name=node_name_var)
        # 断言 区已被创建
        assert 'region already exist' in self.hq.tx.query_tx(resp['txhash'])['raw_log']
