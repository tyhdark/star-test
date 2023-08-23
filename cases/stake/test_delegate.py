# -*- coding: utf-8 -*-
import inspect
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.parse_response import HttpResponse
from x.query import Query, HttpQuery
from x.tx import Tx
from tools.compute import Compute


# 单元测试delegate模块

class TestDelegate(object):
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

    @pytest.fixture(scope="class")
    def setup_class_get_kyc_user_info(self):
        """
        :return: user_addr, user_no_kyc_addr
        """

        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info
        time.sleep(self.tx.sleep_time)

        user_no_kyc_info = self.test_key.test_add()
        user_no_kyc_addr = user_no_kyc_info['address']
        time.sleep(self.tx.sleep_time)

        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1) * 2)  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        time.sleep(self.tx.sleep_time)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_no_kyc_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        logger.info("TestDelegate/get_kyc_user_info----------------->创建数据")
        time.sleep(self.tx.sleep_time)

        # 创建没有余额的账户
        user_no_kyc_info = self.test_key.test_add()
        user_no_kyc_addr = user_no_kyc_info['address']

        yield user_addr, user_no_kyc_addr

        # 删除用户
        self.test_key.test_delete_key(user_addr)
        self.test_key.test_delete_key(user_no_kyc_addr)
        logger.info("TestDelegate/get_kyc_user_info----------------->删除数据")

    @pytest.fixture(scope="class")
    def setup_no_kyc_no_balance_data(self):
        user_info = self.test_key.test_add()
        user_addr = user_info['address']
        time.sleep(self.tx.sleep_time)
        logger.info("TestDelegate/setup_no_kyc_no_balance_data----------------->创建数据")
        yield user_addr
        self.test_key.test_delete_key(user_addr)
        logger.info("TestDelegate/setup_no_kyc_no_balance_data----------------->删除数据")

    @pytest.mark.parametrize("error_data", (("", -10), ("xxx", "xx"), ("??", "-1.1")))
    def test_error_delegate(self, setup_class_get_kyc_user_info, error_data):
        """
        错误传参数的活期委托
        """
        user_addr, user_no_kyc_addr = setup_class_get_kyc_user_info
        # 断言 错误的地址返回Error
        del_data = dict(from_addr=error_data[0], amount=10)
        resp = self.tx.staking.delegate(**del_data)
        assert "Error" in resp

        # 断言 错误的活期委托金额
        del_data = dict(from_addr=user_addr, amount=error_data[1])
        resp = self.tx.staking.delegate(**del_data)
        assert "Error" in resp

    @pytest.mark.parametrize("balance_data", (1, 10, 20))
    def test_no_kyc_no_balance_delegate(self, setup_no_kyc_no_balance_data, balance_data):
        """
        新创建的用户，没有kyc，没有余额时进行活期委托
        """
        logger.info("TestDelegate/test_no_kyc_no_balance_delegate")
        user_addr = setup_no_kyc_no_balance_data

        # 没有余额的情况下进行活期委托 委托10 命令应该错误
        del_data = dict(from_addr=user_addr, amount=balance_data)
        resp = self.tx.staking.delegate(**del_data)
        # 断言 找不到活期委托的数据
        assert "NotFound" in resp

    # def test_no_kyc_no_balance_delegate(self):
    #     """
    #     新创建的用户，没有kyc，没有余额时进行活期委托
    #     """
    #     logger.info("TestDelegate/test_no_kyc_no_balance_delegate")
    #     user_info = self.test_key.test_add()
    #     user_addr = user_info['address']
    #     # 查询当前用户是不是没有余额
    #     user_balance = HttpResponse.get_balance_unit(user_addr)
    #     assert user_balance == 0
    #
    #     # 没有余额的情况下进行活期委托 委托10 命令应该错误
    #     assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=10))
    #
    #     # 传入金额为0 命令应该错误
    #     assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=0))
    #
    #     # 传入金额为-1 命令应该错误
    #     assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-1))
    #
    #     # 传入金额为-10 命令应该错误
    #     assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-10))
    #
    #     # 传入错误的地址
    #     assert self.error_delegation(del_data=dict(from_addr="xxyy", amount=10))
    #
    #     # 传入空地址
    #     assert self.error_delegation(del_data=dict(from_addr="", amount=10))
    #
    #     # 传入空金额
    #     assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=""))
    #
    #     # 再次查询当前用户余额 应该是0
    #     user_balance = HttpResponse.get_balance_unit(user_addr)
    #     assert user_balance == 0
    #
    #     # 查询用户的活期委托 ： 这里应该还404找不到委托数据
    #     status_code = self.delegation(addr=user_addr).status_code
    #     assert status_code == 404
    #
    #     # 删除用户
    #     self.test_key.test_delete_key(user_addr)

    def test_no_kyc_have_balance_delegate(self):
        """
        新创建的用户，没有kyc，有余额时进行活期委托
        """
        logger.info("TestDelegate/test_no_kyc_have_balance_delegate")
        user_info = self.test_key.test_add()
        user_addr = user_info['address']

        # 管理员给用户转100块
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        # 查询用户的余额
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount)

        # 传入金额为0 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=0))

        # 传入金额为-1 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-1))

        # 传入金额为-10 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-10))

        # 传入错误的地址
        assert self.error_delegation(del_data=dict(from_addr="xxyy", amount=10))

        # 传入大于余额的金额时 返回tx的code=5 这个时候扣除了手续费
        resp = self.tx.staking.delegate(from_addr=user_addr, amount=110)
        time.sleep(self.tx.sleep_time)
        tx_resp = self.q.tx.query_tx(resp['txhash'])
        assert tx_resp['code'] == 5

        # 传入等于余额的金额时 返回tx的code=5 这个时候扣除了手续费  这里要扣掉上面交易的手续费
        resp = self.tx.staking.delegate(from_addr=user_addr,
                                        amount=100 - Compute.to_u(self.base_cfg.fees, reverse=True))
        time.sleep(self.tx.sleep_time)
        tx_resp = self.q.tx.query_tx(resp['txhash'])
        assert tx_resp['code'] == 5

        # 查询用户的余额 100 - 10 -手续费*2
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount) - self.base_cfg.fees * 2

        # 委托金额 < 余额-手续费 用户发起10委托
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount)
        self.test_del.test_delegate(**del_data)
        time.sleep(self.tx.sleep_time)

        # 查询用户的余额 100 - 10 -手续费*3 = 999900  上次失败的委托也扣除了手续费这里记得减掉
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - self.base_cfg.fees * 3

        # 当前活期委托数据应该等于委托数据
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount)

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def test_no_kyc_un_delegate(self):
        """
        新创建的用户，没有kyc，有活期委托 进行赎回操作
        """
        logger.info("TestDelegate/test_no_kyc_un_delegate")
        user_info = self.test_key.test_add()
        user_addr = user_info['address']

        # 管理员给用户转100块
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)

        # 用户发起10块钱质押
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount)
        self.test_del.test_delegate(**del_data)
        time.sleep(self.tx.sleep_time)
        # 查询用户的余额 100 - 10 -手续费 = 999900
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - self.base_cfg.fees

        # 赎5的回活期委托
        un_del_amount = 5
        un_del_data = dict(from_addr=user_addr, amount=un_del_amount)
        self.test_del.test_undelegate_nokyc(**un_del_data)
        time.sleep(self.tx.sleep_time)

        # 当前活期委托数据应该等于委托数据
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == Compute.to_u(delegate_amount - un_del_amount)

        # 赎超过活期的委托
        un_del_amount = 100
        un_del_data = dict(from_addr=user_addr, amount=un_del_amount)
        self.test_del.test_undelegate_nokyc(**un_del_data)
        time.sleep(self.tx.sleep_time)

        # 超过金额应该被全部赎回 当前活期委托数据应该等于0
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unKycAmount']) == 0

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def test_kyc_have_balance_delegate(self):
        """新创建的用户，做了kyc，有余额时进行活期委托"""
        logger.info("TestDelegate/test_kyc_have_balance_delegate")
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info
        time.sleep(self.tx.sleep_time)
        # 查询当前用户是不是没有余额
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == 0

        # 管理员给用户转100块
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        time.sleep(self.tx.sleep_time)

        # 传入金额为0 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=0))

        # 传入金额为-1 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-1))

        # 传入金额为-10 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-10))

        # 传入错误的地址
        assert self.error_delegation(del_data=dict(from_addr="xxyy", amount=10))

        # 传入空地址
        assert self.error_delegation(del_data=dict(from_addr="", amount=10))

        # 传入空金额
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=""))

        # 用户发起大于余额的委托
        resp = self.tx.staking.delegate(from_addr=user_addr, amount=110)
        time.sleep(self.tx.sleep_time)
        tx_resp = self.q.tx.query_tx(resp['txhash'])
        assert tx_resp['code'] == 5

        # 用户发起等于余额的委托
        user_balance = HttpResponse.get_balance_unit(user_addr)
        resp = self.tx.staking.delegate(from_addr=user_addr, amount=user_balance)
        time.sleep(self.tx.sleep_time)
        tx_resp = self.q.tx.query_tx(resp['txhash'])
        assert tx_resp['code'] == 5

        # 委托金额 < 余额-手续费 用户发起10块钱委托
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount)
        self.test_del.test_delegate(**del_data)
        time.sleep(self.tx.sleep_time)

        # 当前活期委托数据应该等于委托数据
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['amount']) == Compute.to_u(delegate_amount)

        # 当前用户余额是
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - self.base_cfg.fees * 3

        # 当前活期委托数据应该是10
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['amount']) == Compute.to_u(10)

        # 当前不可提取的活期委托 应该是1 这是kyc认证后送的
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unmovable']) == Compute.to_u(1)

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def test_kyc_no_balance_delegate(self):
        """新创建的用户，做了kyc，没有余额时进行活期委托"""
        logger.info("TestDelegate/test_kyc_no_balance_delegate")
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info
        time.sleep(self.tx.sleep_time)

        # 查询当前用户是不是没有余额
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == 0

        # 管理员给用户转100块
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        time.sleep(self.tx.sleep_time)

        # 没有余额的情况下进行活期委托 委托10  返回：code=1144
        # raw_log'0umec is smaller than 10umec: insufficient funds: send coins to node validator  error'
        del_data = dict(from_addr=user_addr, amount=10)
        assert 1144 == self.tx.staking.delegate(**del_data)['code']

        # 传入金额为0 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=0))

        # 传入金额为-1 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-1))

        # 传入金额为-10 命令应该错误
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=-10))

        # 传入错误的地址
        assert self.error_delegation(del_data=dict(from_addr="xxyy", amount=10))

        # 传入空地址
        assert self.error_delegation(del_data=dict(from_addr="", amount=10))

        # 传入空金额
        assert self.error_delegation(del_data=dict(from_addr=user_addr, amount=""))

        # 再次查询当前用户余额 应该是0
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == 0

        # 当前活期委托数据应该是0
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['amount']) == 0

        # 当前不可提取的活期委托 应该是1 这是kyc认证后送的
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unmovable']) == Compute.to_u(1)

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def test_kyc_un_delegate(self):
        """
        新创建的用户，有kyc，有活期委托 进行赎回操作
        """
        logger.info("TestDelegate/test_kyc_un_delegate")
        user_info = self.test_kyc.test_new_kyc_user()
        user_addr = user_info

        time.sleep(self.tx.sleep_time)

        # 管理员给用户转100块
        send_amount = 100
        self.base_cfg.Bank.send_to_admin(amount=(send_amount + 1))  # 怕管理员没钱，国库先转钱给管理员
        time.sleep(self.tx.sleep_time)
        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr, amount=send_amount)
        self.test_bank.test_send(**send_data)
        time.sleep(self.tx.sleep_time)

        # 用户发起10块钱质押
        delegate_amount = 10
        del_data = dict(from_addr=user_addr, amount=delegate_amount)
        self.test_del.test_delegate(**del_data)
        time.sleep(self.tx.sleep_time)

        # 查询用户的余额 100 - 10 -手续费 = 999900
        user_balance = HttpResponse.get_balance_unit(user_addr)
        assert user_balance == Compute.to_u(send_amount - delegate_amount) - self.base_cfg.fees

        # 赎5的回活期委托
        un_del_amount = 5
        un_del_data = dict(from_addr=user_addr, amount=un_del_amount)
        self.test_del.test_undelegate_kyc(**un_del_data)
        time.sleep(self.tx.sleep_time)

        # 当前活期委托数据应该等于委托数据
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['amount']) == Compute.to_u(delegate_amount - un_del_amount)

        # 赎超过活期的委托    "code": 53, "raw_log": "failed to execute message;
        # message index: 0: Validator DelgationAmount \u003c 0.",
        un_del_amount = 100
        un_del_data = dict(from_addr=user_addr, amount=un_del_amount)
        un_del_resp = self.tx.staking.undelegate_kyc(**un_del_data)
        time.sleep(self.tx.sleep_time)
        un_del_resp_tx = un_del_resp['txhash']
        resp = self.hq.tx.query_tx(un_del_resp_tx)
        assert 53 == resp['code']

        # 超过金额应该被全部赎回没成功，所以活期委托还是10-5 = 5
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['amount']) == Compute.to_u(delegate_amount - un_del_amount)

        # 当前不可提取的活期委托 应该是1 这是kyc认证后送的
        user_delegate_info = HttpResponse.get_delegate(user_addr)
        assert int(user_delegate_info['unmovable']) == Compute.to_u(1)

        # 删除用户
        self.test_key.test_delete_key(user_addr)

    def delegation(self, addr=None):
        """
        查询委托信息
        :param addr: 传入addr 查询某个地址委托,不传查询所有委托
        """
        url = HttpQuery.api_url + HttpQuery.query_delegation.format(delegator_addr=addr)
        logger.info(f"{inspect.stack()[0][3]}: {url}")
        response = HttpQuery.client.get(url=url)
        logger.info(f"response: {response}")
        return response

    def error_delegation(self, del_data=None):
        """
        处理异常情况下的delegation请求
        如果Error存在于返回的数据里 则返回True,否则返回False
        :param del_data:
        :return: True = 是有错误，False = 没有错误
        """
        if "Error" in self.tx.staking.delegate(**del_data):
            return True
        else:
            return False
