# -*- coding: utf-8 -*-
import decimal
import math
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute
from tools.parse_response import HttpResponse


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionDelegate(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    base_cfg = test_bank.tx

    def test_region_delegate(self, setup_create_region):
        """测试新创建区域并质押"""
        logger.info("TestRegionDelegate/test_region_delegate")
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info['address']

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info['address']

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate(**del_data)

        user_balance = HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])
        assert user_balance['amount'] == str(Compute.to_u(100 - 10 - self.base_cfg.fees))

        # 验证区信息
        region_info = HttpResponse.get_region(region_id)
        assert region_info['region_commission']['currentDemandTotalUAC'] == str(Compute.to_u(10 + 1))
        assert user_addr in region_info['delegators']['delegators']

        return region_admin_addr, region_id, user_addr

    def test_region_more_delegate(self, setup_create_region):
        """多用户质押"""
        logger.info("TestRegionDelegate/test_region_more_delegate")
        region_admin_addr, region_id, user_addr1 = self.test_region_delegate(setup_create_region)
        logger.info(f'{"setup test_region_delegate finish":*^50s}')

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr2 = user_info['address']

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2, amount=100)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr2, amount=10)
        self.test_del.test_delegate(**del_data)

        user_balance = HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])
        assert user_balance['amount'] == str(Compute.to_u(100 - 10 - self.base_cfg.fees))

        region_info = HttpResponse.get_region(region_id)
        assert region_info['region_commission']['currentDemandTotalUAC'] == str(Compute.to_u(10 + 1 + 10 + 1))
        assert user_addr1 and user_addr2 in region_info['delegators']['delegators']
        logger.info(f"collect_addr_list:{region_admin_addr, region_id, user_addr1, user_addr2}")
        return region_admin_addr, region_id, user_addr1, user_addr2

    def test_region_more_undelegate(self, setup_create_region):
        """
        多用户减少/退出活期质押
        @Desc:
            - user1 赎回部分活期质押
            - user1 赎回大于额 > 剩余活期质押额  （退出质押,质押有收益会一起返回至余额,金额验证参考收益相关用例）
            + expect: user1 无活期质押,还存在KYC赠送质押

            - user2 赎回小数值
            - user2 赎回小数值超过6位小数,截取字符
            + expect: user2 还剩下2uac活期质押,还存在KYC赠送质押

            - user2 调用exit退出活期质押
            + expect: user2 无活期质押,还存在KYC赠送质押
        """
        logger.info("TestRegionDelegate/test_region_more_undelegate")
        region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate(setup_create_region)
        logger.info(f'{"setup test_region_more_delegate finish":*^50s}')

        user1_balance = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])

        logger.info(f'{"- user1 赎回部分活期质押":*^50s}')
        amount = 5
        del_data = dict(from_addr=user_addr1, amount=amount)
        self.test_del.test_undelegate(**del_data)

        resp_balance_1 = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_1 == user1_balance + int(Compute.to_u(amount - self.base_cfg.fees))

        logger.info(f'{"- user1 赎回大于额 > 剩余活期质押额":*^50s}')
        amount2 = 6
        del_data = dict(from_addr=user_addr1, amount=amount2)
        self.test_del.test_undelegate(**del_data)

        # 赎回6acc但是余额只是增加5ac
        resp_balance_2 = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_2 == resp_balance_1 + int(Compute.to_u(amount - self.base_cfg.fees))
        logger.info(f'{"+ expect: user1 无活期质押,还存在KYC赠送质押":*^50s}')
        user1_del_info = HttpResponse.get_delegate(user_addr1)
        # ["delegation"]["amountAC"] 代币单位 uac
        assert int(user1_del_info['amountAC']) == 0
        assert int(user1_del_info["unmovableAmount"]) == Compute.to_u(1)

        user2_balance = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        logger.info(f'{"- user2 赎回小数值":*^50s}')
        amount3 = 4.999999
        del_data = dict(from_addr=user_addr2, amount=amount3)
        self.test_del.test_undelegate(**del_data)

        resp_balance_3 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_3 == user2_balance + int(Compute.to_u(amount3 - self.base_cfg.fees))

        logger.info(f'{"- user2 赎回小数值超过6位小数,截取字符进行赎回":*^50s}')
        amount4 = 4.9999999
        del_data = dict(from_addr=user_addr2, amount=amount4)
        self.test_del.test_undelegate(**del_data)

        resp_balance_4 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_4 == resp_balance_3 + int(Compute.to_u(amount3 - self.base_cfg.fees))

        logger.info(f'{"+ expect: user2 还剩下2uac活期质押,还存在KYC赠送质押":*^50s}')
        user2_del_info = HttpResponse.get_delegate(user_addr2)
        logger.info(f'user2_del_info:{user2_del_info}')
        assert int(user2_del_info["amountAC"]) == 2
        assert int(user2_del_info["unmovableAmount"]) == Compute.to_u(1)

        logger.info(f'{"- user2 调用exit退出活期质押":*^50s}')
        del_data = dict(from_addr=user_addr2, delegator_address=user_addr2)
        self.test_del.test_exit_delegate(**del_data)

        resp_balance_5 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_5 == resp_balance_4 + 2 - Compute.to_u(self.base_cfg.fees)

        logger.info(f'{"+ expect: user2 无活期质押,还存在KYC赠送质押":*^50s}')
        user2_del_info = HttpResponse.get_delegate(user_addr2)
        assert int(user2_del_info["amountAC"]) == 0
        assert int(user2_del_info["unmovableAmount"]) == Compute.to_u(1)

    def test_region_more_exit_delegate(self, setup_create_region):
        """
        不同角色发起清退活期质押
        @Desc:
            - user1 superAdmin发起清退
            + expect: user1 无活期质押,还剩下kyc赠送质押

            - user2 regionAmin发起清退
            + expect: user2 无活期质押,还剩下kyc赠送质押

            - user2 regionAmin多次发起清退
            + expect: 无效清退 error_code: 2097
        """
        logger.info("TestRegionDelegate/test_region_more_exit_delegate")
        region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate(setup_create_region)
        logger.info(f'{"setup test_region_more_delegate finish":*^50s}')

        user1_balance = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
        logger.info(f'{"- user1 superAdmin发起清退":*^50s}')
        del_data = dict(from_addr=self.base_cfg.super_addr, delegator_address=user_addr1)
        self.test_del.test_exit_delegate(**del_data)

        u_delegate_amount = Compute.to_u(10)
        resp_balance_1 = int(HttpResponse.get_balance_unit(user_addr1, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_1 == user1_balance + u_delegate_amount
        logger.info(f'{"+ expect: user1 无活期质押,还剩下kyc赠送质押":*^50s}')
        user1_del_info = HttpResponse.get_delegate(user_addr1)
        # ["delegation"]["amountAC"] 代币单位 uac
        assert int(user1_del_info["amountAC"]) == 0
        assert int(user1_del_info["unmovableAmount"]) == Compute.to_u(1)

        user2_balance = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        logger.info(f'{"- user2 regionAmin发起清退":*^50s}')
        del_data = dict(from_addr=region_admin_addr, delegator_address=user_addr2)
        self.test_del.test_exit_delegate(**del_data)

        resp_balance_2 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance_2 == user2_balance + u_delegate_amount

        logger.info(f'{"+ expect: user2 无活期质押,还剩下kyc赠送质押":*^50s}')
        user2_del_info = HttpResponse.get_delegate(user_addr2)
        assert int(user2_del_info["amountAC"]) == 0
        assert int(user2_del_info["unmovableAmount"]) == Compute.to_u(1)

        user2_balance2 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        logger.info(f'{"- user2 regionAmin多次发起清退":*^50s}')
        del_data = dict(from_addr=region_admin_addr, delegator_address=user_addr2)
        logger.info(f'{"+ expect: 无效清退 error_code: 2097"}')
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_exit_delegate(**del_data)
        assert "'code': 2097" in str(ex.value)

        resp_balance2 = int(HttpResponse.get_balance_unit(user_addr2, self.base_cfg.coin['uc'])['amount'])
        assert resp_balance2 == user2_balance2

    def test_delegate_fixed(self, setup_create_region):
        """
        活期内周期质押
        :param setup_create_region:
        :Desc
            - user1 申请kyc,发送100 coin
            - user1 活期质押内周期质押 10 coin + fees
            + expect: user1 余额 100 coin - 10 coin - fees
        """
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info["address"]
        logger.info("TestRegionDelegate/test_delegate_fixed")
        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info["address"]

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
        self.test_del.test_delegate_fixed(**del_data)

        user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])

        assert user_addr_balance == Compute.to_u(100 - 10 - self.base_cfg.fees)
        delegate_info = HttpResponse.get_delegate(user_addr)
        assert delegate_info["fixedAmount"] == str(Compute.to_u(10))
        x = decimal.Decimal(10) / decimal.Decimal(400) / decimal.Decimal(self.base_cfg.region_as)
        assert delegate_info["fixedASRate"] == '{:.18f}'.format(x)

        resp = HttpResponse.show_fixed_delegation(user_addr)
        assert len(resp['items']) == 1
        assert resp['items'][0]['amount']['amount'] == str(Compute.to_u(10))

        # Compute revenue over the period
        interests = set([i['amount'] for i in resp['items'][0]['interests']])
        assert len(interests) == 1
        y = Compute.interest(amount=Compute.to_u(10), period=1, rate=self.base_cfg.annual_rate[1])
        assert int(interests.pop()) == y

        return region_admin_addr, region_id, region_name, user_addr

    def test_undelegate_fixed(self, setup_create_region):
        """提取活期内周期质押"""
        logger.info("TestRegionDelegate/test_undelegate_fixed")
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info["address"]

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info["address"]

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
        self.test_del.test_delegate_fixed(**del_data)

        fixed_delegate_info = HttpResponse.show_fixed_delegation(user_addr)
        fixed_delegation_id = fixed_delegate_info['items'][0]['id']
        undelegate_fixed_data = dict(from_addr=user_addr, fixed_delegation_id=fixed_delegation_id)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_undelegate_fixed(**undelegate_fixed_data)
        assert "'code': 2161" in str(ex.value)  # fixed delegation not reach deadline

        time.sleep(30)  # 30s is equal to one month
        self.test_del.test_undelegate_fixed(**undelegate_fixed_data)

    def test_delegate_infinite(self, setup_create_region):
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info["address"]
        logger.info("TestRegionDelegate/test_delegate_infinite")
        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info["address"]

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate_infinite(**del_data)

        user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        assert user_addr_balance == Compute.to_u(100 - 10 - self.base_cfg.fees)
        delegate_info = HttpResponse.get_delegate(user_addr)
        # 包含new-kyc的 1coin
        assert delegate_info["unmovableAmount"] == str(Compute.to_u(10 + 1))
        x = decimal.Decimal(11) / decimal.Decimal(400) / decimal.Decimal(self.base_cfg.region_as)
        assert delegate_info["unmovableASRate"] == '{:.18f}'.format(x)

        return user_addr, region_admin_addr, region_id

    def test_undelegate_infinite(self, setup_create_region):
        """
        测试提取永久委托
            - 未修改区属性,不可提取
            - 修改区属性,可提取
                - 区管理员不可修改
                - 超级管理员可修改
        """
        user_addr, region_admin_addr, region_id = self.test_delegate_infinite(setup_create_region)
        logger.info("TestRegionDelegate/test_undelegate_infinite")
        del_data = dict(from_addr=user_addr, amount=5)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_undelegate_infinite(**del_data)
        assert "'code': 2098" in str(ex.value)

        # region_admin update region info todo: code is not 0
        region_data = dict(region_id=region_id, from_addr=region_admin_addr, isUndelegate=True)
        self.test_region.test_update_region(**region_data)
        region_info = HttpResponse.get_region(region_id)
        assert region_info['region']['isUndelegate'] is False

        # superadmin update region info
        region_data = dict(region_id=region_id, from_addr=self.base_cfg.super_addr, isUndelegate=True)
        self.test_region.test_update_region(**region_data)

        # query region info
        region_info = HttpResponse.get_region(region_id)
        assert region_info['region']['isUndelegate'] is True

        # query user_addr balance
        start_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        self.test_del.test_undelegate_infinite(**del_data)
        end_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        assert end_user_addr_balance == start_user_addr_balance + Compute.to_u(5 - self.base_cfg.fees)

        # update isUndelegate to False
        region_data = dict(region_id=region_id, from_addr=self.base_cfg.super_addr, isUndelegate=False)
        self.test_region.test_update_region(**region_data)

        # query region info
        region_info = HttpResponse.get_region(region_id)
        assert region_info['region']['isUndelegate'] is False
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_undelegate_infinite(**del_data)
        assert "'code': 2098" in str(ex.value)

    def test_undelegate_infinite_excess(self, setup_create_region):
        """活期永久质押 超额提取"""
        user_addr, region_admin_addr, region_id = self.test_delegate_infinite(setup_create_region)
        logger.info("TestRegionDelegate/test_undelegate_infinite_excess")

        # isUndelegate is True
        region_data = dict(region_id=f"{region_id}", from_addr=self.base_cfg.super_addr, isUndelegate=True)
        self.test_region.test_update_region(**region_data)
        region_info = HttpResponse.get_region(region_id)
        assert region_info['region']['isUndelegate'] is True

        # 提取所有永久质押金额 -> 返回永久质押本金+活期所得收益
        start_user_addr_balance2 = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])

        # 查询活期收益 和 提取活期 !应该保证其在同一个区块内,目前代码无法保证
        interest_amount = float(HttpResponse.get_delegate(user_addr)['interestAmount'])
        logger.info(f"interest_amount: {interest_amount}")
        x = math.floor(interest_amount) if interest_amount >= 1 else 0
        del_data = dict(from_addr=user_addr, amount=100)
        self.test_del.test_undelegate_infinite(**del_data)

        end_user_addr_balance2 = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        # 剩余8本金 - 1手续费 + 活期收益(手动永久质押+kyc收益)
        assert end_user_addr_balance2 == start_user_addr_balance2 + Compute.to_u(10 - self.base_cfg.fees) + x

    def test_withdraw(self, setup_create_region):
        """活期收益提取"""
        region_admin_info, region_id, region_name = setup_create_region
        region_admin_addr = region_admin_info["address"]

        new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
        user_addr = user_info["address"]

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=100)
        self.test_bank.test_send(**send_data)

        # 正常活期委托 10 token
        del_data = dict(from_addr=user_addr, amount=10)
        self.test_del.test_delegate(**del_data)

        # 永久活期委托 10 coin
        self.test_del.test_delegate_infinite(**del_data)

        # 活期周期委托 10 coin
        del_data = dict(from_addr=user_addr, amount=10, term=self.base_cfg.delegate_term[1])
        self.test_del.test_delegate_fixed(**del_data)

        start_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        assert start_user_addr_balance == Compute.to_u(100 - (10 * 3) - (self.base_cfg.fees * 3))

        time.sleep(30)

        interest_amount = float(HttpResponse.get_delegate(user_addr)['interestAmount'])
        logger.info(f"interest_amount: {interest_amount}")
        x = math.floor(interest_amount) if interest_amount >= 1 else 0
        # 提取活期收益
        self.test_del.test_withdraw(**dict(addr=user_addr))

        end_user_addr_balance = int(HttpResponse.get_balance_unit(user_addr, self.base_cfg.coin['uc'])["amount"])
        assert end_user_addr_balance == start_user_addr_balance - Compute.to_u(self.base_cfg.fees) + x