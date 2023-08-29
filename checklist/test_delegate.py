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
from x.query import HttpQuery, Query
from x.tx import Tx


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
    tx = Tx()
    hq = HttpQuery()
    q = Query()
    user_addr = None

    def test_no_kyc_user_un_delegate_seven(self, create_no_kyc_send_money):
        """
        没有进行kyc的用户进行超过7次的赎回操作
        @Desc
            - user 非kyc用户
            - 超管给用户发钱
            - 用户存80mec
            - 用户赎回
            + expect:赎回7次都成功，赎回第8次及之后的时候异常 code=27
        """
        logger.info("TestRegionDelegate/test_no_kyc_user_un_delegate_seven")
        user_addr = create_no_kyc_send_money
        del_data = dict(from_addr=user_addr, amount=80)
        self.test_del.test_delegate(**del_data)

        del_data = dict(from_addr=user_addr, amount=2)
        for i in range(1, 9):
            resp = self.tx.staking.undelegate_nokyc(**del_data)
            code = self.hq.tx.query_tx(resp['txhash'])['code']
            # 只允许非kyc用户进行7次活期委托
            if i <= 7:
                assert code == 0
            else:
                assert code == 27

    def test_different_node_delegate(self):
        """
        在费率不同的验证者节点之间进行委托和赎回
        @Desc
            - node1 和 node7 的节点费率不同
            - 用户通过node1节点验证委托
            - 用户通过node7节点验证赎回
            + expect:委托和赎回正常，收费费分别按对应的扣除
        """
        logger.info("TestRegionDelegate/test_different_node_delegate")
        user_addr = self.test_key.test_add()['address']
        time.sleep(self.tx.sleep_time*2)

        self.base_cfg.Bank.send_to_admin(amount=(300 + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr, amount=300)
        self.test_bank.test_send(**send_data)

        before_balance = self.hq.bank.query_balances(user_addr)
        # 用户发起活期委托,使用节点node1进行验证
        delegate_amount = 100
        delegate_data = dict(from_addr=user_addr, amount=delegate_amount, node_ip=self.tx.node_id['node1'])
        resp = self.tx.staking.delegate(**delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 查询用户的活期委托 拿到块高
        start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']

        # 验证用户的余额应该 =  发起活期委托之前的余额 - 活期委托的金额 - 手续费
        after_balance = self.hq.bank.query_balances(user_addr)
        assert after_balance == before_balance - Compute.to_u(delegate_amount) - self.base_cfg.fees

        # 查询用户的非kyc委托 应该是发起活期委托的金额
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

        # 赎回委托的金额,使用node7的节点进行验证，这里node7的基础手续费时200umec
        un_delegate_amount = delegate_amount
        un_del_data = dict(from_addr=user_addr, amount=un_delegate_amount, fees=self.base_cfg.fees*2,
                           node_ip=self.tx.node_id['node7'])
        result = self.test_del.test_undelegate_nokyc(**un_del_data)
        assert resp['code'] == 0

        # 计算收益
        end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        reward = Reward.reward_nokyc(stake=float(delegate_amount), start_height=start_height, end_height=end_height)

        # 赎回金额不会立马到帐，只有收益到帐  这里node7的基础手续费时200umec
        end_balance = self.hq.bank.query_balances(user_addr)
        assert end_balance + self.base_cfg.fees*2 - after_balance == reward

        self.tx.keys.delete(self.q.key.name_of_addre(user_addr))

    def test_one_no_kyc_user_delegate(self):
        """
        单个非kyc用户两次以上的活期委托并赎回
        @Desc
            - user 新增一个用户
            - 超管给用户发钱
            - 用户第一次进行活期委托
            + expect:活期委托交易成功，用户余额扣除活期委托金额和手续费，用户非kyc委托增加金额与委托金额一致
            - 用户赎回所有的活期委托
            + expect：赎回交易成功，余额不增加，要7天后到帐，产生的收益到帐
            - 用户第二次进行活期委托
            + expect:活期委托交易成功，用户余额扣除活期委托金额和手续费，用户非kyc委托增加金额与委托金额一致
            - 用户赎回所有的活期委托
            + expect：赎回交易成功，余额不增加，要7天后到帐，收益立马到帐
        """
        logger.info("TestRegionDelegate/test_one_no_kyc_user_delegate")
        user_addr = self.test_key.test_add()['address']
        time.sleep(self.tx.sleep_time*2)

        self.base_cfg.Bank.send_to_admin(amount=(300 + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr, amount=300)
        self.test_bank.test_send(**send_data)
        # 不能超过7次
        for index in range(1, 3):
            before_balance = self.hq.bank.query_balances(user_addr)
            # 用户发起活期委托
            delegate_amount = 100
            delegate_data = dict(from_addr=user_addr, amount=delegate_amount)
            resp = self.tx.staking.delegate(**delegate_data)
            code = self.hq.tx.query_tx(resp['txhash'])['code']
            assert code == 0

            # 查询用户的活期委托 拿到块高
            start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']

            # 验证用户的余额应该 =  发起活期委托之前的余额 - 活期委托的金额 - 手续费
            after_balance = self.hq.bank.query_balances(user_addr)
            assert after_balance == before_balance - Compute.to_u(delegate_amount) - self.base_cfg.fees

            # 查询用户的非kyc委托 应该是发起活期委托的金额
            user_delegate_info = HttpResponse.get_delegate(user_addr)
            assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

            # 赎回委托的金额
            un_delegate_amount = delegate_amount
            un_del_data = dict(from_addr=user_addr, amount=un_delegate_amount)
            result = self.test_del.test_undelegate_nokyc(**un_del_data)
            assert resp['code'] == 0

            # 计算收益
            end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
            reward = Reward.reward_nokyc(stake=float(delegate_amount), start_height=start_height, end_height=end_height)

            # 赎回金额不会立马到帐，只有收益到帐
            end_balance = self.hq.bank.query_balances(user_addr)
            assert end_balance + self.base_cfg.fees - after_balance == reward

        self.tx.keys.delete(self.q.key.name_of_addre(user_addr))

    def test_no_kyc_to_kyc_user_more_delegate(self):
        """
        单个非kyc用户多次活期委托，再赎回，然后成为kyc后进行活期委托并赎回
        @Desc
            - user 新增一个用户
            - 超管给用户发钱
            - 用户第一次进行活期委托
            + expect:活期委托交易成功，用户余额扣除活期委托金额和手续费，用户非kyc委托增加金额与委托金额一致
            - 用户第二次进行活期委托
            + expect:活期委托交易成功，计算之前已存在的活期委托收益，收益进入用户的余额账户
            - 用户认证为kyc用户，并进行活期委托
            + expect：用户同时存在kyc委托和非kyc委托，金额正确
            - 赎回所有委托
            + expect: kyc委托金额赎回即时到帐，收益也到帐,非kyc委托金额只有收益到帐
        """
        logger.info("TestRegionDelegate/test_no_kyc_to_kyc_user_more_delegate")
        user_addr = self.test_key.test_add()['address']
        time.sleep(self.tx.sleep_time)

        self.base_cfg.Bank.send_to_admin(amount=(500 + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user_addr, amount=500)
        self.test_bank.test_send(**send_data)

        before_balance = self.hq.bank.query_balances(user_addr)
        # 用户第一次发起活期委托
        delegate_amount = 100
        delegate_data = dict(from_addr=user_addr, amount=delegate_amount)
        resp = self.tx.staking.delegate(**delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 查询用户的活期委托 拿到块高
        start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']

        # 验证用户的余额应该 =  发起活期委托之前的余额 - 活期委托的金额 - 手续费
        after_balance = self.hq.bank.query_balances(user_addr)
        assert after_balance == before_balance - Compute.to_u(delegate_amount) - self.base_cfg.fees

        # 查询用户的非kyc委托 应该是发起活期委托的金额
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

        # 用户发起第二次活期委托，非kyc存在已有活期委托时再进行活期委托会先计算上一笔活期委托的所有收益
        delegate_amount = 100
        delegate_data = dict(from_addr=user_addr, amount=delegate_amount)
        resp = self.tx.staking.delegate(**delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 查询用户的活期委托 拿到块高 这里的开始块高就是计算上一笔活期委托收益的结束块高
        end_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        reward = Reward.reward_nokyc(stake=float(delegate_amount), start_height=start_height, end_height=end_height)
        # 赎回金额不会立马到帐，只有收益到帐
        end_balance = self.hq.bank.query_balances(user_addr)
        # 计算出的收益与实际收益一致  余额+2次手续费+2次活期委托的金额-没有进行交易时的余额 = 收益
        assert end_balance + self.base_cfg.fees*2 + Compute.to_u(delegate_amount*2) - before_balance == reward

        kyc_start_balance = self.hq.bank.query_balances(user_addr)
        # 将用户认证成kyc
        self.test_kyc.test_new_kyc_user_not_in_node5(addr=user_addr)
        kyc_end_balance = self.hq.bank.query_balances(user_addr)
        # 完成kyc认证后会转入一笔费用到unmovable，所以也需要计算一次非kyc时候的活期委托
        kyc_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        un_kyc_reward1 = Reward.reward_nokyc(stake=float(delegate_amount*2),
                                             start_height=end_height, end_height=kyc_height)

        # 认证完kyc后的余额
        kyc_delegate_before_balance = self.hq.bank.query_balances(user_addr)

        # 如果还有非kyc认证时候的委托，完成kyc人在后会产生收益吗？

        # 用户进行活期委托
        kyc_delegate_amount = 100
        kyc_delegate_data = dict(from_addr=user_addr, amount=kyc_delegate_amount)
        resp = self.tx.staking.delegate(**kyc_delegate_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0
        kyc_delegate_end_balance = self.hq.bank.query_balances(user_addr)
        # 当前活期委托数据应该等于委托数据
        user1_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user1_delegate_info['amount']) == Compute.to_u(delegate_amount)

        # 完成kyc活期委托后要计算一笔 非kyc时活期的收益
        kyc_start_height = (HttpQuery.Staking.delegation(addr=user_addr))['startHeight']
        un_kyc_reward2 = Reward.reward_nokyc(stake=float(delegate_amount*2),
                                             start_height=kyc_height, end_height=kyc_start_height)

        # 赎回kyc活期委托，并计算收益
        result = Tx.Staking.undelegate_kyc(from_addr=user_addr, amount=float(kyc_delegate_amount))
        self.hq.tx.query_tx(result['txhash'])
        kyc_end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        # 计算出用户的活期委托收益
        reward = Reward.reward_kyc(stake=float(kyc_delegate_amount),
                                   start_height=kyc_start_height, end_height=kyc_end_height)

        # 完成赎回时也要计算一次非kyc时委托的收益
        un_kyc_reward3 = Reward.reward_nokyc(stake=float(delegate_amount * 2), start_height=kyc_height,
                                             end_height=kyc_start_height)
        un_kyn_reward = un_kyc_reward1 + un_kyc_reward2 + un_kyc_reward3
        kyc_delegate_after_balance = self.hq.bank.query_balances(user_addr)
        # 最后的余额 + 两次手续非 - 开始kyc认证前的余额 - 非kyc委托部分的收益 = kyc后活期委托的收益
        assert kyc_delegate_after_balance + self.base_cfg.fees*2 - kyc_start_balance - un_kyn_reward == reward
        # 删除用户
        self.tx.keys.delete(self.q.key.name_of_addre(user_addr))

    def test_more_kyc_user_delegate(self):
        """
        多个kyc用户两次以上的活期委托并赎回
        @Desc
            - user1 user2 新增2个kyc用户
            - 超管给两个用户转钱
            - 用户第一次进行活期委托
            + expect:活期委托交易成功，用户余额扣除活期委托金额和手续费，用户委托账户增加金额与委托金额一致
            - 用户赎回所有的活期委托
            + expect：赎回交易成功，余额增加，产生的收益到帐
            - 用户第二次进行活期委托
            + expect:活期委托交易成功，用户余额扣除活期委托金额和手续费，用户非kyc委托增加金额与委托金额一致
            - 用户赎回所有的活期委托
            + expect：赎回交易成功，余额不增加，要7天后到帐，收益立马到帐
        """
        logger.info("TestRegionDelegate/test_more_kyc_user_delegate")
        region_list_len = len(self.q.staking.list_region())
        if region_list_len == 0:
            pytest.skip("没有可用的区,请先创建区")

        # 获得两个kyc用户
        user1_addr = self.test_kyc.test_new_kyc_user_not_in_node5()
        user2_addr = self.test_kyc.test_new_kyc_user_not_in_node5()

        self.base_cfg.Bank.send_to_admin(amount=(500 + 1) * 2)  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user1_addr, amount=500)
        self.test_bank.test_send(**send_data)
        send_data = dict(from_addr=self.tx.super_addr, to_addr=user2_addr, amount=500)
        self.test_bank.test_send(**send_data)

        for index in range(1, 3):
            # 用户余额
            user1_before_balance = self.hq.bank.query_balances(user1_addr)
            user2_before_balance = self.hq.bank.query_balances(user2_addr)
            # 用户发起活期委托
            delegate_amount = 100
            delegate_data = dict(from_addr=user1_addr, amount=delegate_amount)
            resp = self.tx.staking.delegate(**delegate_data)
            code = self.hq.tx.query_tx(resp['txhash'])['code']
            assert code == 0

            # 当前活期委托数据应该等于委托数据
            user1_delegate_info = HttpResponse.get_delegate(user1_addr)
            assert int(user1_delegate_info['amount']) == Compute.to_u(delegate_amount)

            start_height = (HttpQuery.Staking.delegation(addr=user1_addr))['startHeight']
            result = Tx.Staking.undelegate_kyc(from_addr=user1_addr, amount=float(delegate_amount))
            self.hq.tx.query_tx(result['txhash'])
            end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
            # 计算出用户的活期委托收益
            reward = Reward.reward_kyc(stake=float(delegate_amount),
                                       start_height=start_height, end_height=end_height)
            user1_end_balance = self.hq.bank.query_balances(user1_addr)
            # 最终的余额 = 开始的余额 - 2次手续费 + 产生的收益
            assert user1_before_balance - self.base_cfg.fees * 2 + reward == user1_end_balance

            # 用户发起活期委托
            user2_delegate_amount = 100
            delegate_data = dict(from_addr=user2_addr, amount=user2_delegate_amount)
            resp = self.tx.staking.delegate(**delegate_data)
            code = self.hq.tx.query_tx(resp['txhash'])['code']
            assert code == 0

            # 当前活期委托数据应该等于委托数据
            user2_delegate_info = HttpResponse.get_delegate(user2_addr)
            assert int(user2_delegate_info['amount']) == Compute.to_u(user2_delegate_amount)

            start_height = (HttpQuery.Staking.delegation(addr=user2_addr))['startHeight']
            result = Tx.Staking.undelegate_kyc(from_addr=user2_addr, amount=float(user2_delegate_amount))
            self.hq.tx.query_tx(result['txhash'])
            end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
            # 计算出用户的活期委托收益
            reward = Reward.reward_kyc(stake=float(user2_delegate_amount),
                                       start_height=start_height, end_height=end_height)
            user2_end_balance = self.hq.bank.query_balances(user2_addr)
            # 最终的余额 = 开始的余额 - 2次手续费 + 产生的收益
            assert user2_before_balance - self.base_cfg.fees * 2 + reward == user2_end_balance

        self.tx.keys.delete(self.q.key.name_of_addre(user1_addr))
        self.tx.keys.delete(self.q.key.name_of_addre(user2_addr))

    def test_kyc_user_more_delegate(self):
        """
        一个kyc用户连续委托多次，再赎回
        @Desc
            - user kyc用户委连续托次4次
            + expect： 累积委托金额与进行委托的金额一致，手续费扣除金额正确
            - user 进行全部金额的赎回操作
            + expect：赎回成功，活期委托金额回到余额账户 计算收益与实际收益一致，手续费扣除金额正确
        """
        logger.info("TestRegionDelegate/test_kyc_user_more_delegate")
        region_list_len = len(self.q.staking.list_region())
        if region_list_len == 0:
            pytest.skip("没有可用的区,请先创建区")

        kyc_user_addr = self.test_kyc.test_new_kyc_user_not_in_node5()
        no_kyc_user_addr = self.test_key.test_add()['address']

        self.base_cfg.Bank.send_to_admin(amount=(500 + 1) * 2)  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        # 超管给用户转100mec
        send_data = dict(from_addr=self.tx.super_addr, to_addr=kyc_user_addr, amount=500)
        self.test_bank.test_send(**send_data)
        send_data = dict(from_addr=self.tx.super_addr, to_addr=no_kyc_user_addr, amount=500)
        self.test_bank.test_send(**send_data)
        kyc_user_start_balance = self.hq.bank.query_balances(kyc_user_addr)
        start_height_list = []
        # kyc 用户一直委托
        for index in range(1, 5):
            kyc_user_delegate_amount = 100
            delegate_data = dict(from_addr=kyc_user_addr, amount=kyc_user_delegate_amount)
            resp = self.tx.staking.delegate(**delegate_data)
            code = self.hq.tx.query_tx(resp['txhash'])['code']
            assert code == 0
            start_height = (HttpQuery.Staking.delegation(addr=kyc_user_addr))['startHeight']
            start_height_list.append(start_height)
            # 当前活期委托数据应该等于委托数据
            kyc_user_delegate_info = HttpResponse.get_delegate(kyc_user_addr)
            assert int(kyc_user_delegate_info['amount']) == Compute.to_u(kyc_user_delegate_amount*index)

        result = Tx.Staking.undelegate_kyc(from_addr=kyc_user_addr,
                                           amount=float(kyc_user_delegate_amount*len(start_height_list)))
        self.hq.tx.query_tx(result['txhash'])
        end_height = int((Query.Tx.query_tx(tx_hash=result['txhash']))['height'])
        reward = 0
        for i in range(0, len(start_height_list)):
            logger.info(f"------------计算第{i+1}次收益-----------------------")
            logger.info(f"------------块高是：{start_height_list[i]}-----------------------")
            # 大于一次后，会重复计算kyc成功后赠送的1mec收益，所以委托金额要减1
            if i > 0:
                amount = kyc_user_delegate_amount - 1
            else:
                amount = kyc_user_delegate_amount
            reward += Reward.reward_kyc(stake=float(amount),
                                        start_height=start_height_list[i], end_height=end_height)

        kyc_user_end_balance = self.hq.bank.query_balances(kyc_user_addr)
        logger.info(f"查到的余额是：{kyc_user_end_balance}")
        logger.info(f"累积计算出的收益是：{reward}")
        assert (kyc_user_end_balance + self.base_cfg.fees * len(start_height_list) +
                self.base_cfg.fees - kyc_user_start_balance) == reward

        self.tx.keys.delete(self.q.key.name_of_addre(self.q.key.name_of_addre(kyc_user_addr)))
        self.tx.keys.delete(self.q.key.name_of_addre(self.q.key.name_of_addre(no_kyc_user_addr)))


    # def test_region_delegate(self, setup_create_region):
    #     """测试新创建区域并质押"""
    #     logger.info("TestRegionDelegate/test_region_delegate")
    #     region_admin_info, region_id, region_name = setup_create_region #
    #     region_admin_addr = region_admin_info['address']
    #
    #     new_kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
    #     user_info = self.test_kyc.test_new_kyc_user(**new_kyc_data)
    #     user_addr = user_info['address']
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
    # @pytest.mark.skip
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
    #     self.base_cfg.Bank.send_to_admin(amount=10000)
    #     user_info = self.test_kyc.test_new_kyc_user(region_id=region_id)
    #     user_addr = user_info
    #     # 管理员给用户转100块
    #     send_amount = 100
    #     self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=(send_amount + 1))
    #     self.test_bank.test_send(**send_data)
    #     # 用户发起10块钱质押
    #     del_data = dict(from_addr=user_addr, amount=send_amount)
    #     self.test_del.test_delegate(**del_data)
    #     # 查询用户的余额
    #     user_balance = HttpResponse.get_balance_unit(user_addr)
    #     assert user_balance == 1 * (10 ** 6) - self.base_cfg.fees
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
    #     assert delegation_amount == send_amount * (10 ** 6)
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

    # def test_two_kyc_user_delegate(self, get_region_id_existing):
    #     """
    #     两个用户质押的情况 汪 过了,拿已存在的区ID，
    #     """
    #     # 拿上一个接口结束时的区id和kyc用户地址
    #     logger.info("TestRegionDelegate/test_more_kyc_user_delegate")
    #     # region_id, user_addr1 = self.test_region_delegate(setup_create_validator_and_region) # 这个是上面传下的来
    #     region_id = get_region_id_existing  # 这个是获取已存在的区id,且等下自己新建KYC用户
    #     # 委托之前先查询一下节点的委托金额，等下后面拿来做断言
    #     validator_addr = HttpResponse.get_region(region_id=region_id)['region']['operator_address']
    #     validator_delegate_start = int(
    #         HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     logger.info(f"测试开始前，节点委托的金额：{validator_delegate_start}")
    #     send_amount = 101
    #     delegate_amount1 = 100
    #     # 本来第一个用户是上面接口传下来的，现在没有传下来，就手动创建第1个用户，区id不变
    #     user_info1 = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)
    #     user_addr1 = user_info1
    #     # 管理员给这个用户转账。
    #     self.base_cfg.Bank.send_to_admin(amount=send_amount)
    #     send_data1 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr1, amount=send_amount)  # 准备转账数据
    #     self.test_bank.test_send(**send_data1)  # 发起转账，**字典传参
    #     # 用户发起委托
    #     del_data = dict(from_addr=user_addr1, amount=delegate_amount1)
    #     self.test_del.test_delegate(**del_data)  # 字典传参
    #     # 查询余额
    #     user1_balances = HttpResponse.get_balance_unit(user_addr=user_addr1)
    #     logger.info(f"委托结束后用户的余额：{user1_balances}")
    #     # 断言
    #     assert user1_balances == Compute.to_u(number=(send_amount - delegate_amount1)) - self.base_cfg.fees
    #
    #     logger.info(f'{"setup test_region_delegate finish":*^50s}')
    #     delegate_amount2 = 80
    #     # 如果用上面接口传下来的region_id 就直接用
    #     user_info2 = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)  # 创建随机用户且KYC，会返回user_add
    #     user_addr2 = user_info2
    #     # 管理员给这个用户转账。
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2, amount=send_amount)  # 准备转账数据
    #     self.test_bank.test_send(**send_data)  # 发起转账，**字典传参
    #     # 用户发起委托
    #     del_data = dict(from_addr=user_addr2, amount=delegate_amount2)
    #     self.test_del.test_delegate(**del_data)  # 字典传参
    #     # 查询用户余额 回来的是int的
    #     user2_balances = HttpResponse.get_balance_unit(user_addr=user_addr2)
    #     logger.info(f"委托结束后用户的余额：{user2_balances}")
    #     # 断言个人的余额有没有减少
    #     assert user2_balances == Compute.to_u(number=(send_amount - delegate_amount2)) - self.base_cfg.fees
    #     # 断言区委托有没有增加->就是验证者节点的委托
    #
    #     validator_delegate_end = int(
    #         HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     logger.info(f"测试结束后，节点委托的金额：{validator_delegate_end}")
    #     # 断言节点委托是否等于用户的委托
    #     assert validator_delegate_end == validator_delegate_start + Compute.to_u(
    #         number=delegate_amount1) + Compute.to_u(
    #         number=delegate_amount2)
    #     # logger.info(f"collect_addr_list:{region_id, user_addr1, user_addr2}")
    #     logger.info(f"collect_addr_list:{region_id, user_addr2}")
    #     logger.info('test_two_kyc_user_delegate 本条用例结束')
    #     logger.info(f"region_id={region_id}，user_addr2={user_addr2}")
    #     # return region_id, user_addr1, user_addr2
    #     logger.info(
    #         f"user_addr1={user_addr1},user_addr2={user_addr2},validator_addr={validator_addr},"
    #         f"validator_delegate_end={validator_delegate_end},user1_balances{user1_balances},"
    #         f"user2_balances{user2_balances},delegate_amount={delegate_amount2}")
    #     return user_addr1, user_addr2, validator_addr, validator_delegate_end, user1_balances, user2_balances, delegate_amount1, delegate_amount2

    # def test_two_kyc_user_delegate(self, setup_create_validator_and_region):
    #     """
    #     两个用户质押的情况 汪 过了,拿已存在的区ID，
    #     """
    #     # 拿上一个接口结束时的区id和kyc用户地址
    #     logger.info("TestRegionDelegate/test_more_kyc_user_delegate")
    #     region_id, user_addr1 = self.test_region_delegate(setup_create_validator_and_region) # 这个是上面传下的来
    #     # region_id = get_region_id_existing  # 这个是获取已存在的区id,且等下自己新建KYC用户
    #     # 委托之前先查询一下节点的委托金额，等下后面拿来做断言
    #     validator_addr = HttpResponse.get_region(region_id=region_id)['region']['operator_address']
    #     validator_delegate_start = int(
    #         HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     logger.info(f"测试开始前，节点委托的金额：{validator_delegate_start}")
    #     send_amount = 101
    #     delegate_amount1 = 100
    #     # 本来第一个用户是上面接口传下来的，现在没有传下来，就手动创建第1个用户，区id不变
    #     # user_info1 = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)
    #     # user_addr1 = user_info1
    #     # 管理员给这个用户转账。
    #     self.base_cfg.Bank.send_to_admin(amount=send_amount)
    #     send_data1 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr1, amount=send_amount)  # 准备转账数据
    #     self.test_bank.test_send(**send_data1)  # 发起转账，**字典传参
    #     # 用户发起委托
    #     del_data = dict(from_addr=user_addr1, amount=delegate_amount1)
    #     self.test_del.test_delegate(**del_data)  # 字典传参
    #     # 查询余额
    #     user1_balances = HttpResponse.get_balance_unit(user_addr=user_addr1)
    #     logger.info(f"委托结束后用户user1的余额：{user1_balances}")
    #     # 断言
    #     assert user1_balances == Compute.to_u(number=(send_amount - delegate_amount1)) - self.base_cfg.fees
    #
    #     logger.info(f'{"setup test_region_delegate finish":*^50s}')
    #     delegate_amount2 = 80
    #     # 如果用上面接口传下来的region_id 就直接用
    #     user_info2 = self.test_kyc.test_new_kyc_user(region_id=region_id, addr=None)  # 创建随机用户且KYC，会返回user_add
    #     user_addr2 = user_info2
    #     # 管理员给这个用户转账。
    #     send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2, amount=send_amount)  # 准备转账数据
    #     self.test_bank.test_send(**send_data)  # 发起转账，**字典传参
    #     # 用户发起委托
    #     del_data = dict(from_addr=user_addr2, amount=delegate_amount2)
    #     self.test_del.test_delegate(**del_data)  # 字典传参
    #     # 查询用户余额 回来的是int的
    #     user2_balances = HttpResponse.get_balance_unit(user_addr=user_addr2)
    #     logger.info(f"委托结束后用户user2的余额：{user2_balances}")
    #     # 断言个人的余额有没有减少
    #     assert user2_balances == Compute.to_u(number=(send_amount - delegate_amount2)) - self.base_cfg.fees
    #     # 断言区委托有没有增加->就是验证者节点的委托
    #
    #     validator_delegate_end = int(
    #         HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     logger.info(f"测试结束后，节点委托的金额：{validator_delegate_end}")
    #     # 断言节点委托是否等于用户的委托
    #     assert validator_delegate_end == validator_delegate_start + Compute.to_u(
    #         number=delegate_amount1) + Compute.to_u(
    #         number=delegate_amount2)
    #     # logger.info(f"collect_addr_list:{region_id, user_addr1, user_addr2}")
    #     logger.info(f"collect_addr_list:{region_id, user_addr2}")
    #     logger.info('test_two_kyc_user_delegate 本条用例结束')
    #     logger.info(f"region_id={region_id}，user_addr2={user_addr2}")
    #     # return region_id, user_addr1, user_addr2
    #     logger.info(
    #         f"user_addr1={user_addr1},user_addr2={user_addr2},validator_addr={validator_addr},"
    #         f"validator_delegate_end={validator_delegate_end},user1_balances{user1_balances},"
    #         f"user2_balances{user2_balances},delegate_amount={delegate_amount2}")
    #     return user_addr1, user_addr2, validator_addr, validator_delegate_end, user1_balances, user2_balances, delegate_amount1, delegate_amount2

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

    # def test_region_more_undelegate_wang(self, setup_create_validator_and_region):
    #     """测试两个用户减少委托，计算收益，前置是前面用户委托成功，"""
    #     # 先把用户信息拿出来，上一个测试接口造了数据，两个KYC用户委托，
    #     user_addr1, user_addr2, validator_addr, vali_delegator, user1_balances_start, user2_balances_start, \
    #         delegate_amount1, delegate_amount2 = self.test_two_kyc_user_delegate(
    #         setup_create_validator_and_region=setup_create_validator_and_region)
    #     logger.info(
    #         f"打印上一个接口传下来后的值，user1_balances={user1_balances_start},type{type(user1_balances_start)}")
    #     logger.info(
    #         f"打印上一个接口传下来后的值，user2_balances={user2_balances_start},type{type(user2_balances_start)}")
    #
    #     # 用戶1用例1:減少用户1的委托，减少金额小于已有委托金额
    #     user1_undel_amount = 1  # 單位是mec
    #     start_height = HttpResponse.get_delegate_for_http(user_addr=user_addr1)['startHeight']
    #     time.sleep(30)
    #     un_delegate_data = dict(from_addr=user_addr1, amount=user1_undel_amount)  # 解决传参，字典传参
    #     end_height = int((self.test_del.test_undelegate_kyc(**un_delegate_data))['height'])  # 减少委托
    #     # 查询user1的金额
    #     user1_balances_end = HttpResponse.get_balance_unit(user_addr=user_addr1)
    #     # 手动计算收益，然后断言用户余额
    #     rewards = Reward.reward_kyc(stake=delegate_amount1, end_height=end_height, start_height=start_height)
    #     logger.info(f"开始快高为：{start_height},结束快高为：{end_height}，手动计算的收益为：{rewards}")
    #     assert user1_balances_end == user1_balances_start + Compute.to_u(
    #         number=user1_undel_amount) + rewards - self.base_cfg.fees
    #     # 查询区域委托
    #     vali_delegator2 = int(HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     # 断言现在的区域委托是否等于之前的-這一次减少的
    #     logger.info(
    #         f"开始是的节点委托金额为：{vali_delegator},结束后的节点委托金额为:{vali_delegator2},减少了委托{Compute.to_u(number=user1_undel_amount)}")
    #     assert vali_delegator2 == vali_delegator - Compute.to_u(number=user1_undel_amount)
    #
    #     # 用户2测试用例1 减少金额小于已有金额
    #     user2_undel_amount = 2
    #     start_height_user2 = HttpResponse.get_delegate_for_http(user_addr=user_addr2)['startHeight']
    #     un_delegate_data2 = dict(from_addr=user_addr2, amount=user2_undel_amount)
    #     end_height_user2 = int((self.test_del.test_undelegate_kyc(**un_delegate_data2))['height'])  # 减少用户2委托
    #     # # 查询user1的金额
    #     user2_balances_end = HttpResponse.get_balance_unit(user_addr=user_addr2)
    #     # # 手动计算收益，然后断言用户余额
    #     rewards_user2 = Reward.reward_kyc(stake=delegate_amount2, end_height=end_height_user2,
    #                                       start_height=start_height_user2)
    #     assert user2_balances_end == user2_balances_start + Compute.to_u(
    #         number=user2_undel_amount) + rewards_user2 - self.base_cfg.fees
    #     # # 查询区域委托
    #     vali_delegator3 = int(HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     assert vali_delegator3 == vali_delegator2 - Compute.to_u(number=user2_undel_amount)
    #     # 打扫数据，根据addr删除用户
    #     self.test_key.test_delete_key(addr=user_addr1)
    #     self.test_key.test_delete_key(addr=user_addr2)

    # def test_region_more_undelegate_wang(self, get_region_id_existing):
    #     """测试两个用户减少委托，计算收益，前置是前面用户委托成功，"""
    #     # 先把用户信息拿出来，上一个测试接口造了数据，两个KYC用户委托，
    #     user_addr1, user_addr2, validator_addr, vali_delegator, user1_balances_start, user2_balances_start, \
    #         delegate_amount1, delegate_amount2 = self.test_two_kyc_user_delegate(
    #         get_region_id_existing=get_region_id_existing)
    #     logger.info(
    #         f"打印上一个接口传下来后的值，user1_balances={user1_balances_start},type{type(user1_balances_start)}")
    #     logger.info(
    #         f"打印上一个接口传下来后的值，user2_balances={user2_balances_start},type{type(user2_balances_start)}")
    #
    #     # 用戶1用例1:減少用户1的委托，减少金额小于已有委托金额
    #     user1_undel_amount = 1  # 單位是mec
    #     start_height = HttpResponse.get_delegate_for_http(user_addr=user_addr1)['startHeight']
    #     time.sleep(30)
    #     un_delegate_data = dict(from_addr=user_addr1, amount=user1_undel_amount)  # 解决传参，字典传参
    #     end_height = int((self.test_del.test_undelegate_kyc(**un_delegate_data))['height'])  # 减少委托
    #     # 查询user1的金额
    #     user1_balances_end = HttpResponse.get_balance_unit(user_addr=user_addr1)
    #     # 手动计算收益，然后断言用户余额
    #     rewards = Reward.reward_kyc(stake=delegate_amount1, end_height=end_height, start_height=start_height)
    #     logger.info(f"开始快高为：{start_height},结束快高为：{end_height}，手动计算的收益为：{rewards}")
    #     assert user1_balances_end == user1_balances_start + Compute.to_u(
    #         number=user1_undel_amount) + rewards - self.base_cfg.fees
    #     # 查询区域委托
    #     vali_delegator2 = int(HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     # 断言现在的区域委托是否等于之前的-這一次减少的
    #     logger.info(
    #         f"开始是的节点委托金额为：{vali_delegator},结束后的节点委托金额为:{vali_delegator2},减少了委托{Compute.to_u(number=user1_undel_amount)}")
    #     assert vali_delegator2 == vali_delegator - Compute.to_u(number=user1_undel_amount)
    #
    #     # 用户2测试用例1 减少金额小于已有金额
    #     user2_undel_amount = 2
    #     start_height_user2 = HttpResponse.get_delegate_for_http(user_addr=user_addr2)['startHeight']
    #     un_delegate_data2 = dict(from_addr=user_addr2, amount=user2_undel_amount)
    #     end_height_user2 = int((self.test_del.test_undelegate_kyc(**un_delegate_data2))['height'])  # 减少用户2委托
    #     # # 查询user1的金额
    #     user2_balances_end = HttpResponse.get_balance_unit(user_addr=user_addr2)
    #     # # 手动计算收益，然后断言用户余额
    #     rewards_user2 = Reward.reward_kyc(stake=delegate_amount2, end_height=end_height_user2,
    #                                       start_height=start_height_user2)
    #     assert user2_balances_end == user2_balances_start + Compute.to_u(
    #         number=user2_undel_amount) + rewards_user2 - self.base_cfg.fees
    #     # # 查询区域委托
    #     vali_delegator3 = int(HttpResponse.get_validator_delegate(validator_addr=validator_addr)['delegation_amount'])
    #     assert vali_delegator3 == vali_delegator2 - Compute.to_u(number=user2_undel_amount)
    #     # 打扫数据，根据addr删除用户
    #     self.test_key.test_delete_key(addr=user_addr1)
    #     self.test_key.test_delete_key(addr=user_addr2)

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

    # @pytest.mark.skip
    # def test_withdrw_rewards_wang(self):
    #     """只提取活期收益，计算收益是否符合当前产生的收益1 failed, 23 passed, 62 deselected"""
    #     pass
    #
    # @pytest.mark.skip
    # def test_deposit_fixed(self):
    #     """测试发起定期委托，返回用户地址，委托id"""
    #     pass
    #
    # @pytest.mark.skip
    # def test_withdraw_fixed(self):
    #     """测试赎回定期委托，且计算收益。这里可以两种情况都写，一个到期一个未到期，用上面的发起委托的接口返回出来的用户地址，委托id作为入参"""
    #     pass
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
#     pytest.main(["-k", "./test_delegate.py::TestRegionDelegate::test_two_kyc_user_delegate", "--capture=no"])
