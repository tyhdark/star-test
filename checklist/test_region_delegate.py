# -*- coding: utf-8 -*-
import decimal
import math
import time

import pytest
from loguru import logger

from case import package
from config import chain
from tools import calculate, handle_query


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionDelegate(object):
    test_region = package.RegionPackage()
    test_del = package.DelegatePackage()
    test_kyc = package.KycPackage()
    test_bank = package.BankPackage()
    handle_q = handle_query.HandleQuery()

    def test_region_delegate(self):
        """测试新创建区域并质押"""
        logger.info("TestRegionDelegate/test_region_delegate")
        region_admin_addr, region_id, _ = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)

        # 验证用户余额
        user_balance = self.handle_q.get_balance(user_addr, chain.coin['uc'])
        assert user_balance['amount'] == str(calculate.subtraction(100, 10, 1))

        # 验证区信息
        region_info = self.handle_q.get_region(region_id)
        assert region_info['region_commission']['currentDemandTotalUAC'] == str(calculate.add([10, 1]))
        assert user_addr in region_info['delegators']['delegators']

        return region_admin_addr, region_id, user_addr

    def test_region_more_delegate(self):
        """多用户质押"""
        logger.info("TestRegionDelegate/test_region_more_delegate")
        region_admin_addr, region_id, user_addr1 = self.test_region_delegate()
        logger.info(f'{"setup test_region_delegate finish":*^50s}')

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr2 = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr2}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)

        user_balance = self.handle_q.get_balance(user_addr2, chain.coin['uc'])
        assert user_balance['amount'] == str(calculate.subtraction(100, 10, 1))

        region_info = self.handle_q.get_region(region_id)
        assert region_info['region_commission']['currentDemandTotalUAC'] == str(calculate.add([10, 1, 10, 1]))
        assert user_addr1 and user_addr2 in region_info['delegators']['delegators']
        logger.info(f"collect_addr_list:{region_admin_addr, region_id, user_addr1, user_addr2}")
        return region_admin_addr, region_id, user_addr1, user_addr2

    def test_region_more_undelegate(self):
        """
        多用户减少/退出活期质押
        @Desc:
            - user1 赎回部分活期质押
            - user1 赎回大于额 > 剩余活期质押额  （退出质押,质押有收益会一起返回至余额,金额验证参考收益相关用例）
            + expect: user1 无活期质押,还存在KYC赠送质押

            - user2 赎回小数值
            - user2 赎回小数值超过6位小数,截取字符
            + expect: user2 还剩下2usrc活期质押,还存在KYC赠送质押

            - user2 调用exit退出活期质押
            + expect: user2 无活期质押,还存在KYC赠送质押
        """
        logger.info("TestRegionDelegate/test_region_more_undelegate")
        region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate()
        logger.info(f'{"setup test_region_more_delegate finish":*^50s}')

        user1_balance = int(self.handle_q.get_balance(user_addr1, chain.coin['uc'])['amount'])

        logger.info(f'{"- user1 赎回部分活期质押":*^50s}')
        amount = 5
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr1}", amount=amount, fees="1")
        self.test_del.test_undelegate(del_data)

        u_amount = calculate.to_usrc(amount)
        u_fees = calculate.to_usrc(1)
        resp_balance_1 = int(self.handle_q.get_balance(user_addr1, chain.coin['uc'])['amount'])
        assert resp_balance_1 == user1_balance + u_amount - u_fees

        logger.info(f'{"- user1 赎回大于额 > 剩余活期质押额":*^50s}')
        amount2 = 6
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr1}", amount=amount2, fees="1")
        self.test_del.test_undelegate(del_data)

        # u_amount == 5000000usrc  赎回6src但是余额只是增加5src
        resp_balance_2 = int(self.handle_q.get_balance(user_addr1, chain.coin['uc'])['amount'])
        assert resp_balance_2 == resp_balance_1 + u_amount - u_fees
        time.sleep(2)
        logger.info(f'{"+ expect: user1 无活期质押,还存在KYC赠送质押":*^50s}')
        user1_del_info = self.handle_q.get_delegate(user_addr1)
        # ["delegation"]["amountAC"] 代币单位 usrc
        assert user1_del_info['delegation']['amountAC'] == "0"
        assert user1_del_info["delegation"]["unmovableAmount"] == "1000000"

        user2_balance = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        logger.info(f'{"- user2 赎回小数值":*^50s}')
        amount3 = 4.999999
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", amount=amount3, fees="1")
        self.test_del.test_undelegate(del_data)

        u_amount3 = calculate.to_usrc(amount3)
        resp_balance_3 = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        assert resp_balance_3 == user2_balance + u_amount3 - u_fees

        logger.info(f'{"- user2 赎回小数值超过6位小数,截取字符":*^50s}')
        amount4 = 4.9999999
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", amount=amount4, fees="1")
        self.test_del.test_undelegate(del_data)

        resp_balance_4 = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        assert resp_balance_4 == resp_balance_3 + u_amount3 - u_fees

        logger.info(f'{"+ expect: user2 还剩下2usrc活期质押,还存在KYC赠送质押":*^50s}')
        time.sleep(2)
        user2_del_info = self.handle_q.get_delegate(user_addr2)
        logger.info(f'user2_del_info:{user2_del_info}')
        assert user2_del_info["delegation"]["amountAC"] == "2"
        assert user2_del_info["delegation"]["unmovableAmount"] == "1000000"

        logger.info(f'{"- user2 调用exit退出活期质押":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr2}",
                        from_addr=f"{user_addr2}", fees="1")
        self.test_del.test_exit_delegate(del_data)

        resp_balance_5 = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        assert resp_balance_5 == resp_balance_4 + 2 - u_fees

        logger.info(f'{"+ expect: user2 无活期质押,还存在KYC赠送质押":*^50s}')
        time.sleep(2)
        user2_del_info = self.handle_q.get_delegate(user_addr2)
        assert user2_del_info["delegation"]["amountAC"] == "0"
        assert user2_del_info["delegation"]["unmovableAmount"] == "1000000"

    def test_region_more_exit_delegate(self):
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
        region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate()
        logger.info(f'{"setup test_region_more_delegate finish":*^50s}')

        user1_balance = int(self.handle_q.get_balance(user_addr1, chain.coin['uc'])['amount'])
        logger.info(f'{"- user1 superAdmin发起清退":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr1}",
                        from_addr=f"{chain.super_addr}", fees="1")
        self.test_del.test_exit_delegate(del_data)

        u_delegate_amount = calculate.to_usrc(10)
        resp_balance_1 = int(self.handle_q.get_balance(user_addr1, chain.coin['uc'])['amount'])
        assert resp_balance_1 == user1_balance + u_delegate_amount

        logger.info(f'{"+ expect: user1 无活期质押,还剩下kyc赠送质押":*^50s}')
        time.sleep(2)
        user1_del_info = self.handle_q.get_delegate(user_addr1)
        # ["delegation"]["amountAC"] 代币单位 usrc
        assert user1_del_info["delegation"]["amountAC"] == "0"
        assert user1_del_info["delegation"]["unmovableAmount"] == "1000000"

        user2_balance = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        logger.info(f'{"- user2 regionAmin发起清退":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr2}",
                        from_addr=f"{region_admin_addr}", fees="1")
        self.test_del.test_exit_delegate(del_data)

        resp_balance_2 = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        assert resp_balance_2 == user2_balance + u_delegate_amount

        logger.info(f'{"+ expect: user2 无活期质押,还剩下kyc赠送质押":*^50s}')
        time.sleep(2)
        user2_del_info = self.handle_q.get_delegate(user_addr2)
        assert user2_del_info["delegation"]["amountAC"] == "0"
        assert user2_del_info["delegation"]["unmovableAmount"] == "1000000"

        user2_balance2 = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        logger.info(f'{"- user2 regionAmin多次发起清退":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr2}",
                        from_addr=f"{region_admin_addr}", fees="1")

        logger.info(f'{"+ expect: 无效清退 error_code: 2097"}')
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_exit_delegate(del_data)
        assert str(ex.value) == 'error_code: 2097 != 0'

        resp_balance2 = int(self.handle_q.get_balance(user_addr2, chain.coin['uc'])['amount'])
        assert resp_balance2 == user2_balance2

    def test_delegate_fixed(self, setup_create_region):
        """
        活期内周期质押
        :param setup_create_region:
        :Desc
            - user1 申请kyc,发送100 coin
            - user1 活期质押内周期质押 10 coin + fees 1 coin
            + expect: user1 余额 89 coin
        """
        region_admin_addr, region_id, region_name, _ = setup_create_region
        logger.info("TestRegionDelegate/test_delegate_fixed")
        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[1], fees=1)
        self.test_del.test_delegate_fixed(del_data)

        user_addr_balance = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])

        assert user_addr_balance == calculate.to_usrc(100) - calculate.to_usrc(10) - calculate.to_usrc(1)
        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        assert delegate_info["fixedAmount"] == str(calculate.to_usrc(10))
        x = decimal.Decimal(10) / decimal.Decimal(400) / decimal.Decimal(chain.REGION_AS)
        assert delegate_info["fixedASRate"] == '{:.18f}'.format(x)

        resp = self.handle_q.q.staking.show_fixed_delegation(user_addr)
        assert len(resp['items']) == 1
        assert resp['items'][0]['amount']['amount'] == str(calculate.to_usrc(10))

        # Calculate revenue over the period
        interests = set([i['amount'] for i in resp['items'][0]['interests']])
        assert len(interests) == 1
        y = chain.annualRate[1] * 1 / 12 * calculate.to_usrc(10)
        assert int(interests.pop()) == y

        return region_admin_addr, region_id, region_name, user_addr

    def test_undelegate_fixed(self, setup_create_region):
        """提取活期内周期质押"""
        logger.info("TestRegionDelegate/test_undelegate_fixed")
        region_admin_addr, region_id, region_name, _ = setup_create_region

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[1], fees=1)
        self.test_del.test_delegate_fixed(del_data)

        fixed_delegate_info = self.handle_q.q.staking.show_fixed_delegation(user_addr)
        fixed_delegation_id = fixed_delegate_info['items'][0]['id']
        undelegate_fixed_data = dict(from_addr=user_addr, fixed_delegation_id=fixed_delegation_id, fees=1)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_undelegate_fixed(undelegate_fixed_data)
        assert str(ex.value) == 'error_code: 2161 != 0'  # fixed delegation not reach deadline

        time.sleep(30)  # 30s is equal to one month
        self.test_del.test_undelegate_fixed(undelegate_fixed_data)

    def test_delegate_infinite(self, setup_create_region):
        region_admin_addr, region_id, region_name, _ = setup_create_region
        logger.info("TestRegionDelegate/test_delegate_infinite")
        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_user_addr=f"{user_addr}", amount=10, fees=1)
        self.test_del.test_delegate_infinite(del_data)

        user_addr_balance = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])

        assert user_addr_balance == calculate.to_usrc(100) - calculate.to_usrc(10) - calculate.to_usrc(1)
        delegate_info = self.handle_q.get_delegate(user_addr)['delegation']
        # 包含new-kyc的 1coin
        assert delegate_info["unmovableAmount"] == str(calculate.to_usrc(10) + calculate.to_usrc(1))
        x = decimal.Decimal(11) / decimal.Decimal(400) / decimal.Decimal(chain.REGION_AS)
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
        del_data = dict(region_user_addr=user_addr, amount=2, fees=1)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_undelegate_infinite(del_data)
        assert str(ex.value) == 'error_code: 2098 != 0'

        # region_admin update region info
        region_data = dict(region_id=f"{region_id}", from_addr=f"{region_admin_addr}", isUndelegate=True, fees="1")
        self.test_region.test_update_region(region_data)
        region_info = self.handle_q.get_region(region_id)
        assert region_info['region']['isUndelegate'] is False

        # superadmin update region info
        region_data = dict(region_id=f"{region_id}", from_addr=f"{chain.super_addr}", isUndelegate=True, fees="1")

        self.test_region.test_update_region(region_data)

        # query region info
        region_info = self.handle_q.get_region(region_id)
        assert region_info['region']['isUndelegate'] is True

        # query user_addr balance
        start_user_addr_balance = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])

        self.test_del.test_undelegate_infinite(del_data)

        end_user_addr_balance = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])

        assert end_user_addr_balance == start_user_addr_balance + calculate.to_usrc(2) - calculate.to_usrc(1)

        region_data = dict(region_id=f"{region_id}", from_addr=f"{chain.super_addr}", isUndelegate=False, fees="1")
        self.test_region.test_update_region(region_data)

        # query region info
        region_info = self.handle_q.get_region(region_id)
        assert region_info['region']['isUndelegate'] is False
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_undelegate_infinite(del_data)
        assert str(ex.value) == 'error_code: 2098 != 0'

        # isUndelegate is True
        region_data = dict(region_id=f"{region_id}", from_addr=f"{chain.super_addr}", isUndelegate=True, fees="1")
        self.test_region.test_update_region(region_data)
        region_info = self.handle_q.get_region(region_id)
        assert region_info['region']['isUndelegate'] is True

        # 提取所有永久质押金额 -> 返回永久质押本金+活期所得收益
        start_user_addr_balance2 = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])

        interest_amount = float(self.handle_q.get_delegate(user_addr)['delegation']['interestAmount'])
        # math.floor() 向下取整
        x = math.floor(interest_amount) if interest_amount >= 1 else 0

        del_data2 = dict(region_user_addr=user_addr, amount=10, fees=1)
        self.test_del.test_undelegate_infinite(del_data2)

        end_user_addr_balance2 = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])
        # 剩余8本金 - 1手续费 + 活期收益(手动永久质押+kyc收益)
        assert end_user_addr_balance2 == start_user_addr_balance2 + calculate.to_usrc(8 - 1) + x

    def test_withdraw(self, setup_create_region):
        """活期收益提取"""
        region_admin_addr, region_id, region_name, _ = setup_create_region

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        # 正常活期委托 10 coin
        del_data = dict(region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)

        # 永久活期委托 10 coin
        self.test_del.test_delegate_infinite(del_data)

        # 活期周期委托 10 coin
        del_data = dict(region_user_addr=f"{user_addr}", amount=10, term=chain.delegate_term[1], fees=1)
        self.test_del.test_delegate_fixed(del_data)

        x = calculate.to_usrc(100 - (10 * 3) - (1 * 3))
        start_user_addr_balance = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])
        assert start_user_addr_balance == x

        time.sleep(30)

        interest_amount = float(self.handle_q.get_delegate(user_addr)['delegation']['interestAmount'])
        y = math.floor(interest_amount) if interest_amount >= 1 else 0
        # 提取活期收益
        self.test_del.test_withdraw(dict(region_user_addr=user_addr, fees=1))

        end_user_addr_balance = int(self.handle_q.get_balance(user_addr, chain.coin['uc'])["amount"])
        assert end_user_addr_balance == start_user_addr_balance - calculate.to_usrc(1) + y
