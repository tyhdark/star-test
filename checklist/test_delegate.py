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







