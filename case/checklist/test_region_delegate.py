# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from case.bank.test_tx import TestBank
from case.staking.delegate.test_delegate import TestDelegate
from case.staking.kyc.test_kyc import TestKyc
from case.staking.region.test_region import TestRegion
from config import chain
from tools import calculate, handle_query

logger.add("logs/case_{time}.log", rotation="500MB")


class TestRegionDelegate(object):
    test_region = TestRegion()
    test_del = TestDelegate()
    test_kyc = TestKyc()
    test_bank = TestBank()
    handle_q = handle_query.HandleQuery()

    def test_region_delegate(self):
        """测试新创建区域并质押"""
        region_admin_addr, region_id = self.test_region.test_create_region()

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)

        # 验证用户余额
        user_balance = self.handle_q.get_balance(user_addr, 'usrc')
        assert user_balance['amount'] == str(calculate.subtraction(100, 10, 1))

        # 验证区信息
        region_info = self.handle_q.get_region(region_id)
        assert region_info['region_commission']['currentDemandTotalUAC'] == str(calculate.add([10, 1]))
        assert user_addr in region_info['delegators']['delegators']

        return region_admin_addr, region_id, user_addr

    def test_region_more_delegate(self):
        """多用户质押"""
        region_admin_addr, region_id, user_addr1 = self.test_region_delegate()
        logger.info(f'{"setup test_region_delegate finish":*^50s}')

        new_kyc_data = dict(region_id=f"{region_id}", region_admin_addr=f"{region_admin_addr}")
        user_addr2 = self.test_kyc.test_new_kyc_user(new_kyc_data)

        send_data = dict(from_addr=f"{chain.super_addr}", to_addr=f"{user_addr2}", amount="100", fees="1")
        self.test_bank.test_send(send_data)

        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", amount="10", fees="1")
        self.test_del.test_delegate(del_data)

        user_balance = self.handle_q.get_balance(user_addr2, 'usrc')
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
        region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate()
        logger.info(f'{"setup test_region_more_delegate finish":*^50s}')

        user1_balance = int(self.handle_q.get_balance(user_addr1, 'usrc')['amount'])

        logger.info(f'{"- user1 赎回部分活期质押":*^50s}')
        amount = 5
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr1}", amount=amount, fees="1")
        self.test_del.test_undelegate(del_data)

        u_amount = calculate.to_usrc(amount)
        u_fees = calculate.to_usrc(1)
        resp_balance_1 = int(self.handle_q.get_balance(user_addr1, 'usrc')['amount'])
        assert resp_balance_1 == user1_balance + u_amount - u_fees

        logger.info(f'{"- user1 赎回大于额 > 剩余活期质押额":*^50s}')
        amount2 = 6
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr1}", amount=amount2, fees="1")
        self.test_del.test_undelegate(del_data)

        # u_amount == 5000000usrc  赎回6src但是余额只是增加5src
        resp_balance_2 = int(self.handle_q.get_balance(user_addr1, 'usrc')['amount'])
        assert resp_balance_2 == resp_balance_1 + u_amount - u_fees
        time.sleep(2)
        logger.info(f'{"+ expect: user1 无活期质押,还存在KYC赠送质押":*^50s}')
        user1_del_info = self.handle_q.get_delegate(user_addr1)
        # ["delegation"]["amountAC"] 代币单位 usrc
        assert user1_del_info['delegation']['amountAC'] == "0"
        assert user1_del_info["delegation"]["unmovableAmount"] == "1000000"

        user2_balance = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
        logger.info(f'{"- user2 赎回小数值":*^50s}')
        amount3 = 4.999999
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", amount=amount3, fees="1")
        self.test_del.test_undelegate(del_data)

        u_amount3 = calculate.to_usrc(amount3)
        resp_balance_3 = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
        assert resp_balance_3 == user2_balance + u_amount3 - u_fees

        logger.info(f'{"- user2 赎回小数值超过6位小数,截取字符":*^50s}')
        amount4 = 4.9999999
        del_data = dict(region_id=f"{region_id}", region_user_addr=f"{user_addr2}", amount=amount4, fees="1")
        self.test_del.test_undelegate(del_data)

        resp_balance_4 = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
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

        resp_balance_5 = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
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
        region_admin_addr, region_id, user_addr1, user_addr2 = self.test_region_more_delegate()
        logger.info(f'{"setup test_region_more_delegate finish":*^50s}')

        user1_balance = int(self.handle_q.get_balance(user_addr1, 'usrc')['amount'])
        logger.info(f'{"- user1 superAdmin发起清退":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr1}",
                        from_addr=f"{chain.super_addr}", fees="1", from_super=True)
        self.test_del.test_exit_delegate(del_data)

        u_delegate_amount = calculate.to_usrc(10)
        resp_balance_1 = int(self.handle_q.get_balance(user_addr1, 'usrc')['amount'])
        assert resp_balance_1 == user1_balance + u_delegate_amount

        logger.info(f'{"+ expect: user1 无活期质押,还剩下kyc赠送质押":*^50s}')
        time.sleep(2)
        user1_del_info = self.handle_q.get_delegate(user_addr1)
        # ["delegation"]["amountAC"] 代币单位 usrc
        assert user1_del_info["delegation"]["amountAC"] == "0"
        assert user1_del_info["delegation"]["unmovableAmount"] == "1000000"

        user2_balance = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
        logger.info(f'{"- user2 regionAmin发起清退":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr2}",
                        from_addr=f"{region_admin_addr}", fees="1", from_super=False)
        self.test_del.test_exit_delegate(del_data)

        resp_balance_2 = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
        assert resp_balance_2 == user2_balance + u_delegate_amount

        logger.info(f'{"+ expect: user2 无活期质押,还剩下kyc赠送质押":*^50s}')
        time.sleep(2)
        user2_del_info = self.handle_q.get_delegate(user_addr2)
        assert user2_del_info["delegation"]["amountAC"] == "0"
        assert user2_del_info["delegation"]["unmovableAmount"] == "1000000"

        user2_balance2 = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
        logger.info(f'{"- user2 regionAmin多次发起清退":*^50s}')
        del_data = dict(region_id=f"{region_id}", delegator_address=f"{user_addr2}",
                        from_addr=f"{region_admin_addr}", fees="1", from_super=False)

        logger.info(f'{"+ expect: 无效清退 error_code: 2097"}')
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_exit_delegate(del_data)
        assert str(ex.value) == 'assert 2097 == 0'

        resp_balance2 = int(self.handle_q.get_balance(user_addr2, 'usrc')['amount'])
        assert resp_balance2 == user2_balance2
