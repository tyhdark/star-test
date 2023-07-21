# -*- coding: utf-8 -*-
import decimal
import math
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute
from tools.parse_response import HttpResponse
from tools.rewards import Reward


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionDelegate(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_key = unitcases.Keys()
    test_bank = unitcases.Bank()
    test_validator = unitcases.Validator()
    base_cfg = test_bank.tx
    user_addr = None

    # def test_region_delegate(self, setup_create_region):
    #     """测试新创建区域并质押"""
    #     logger.info("TestRegionDelegate/test_region_delegate")
    #     region_admin_info, region_id, region_name = setup_create_region #
    #     region_admin_addr = region_admin_info['address']
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info['address']
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=10)
    #     self.test_del.test_delegate(**del_data)
    #
    #     user_balance = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
    #     assert user_balance['amount'] == str(Compute.to_u(100 - 10 - self.base_cfg.fees))
    #
    #     # 验证区信息
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_info['region_commission']['currentDemandTotalUAC'] == str(Compute.to_u(10 + 1))
    #     assert user_addr in region_info['delegators']['delegators']
    #
    #     return region_admin_addr, region_id, user_addr
    # @pytest.skip
    # def test_region_delegate(self, setup_create_validator_and_region):
    #     """测试新创建节点，创建区域，创建KYC并质押 wang 过了"""
    #     logger.info("TestRegionDelegate/test_region_delegate")
    #     # 创建节点，然后创建区，然后获得区id
    #     node_name, region_id = setup_create_validator_and_region
    #     #  或者先绑定一个区,如果不需要创建节点只没有传node_name就随机绑定一个没有区的节点
    #     # region_id = setup_create_region 或者先绑定一个区,如果不需要创建节点只创建去，就打开这个
    #     # region_id = "cyp"
    #     # 创建一个用户且将用户 new_kyc，返回用户的地址
    #     # new_kyc_data = dict(region_id=region_id)
    #     user_info = self.test_kyc.test_new_kyc_user(region_id=region_id)
    #     user_addr = user_info
    #     # 管理员给用户转100块
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #     # 用户发起10块钱质押
    #     del_data = dict(from_addr=user_addr, amount=10)
    #     self.test_del.test_delegate(**del_data)
    #     # 查询用户的余额
    #     user_balance = HttpResponse.get_balance_unit(user_addr)
    #     assert user_balance == (100 - 10) * (10 ** 6) - self.base_cfg.fees
    #
    #     # 验证区信息1,区有没有创建成功，2、用户有没有认证在对应的区
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_id == region_info['region']['regionId']
    #     kyc_by_region_list = HttpResponse.get_kyc_by_region(region_id=region_id)
    #     # assert region_info['region_commission']['currentDemandTotalUAC'] == str(Compute.to_u(10 + 1))
    #     assert user_addr in kyc_by_region_list
    #
    #     # 验证节点信息 断言你创建时传入的节点node名，在不在现在的列表里面
    #     validator_node_name_list = HttpResponse.get_validator_node_name_list()
    #     assert node_name in validator_node_name_list
    #
    #     # 验证个人的委托有没有增加
    #     delegation_amount = int(HttpResponse.get_delegate_for_http(user_addr=user_addr)['amount'])
    #     assert delegation_amount == 10 * (10 ** 6)
    #     logger.info('test_region_delegate 结束')
    #
    #     return region_id, user_addr

    # @pytest.skip
    # def test_region_more_delegate(self, setup_create_region):
    #     """多用户质押"""
    #     logger.info("TestRegionDelegate/test_region_more_delegate")
    #     region_id, user_addr1 = self.test_region_delegate(setup_create_region)
    #     logger.info(f'{"setup test_region_delegate finish":*^50s}')
    #
    #     # new_kyc_data = dict(region_id=region_id)
    #     user_info = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)
    #     user_addr2 = user_info['address']
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2, amount=101)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr2, amount=100)
    #     self.test_del.test_delegate(**del_data)
    #
    #     user_balance = HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])
    #     assert user_balance['amount'] == str(Compute.to_u(100 - 10 - self.base_cfg.fees))
    #
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_info['region_commission']['currentDemandTotalUAC'] == str(Compute.to_u(10 + 1 + 10 + 1))
    #     assert user_addr1 and user_addr2 in region_info['delegators']['delegators']
    #     logger.info(f"collect_addr_list:{region_admin_addr, region_id, user_addr1, user_addr2}")
    #     logger.info('结束')
    #     return region_admin_addr, region_id, user_addr1, user_addr2

    def test_two_kyc_user_delegate(self, get_region_id_existing):
        """
        多用户质押的情况 汪 过了，
        """
        # 拿上一个接口结束时的区id和kyc用户地址
        logger.info("TestRegionDelegate/test_more_kyc_user_delegate")
        # region_id, user_addr1 = self.test_region_delegate(setup_create_validator_and_region) # 这个是上面传下的来
        region_id = get_region_id_existing  # 这个是获取已存在的区id,且等下自己新建KYC用户
        # 委托之前先查询一下节点的委托金额，等下后面拿来做断言
        validator_addr = HttpResponse.get_region(region_id=region_id)['region']['operator_address']
        validator_delegate_start = int(
            HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
        logger.info(f"测试开始前，节点委托的金额：{validator_delegate_start}")
        send_amount = 10001
        delegate_amount1 = 10000
        # 本来第一个用户是上面接口传下来的，现在没有传下来，就手动创建第1个用户，区id不变
        user_info1 = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)
        user_addr1 = user_info1
        # 管理员给这个用户转账。
        send_data1 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr1, amount=send_amount)  # 准备转账数据
        self.test_bank.test_send(**send_data1)  # 发起转账，**字典传参
        # 用户发起委托
        del_data = dict(from_addr=user_addr1, amount=delegate_amount1)
        self.test_del.test_delegate(**del_data)  # 字典传参
        # 查询余额
        user1_balances = HttpResponse.get_balance_unit(user_addr=user_addr1)
        logger.info(f"委托结束后用户的余额：{user1_balances}")
        # 断言
        assert user1_balances == Compute.to_u(number=(send_amount - delegate_amount1)) - self.base_cfg.fees

        logger.info(f'{"setup test_region_delegate finish":*^50s}')
        delegate_amount2 = 8000
        # 如果用上面接口传下来的region_id 就直接用
        user_info2 = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)  # 创建随机用户且KYC，会返回user_add
        user_addr2 = user_info2
        # 管理员给这个用户转账。
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2, amount=send_amount)  # 准备转账数据
        self.test_bank.test_send(**send_data)  # 发起转账，**字典传参
        # 用户发起委托
        del_data = dict(from_addr=user_addr2, amount=delegate_amount2)
        self.test_del.test_delegate(**del_data)  # 字典传参
        # 查询用户余额 回来的是int的
        user2_balances = HttpResponse.get_balance_unit(user_addr=user_addr2)
        logger.info(f"委托结束后用户的余额：{user2_balances}")
        # 断言个人的余额有没有减少
        assert user2_balances == Compute.to_u(number=(send_amount - delegate_amount2)) - self.base_cfg.fees
        # 断言区委托有没有增加->就是验证者节点的委托

        validator_delegate_end = int(
            HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
        logger.info(f"测试结束后，节点委托的金额：{validator_delegate_end}")
        # 断言节点委托是否等于用户的委托
        assert validator_delegate_end == validator_delegate_start + Compute.to_u(
            number=delegate_amount1) + Compute.to_u(
            number=delegate_amount2)
        # logger.info(f"collect_addr_list:{region_id, user_addr1, user_addr2}")
        logger.info(f"collect_addr_list:{region_id, user_addr2}")
        logger.info('test_two_kyc_user_delegate 本条用例结束')
        logger.info(f"region_id={region_id}，user_addr2={user_addr2}")
        # return region_id, user_addr1, user_addr2
        logger.info(
            f"user_addr1={user_addr1},user_addr2={user_addr2},validator_addr={validator_addr},"
            f"validator_delegate_end={validator_delegate_end},user1_balances{user1_balances},"
            f"user2_balances{user2_balances},delegate_amount={delegate_amount2}")
        return user_addr1, user_addr2, validator_addr, validator_delegate_end, user1_balances, user2_balances, delegate_amount1, delegate_amount2

    # @pytest.skip
    # def test_region_more_undelegate(self, setup_create_region):
    #     """
    #     多用户减少/退出活期质押
    #     @Desc:
    #         - user1 赎回部分活期质押
    #         - user1 赎回大于额 > 剩余活期质押额  （退出质押,质押有收益会一起返回至余额,金额验证参考收益相关用例）
    #         + expect: user1 无活期质押,还存在KYC赠送质押
    #
    #         - user2 赎回小数值
    #         - user2 赎回小数值超过6位小数,截取字符
    #         + expect: user2 还剩下2uac活期质押,还存在KYC赠送质押
    #
    #         - user2 调用exit退出活期质押
    #         + expect: user2 无活期质押,还存在KYC赠送质押
    #     """
    #     logger.info("TestRegionDelegate/test_region_more_undelegate")
    #     region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate(setup_create_region)
    #     logger.info(f'{"setup test_region_more_delegate finish":*^50s}')
    #
    #     user1_balance = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
    #
    #     logger.info(f'{"- user1 赎回部分活期质押":*^50s}')
    #     amount = 5
    #     del_data = dict(from_addr=user_addr1, amount=amount)
    #     self.test_del.test_undelegate(**del_data)
    #
    #     resp_balance_1 = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_1 == user1_balance + int(Compute.to_u(amount - self.base_cfg.fees))
    #
    #     logger.info(f'{"- user1 赎回大于额 > 剩余活期质押额":*^50s}')
    #     amount2 = 6
    #     del_data = dict(from_addr=user_addr1, amount=amount2)
    #     self.test_del.test_undelegate(**del_data)
    #
    #     # 赎回6acc但是余额只是增加5ac
    #     resp_balance_2 = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_2 == resp_balance_1 + int(Compute.to_u(amount - self.base_cfg.fees))
    #     logger.info(f'{"+ expect: user1 无活期质押,还存在KYC赠送质押":*^50s}')
    #     user1_del_info = HttpResponse.get_delegate(user_addr1)
    #     # ["delegation"]["amountAC"] 代币单位 uac
    #     assert int(user1_del_info['amountAC']) == 0
    #     assert int(user1_del_info["unmovableAmount"]) == Compute.to_u(1)
    #
    #     logger.info("user1结束，user2开始")
    #
    #     user2_balance = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     logger.info(f'{"- user2 赎回小数值":*^50s}')
    #     amount3 = 4.999999
    #     del_data = dict(from_addr=user_addr2, amount=amount3)
    #     self.test_del.test_undelegate(**del_data)
    #
    #     resp_balance_3 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_3 == user2_balance + int(Compute.to_u(amount3 - self.base_cfg.fees))
    #
    #     logger.info(f'{"- user2 赎回小数值超过6位小数,截取字符进行赎回":*^50s}')
    #     amount4 = 4.9999999
    #     del_data = dict(from_addr=user_addr2, amount=amount4)
    #     self.test_del.test_undelegate(**del_data)
    #
    #     resp_balance_4 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_4 == resp_balance_3 + int(Compute.to_u(amount3 - self.base_cfg.fees))
    #
    #     logger.info(f'{"+ expect: user2 还剩下2uac活期质押,还存在KYC赠送质押":*^50s}')
    #     user2_del_info = HttpResponse.get_delegate(user_addr2)
    #     logger.info(f'user2_del_info:{user2_del_info}')
    #     assert int(user2_del_info["amountAC"]) == 2
    #     assert int(user2_del_info["unmovableAmount"]) == Compute.to_u(1)
    #
    #     logger.info(f'{"- user2 调用exit退出活期质押":*^50s}')
    #     del_data = dict(from_addr=user_addr2, delegator_address=user_addr2)
    #     self.test_del.test_exit_delegate(**del_data)
    #
    #     resp_balance_5 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_5 == resp_balance_4 + 2 - Compute.to_u(self.base_cfg.fees)
    #
    #     logger.info(f'{"+ expect: user2 无活期质押,还存在KYC赠送质押":*^50s}')
    #     user2_del_info = HttpResponse.get_delegate(user_addr2)
    #     assert int(user2_del_info["amountAC"]) == 0
    #     assert int(user2_del_info["unmovableAmount"]) == Compute.to_u(1)

    def test_region_more_undelegate_wang(self, get_region_id_existing):
        # 先把用户信息拿出来，这里有两种情况，第一种是上面用例下来只有一个用户，第二是上面用例下来有两个用户
        # 第一種情況，上面下來1個用戶
        user_addr1, user_addr2, validator_addr, vali_delegator, user1_balances_start, user2_balances_start, \
            delegate_amount1, delegate_amount2 = self.test_two_kyc_user_delegate(
            get_region_id_existing=get_region_id_existing)
        logger.info(
            f"打印上一个接口传下来后的值，user1_balances={user1_balances_start},type{type(user1_balances_start)}")
        logger.info(
            f"打印上一个接口传下来后的值，user2_balances={user2_balances_start},type{type(user2_balances_start)}")
        # user1_balances_start = HttpResponse.get_balance_unit(user_addr=user_addr1)
        # 第二种情况，上面下來2個用戶
        # user_addr1,user_addr2, validator_addr, validator_delegator1 = self.test_two_kyc_user_delegate(
        #     get_region_id_existing=get_region_id_existing)
        # user_addr2 = "me1krajder0hxkars23amjrrx0xev3fj6gw69g64l"
        # 由于上面没有下来两个用户，就创建第二个用户

        # 用戶1用例1:減少用户1的委托，減少金額小於已有金額
        user1_undel_amount = 1  # 單位是mec
        start_height = HttpResponse.get_delegate_for_http(user_addr=user_addr1)['startHeight']
        time.sleep(30)
        un_delegate_data = dict(from_addr=user_addr1, amount=user1_undel_amount)  # 解决传参，字典传参
        end_height = int((self.test_del.test_undelegate_kyc(**un_delegate_data))['height'])  # 减少委托
        # 查询user1的金额
        user1_balances_end = HttpResponse.get_balance_unit(user_addr=user_addr1)
        # 手动计算收益，然后断言用户余额
        rewards = Reward.reward_kyc(stake=delegate_amount1, end_height=end_height, start_height=start_height)
        logger.info(f"开始快高为：{start_height},结束快高为：{end_height}，手动计算的收益为：{rewards}")
        assert user1_balances_end == user1_balances_start + Compute.to_u(
            number=user1_undel_amount) + rewards - self.base_cfg.fees
        # 查询区域委托
        vali_delegator2 = int(HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
        # 断言现在的区域委托是否等于之前的-這一次减少的
        logger.info(
            f"开始是的节点委托金额为：{vali_delegator},结束后的节点委托金额为:{vali_delegator2},减少了委托{Compute.to_u(number=user1_undel_amount)}")
        assert vali_delegator2 == vali_delegator - Compute.to_u(number=user1_undel_amount)



        # 用戶1用例二 测试赎回金额大于剩余委托质押金额 无法测试，因为前面断言会报错，他的code不是0
        # 用户2测试用例1 减少金额小于已有金额
        user2_undel_amount = 2
        start_height_user2 = HttpResponse.get_delegate_for_http(user_addr=user_addr2)['startHeight']
        un_delegate_data2 = dict(from_addr=user_addr2, amount=user2_undel_amount)
        end_height_user2 = int((self.test_del.test_undelegate_kyc(**un_delegate_data2))['height'])  # 减少用户2委托
        # # 查询user1的金额
        user2_balances_end = HttpResponse.get_balance_unit(user_addr=user_addr2)
        # # 手动计算收益，然后断言用户余额
        rewards_user2 = Reward.reward_kyc(stake=delegate_amount2, end_height=end_height_user2,
                                          start_height=start_height_user2)
        assert user2_balances_end == user2_balances_start + Compute.to_u(
            number=user2_undel_amount) + rewards_user2 - self.base_cfg.fees
        # # 查询区域委托
        vali_delegator3 = int(HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
        assert vali_delegator3 == vali_delegator2 - Compute.to_u(number=user2_undel_amount)
        # 打扫数据，根据addr删除用户
        self.test_key.test_delete_key(addr=user_addr1)
        self.test_key.test_delete_key(addr=user_addr2)

    # @pytest.skip
    # def test_region_more_exit_delegate(self, setup_create_region):
    #     """
    #     不同角色发起清退活期质押
    #     @Desc:
    #         - user1 superAdmin发起清退
    #         + expect: user1 无活期质押,还剩下kyc赠送质押
    #
    #         - user2 regionAmin发起清退
    #         + expect: user2 无活期质押,还剩下kyc赠送质押
    #
    #         - user2 regionAmin多次发起清退
    #         + expect: 无效清退 error_code: 2097
    #     """
    #     logger.info("TestRegionDelegate/test_region_more_exit_delegate")
    #     region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate(setup_create_region)
    #     logger.info(f'{"setup test_region_more_delegate finish":*^50s}')
    #
    #     user1_balance = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
    #     logger.info(f'{"- user1 superAdmin发起清退":*^50s}')
    #     del_data = dict(from_addr=self.base_cfg.super_addr, delegator_address=user_addr1)
    #     self.test_del.test_exit_delegate(**del_data)
    #
    #     u_delegate_amount = Compute.to_u(10)
    #     resp_balance_1 = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_1 == user1_balance + u_delegate_amount
    #     logger.info(f'{"+ expect: user1 无活期质押,还剩下kyc赠送质押":*^50s}')
    #     user1_del_info = HttpResponse.get_delegate(user_addr1)
    #     # ["delegation"]["amountAC"] 代币单位 uac
    #     assert int(user1_del_info["amountAC"]) == 0
    #     assert int(user1_del_info["unmovableAmount"]) == Compute.to_u(1)
    #
    #     user2_balance = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     logger.info(f'{"- user2 regionAmin发起清退":*^50s}')
    #     del_data = dict(from_addr=region_admin_addr, delegator_address=user_addr2)
    #     self.test_del.test_exit_delegate(**del_data)
    #
    #     resp_balance_2 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance_2 == user2_balance + u_delegate_amount
    #
    #     logger.info(f'{"+ expect: user2 无活期质押,还剩下kyc赠送质押":*^50s}')
    #     user2_del_info = HttpResponse.get_delegate(user_addr2)
    #     assert int(user2_del_info["amountAC"]) == 0
    #     assert int(user2_del_info["unmovableAmount"]) == Compute.to_u(1)
    #
    #     user2_balance2 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     logger.info(f'{"- user2 regionAmin多次发起清退":*^50s}')
    #     del_data = dict(from_addr=region_admin_addr, delegator_address=user_addr2)
    #     logger.info(f'{"+ expect: 无效清退 error_code: 2097"}')
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_exit_delegate(**del_data)
    #     assert "'code': 2097" in str(ex.value)
    #
    #     resp_balance2 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
    #     assert resp_balance2 == user2_balance2

    # @pytest.skip
    # def test_delegate_fixed(self, setup_create_region):
    #     """
    #     活期内周期质押
    #     :param setup_create_region:
    #     :Desc
    #         - user1 申请kyc,发送100 coin
    #         - user1 活期质押内周期质押 10 coin + fees
    #         + expect: user1 余额 100 coin - 10 coin - fees
    #     """
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info["address"]
    #     logger.info("TestRegionDelegate/test_delegate_fixed")
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info["address"]
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
    #     self.test_del.test_delegate_fixed(**del_data)
    #
    #     user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #
    #     assert user_addr_balance == Compute.to_u(100 - 10 - self.base_cfg.fees)
    #     delegate_info = HttpResponse.get_delegate(user_addr)
    #     assert delegate_info["fixedAmount"] == str(Compute.to_u(10))
    #     x = decimal.Decimal(10) / decimal.Decimal(400) / decimal.Decimal(self.base_cfg.region_as)
    #     assert delegate_info["fixedASRate"] == '{:.18f}'.format(x)
    #
    #     resp = HttpResponse.show_fixed_delegation(user_addr)
    #     assert len(resp['items']) == 1
    #     assert resp['items'][0]['amount']['amount'] == str(Compute.to_u(10))
    #
    #     # Compute revenue over the period
    #     interests = set([i['amount'] for i in resp['items'][0]['interests']])
    #     assert len(interests) == 1
    #     y = Compute.interest(amount=Compute.to_u(10), period=1, rate=self.base_cfg.annual_rate[1])
    #     assert int(interests.pop()) == y
    #
    #     return region_admin_addr, region_id, region_name, user_addr

    # @pytest.skip
    # def test_undelegate_fixed(self, setup_create_region):
    #     """提取活期内周期质押"""
    #     logger.info("TestRegionDelegate/test_undelegate_fixed")
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info["address"]
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info["address"]
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
    #     self.test_del.test_delegate_fixed(**del_data)
    #
    #     fixed_delegate_info = HttpResponse.show_fixed_delegation(user_addr)
    #     fixed_delegation_id = fixed_delegate_info['items'][0]['id']
    #     undelegate_fixed_data = dict(from_addr=user_addr, fixed_delegation_id=fixed_delegation_id)
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_undelegate_fixed(**undelegate_fixed_data)
    #     assert "'code': 2161" in str(ex.value)  # fixed delegation not reach deadline
    #
    #     time.sleep(30)  # 30s is equal to one month
    #     self.test_del.test_undelegate_fixed(**undelegate_fixed_data)

    # @pytest.skip
    # def test_delegate_infinite(self, setup_create_region):
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info["address"]
    #     logger.info("TestRegionDelegate/test_delegate_infinite")
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info["address"]
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=10)
    #     self.test_del.test_delegate_infinite(**del_data)
    #
    #     user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #     assert user_addr_balance == Compute.to_u(100 - 10 - self.base_cfg.fees)
    #     delegate_info = HttpResponse.get_delegate(user_addr)
    #     # 包含new-kyc的 1coin
    #     assert delegate_info["unmovableAmount"] == str(Compute.to_u(10 + 1))
    #     x = decimal.Decimal(11) / decimal.Decimal(400) / decimal.Decimal(self.base_cfg.region_as)
    #     assert delegate_info["unmovableASRate"] == '{:.18f}'.format(x)
    #
    #     return user_addr, region_admin_addr, region_id

    # @pytest.skip
    # def test_undelegate_infinite(self, setup_create_region):
    #     """
    #     测试提取永久委托
    #         - 未修改区属性,不可提取
    #         - 修改区属性,可提取
    #             - 区管理员不可修改
    #             - 超级管理员可修改
    #     """
    #     user_addr, region_admin_addr, region_id = self.test_delegate_infinite(setup_create_region)
    #     logger.info("TestRegionDelegate/test_undelegate_infinite")
    #     del_data = dict(from_addr=user_addr, amount=5)
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_undelegate_infinite(**del_data)
    #     assert "'code': 2098" in str(ex.value)
    #
    #     # region_admin update isUndelegate, The tx can be successfully but not modifying the attribute value
    #     region_data = dict(region_id=region_id, from_addr=region_admin_addr, isUndelegate=True)
    #     self.test_region.test_update_region(**region_data)
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_info['region']['isUndelegate'] is False
    #
    #     # superadmin update isUndelegate
    #     region_data = dict(region_id=region_id, from_addr=self.base_cfg.super_addr, isUndelegate=True)
    #     self.test_region.test_update_region(**region_data)
    #
    #     # query region info
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_info['region']['isUndelegate'] is True
    #
    #     # query user_addr balance
    #     start_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #     self.test_del.test_undelegate_infinite(**del_data)
    #     end_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #     assert end_user_addr_balance == start_user_addr_balance + Compute.to_u(5 - self.base_cfg.fees)
    #
    #     # update isUndelegate to False
    #     region_data = dict(region_id=region_id, from_addr=self.base_cfg.super_addr, isUndelegate=False)
    #     self.test_region.test_update_region(**region_data)
    #
    #     # query region info
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_info['region']['isUndelegate'] is False
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_undelegate_infinite(**del_data)
    #     assert "'code': 2098" in str(ex.value)

    # @pytest.skip
    # def test_undelegate_infinite_excess(self, setup_create_region):
    #     """活期永久质押 超额提取"""
    #     user_addr, region_admin_addr, region_id = self.test_delegate_infinite(setup_create_region)
    #     logger.info("TestRegionDelegate/test_undelegate_infinite_excess")
    #
    #     # isUndelegate is True
    #     region_data = dict(region_id=f"{region_id}", from_addr=self.base_cfg.super_addr, isUndelegate=True)
    #     self.test_region.test_update_region(**region_data)
    #     region_info = HttpResponse.get_region(region_id)
    #     assert region_info['region']['isUndelegate'] is True
    #
    #     # 提取所有永久质押金额 -> 返回永久质押本金+活期所得收益
    #     start_user_addr_balance2 = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #
    #     # 查询活期收益 和 提取活期 !应该保证其在同一个区块内,目前代码无法保证
    #     interest_amount = float(HttpResponse.get_delegate(user_addr)['interestAmount'])
    #     logger.info(f"interest_amount: {interest_amount}")
    #     x = math.floor(interest_amount) if interest_amount >= 1 else 0
    #     del_data = dict(from_addr=user_addr, amount=100)
    #     self.test_del.test_undelegate_infinite(**del_data)
    #
    #     end_user_addr_balance2 = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #     # 剩余8本金 - 1手续费 + 活期收益(手动永久质押+kyc收益)
    #     assert end_user_addr_balance2 == start_user_addr_balance2 + Compute.to_u(10 - self.base_cfg.fees) + x

    # @pytest.skip
    # def test_withdraw(self, setup_create_region):
    #     """活期收益提取"""
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info["address"]
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info["address"]
    #
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
    #     self.test_bank.test_send(**send_data)
    #
    #     # 正常活期委托 10 token
    #     del_data = dict(from_addr=user_addr, amount=10)
    #     self.test_del.test_delegate(**del_data)
    #
    #     # 永久活期委托 10 coin
    #     self.test_del.test_delegate_infinite(**del_data)
    #
    #     # 活期周期委托 10 coin
    #     del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
    #     self.test_del.test_delegate_fixed(**del_data)
    #
    #     start_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #     assert start_user_addr_balance == Compute.to_u(100 - (10 * 3) - (self.base_cfg.fees * 3))
    #
    #     time.sleep(30)
    #
    #     interest_amount = float(HttpResponse.get_delegate(user_addr)['interestAmount'])
    #     logger.info(f"interest_amount: {interest_amount}")
    #     x = math.floor(interest_amount) if interest_amount >= 1 else 0
    #     # 提取活期收益
    #     self.test_del.test_withdraw(**dict(addr=user_addr))
    #
    #     end_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
    #     assert end_user_addr_balance == start_user_addr_balance - Compute.to_u(self.base_cfg.fees) + x

    # @pytest.skip
    # def test_exceed_delegate_limit(self, setup_create_region):
    #     region_admin_info, region_id, region_name = setup_create_region
    #     region_admin_addr = region_admin_info["address"]
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info["address"]
    #
    #     gas_limit = (200000 * 210)  # tx 1/10000 fee included
    #     fees = Compute.to_u(gas_limit * 5, reverse=True)
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
    #                      amount=self.base_cfg.max_delegate * 2, gas=gas_limit, fees=fees)
    #     self.test_bank.test_send(**send_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=self.base_cfg.max_delegate)
    #
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_delegate(**del_data)
    #     assert "'code': 2063" in str(ex.value)  # Amount exceeds limit,max delegate amount:1000000ac
    #
    #     del_data = dict(from_addr=user_addr, amount=self.base_cfg.max_delegate - 1)
    #     self.test_del.test_delegate(**del_data)
    #
    #     del_data = dict(from_addr=user_addr, amount=1)
    #     with pytest.raises(AssertionError) as ex:
    #         self.test_del.test_delegate_infinite(**del_data)
    #     assert "'code': 2063" in str(ex.value)  # Amount exceeds limit,max delegate amount:1000000ac
# if __name__ == '__main__':
#     print("2")
