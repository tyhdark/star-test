# -*- coding: utf-8 -*-
import inspect
import os

import pytest
import time
from loguru import logger
# from config import chain
# from tools import handle_query
# from tools import handle_resp_data
from x.query import Query,HttpQuery
from x.tx import Tx
from tools.rewards import Reward



class TestMe(object):
    tx = Tx()
    # key = Tx.Keys()
    q = Query()
    http_query = HttpQuery()
    reward = Reward()
    # handle_q = handle_query.HandleQuery()
    # def setup_class(self):
    #     print("类级别的前置")
    # def teardown_class(self):
    #     print("类级别的后置")
    # def setup(self):
    #     print("每次用例前置执行")
    # def teardown(self):
    #     print("每次用例后置执行")

    # @pytest.mark.skip
    def test_001(self):
        """
        测试pytest有没有用，1+2=3
        """
        assert 1 + 2 == 3

    # @pytest.mark.skip
    def test_002(self):
        """
        测试pytest有没有用，1+3=4
        """
        assert 1 + 3 == 4

    # @pytest.mark.skip
    def test_003(self):
        """
        测试pytest有没有用，在不在列表
        """
        l = [1, 2, 3, 5, 6, 7, 8, 9]
        print("试一下是会跳过这条用例的断言还是该函数方法，如果出现了这个字段，就是通过测试断言")
        assert 3 in l

    @pytest.mark.skip
    def test_add_user_004(self):
        """测试创建用户是否成功"""
        user_name = "testnamekyc003"
        self.tx.Keys.add(username=user_name)
        name_list = self.q.Key.keys_list()
        name_user_list = [i.get('name') for i in name_list]

        logger.info(f"{inspect.stack()[0][3]}:{name_user_list}")
        assert user_name in name_user_list

    @pytest.mark.skip
    def test_send_to_admin_005(self):
        # 先查询管理员余额，
        amout = 100000
        super_adder = self.tx.super_addr
        start_balances= self.http_query.Bank.query_balances(addr=super_adder)
        logger.info(start_balances)
        # 发起转账
        self.tx.bank.send_to_admin(amout=amout)
        # 等待出块
        self.tx.Wait.wait_five_seconds()
        # 再查询管理员余额
        end_balances= self.http_query.Bank.query_balances(addr=super_adder)
        logger.info(end_balances)
        # 断言
        assert end_balances == start_balances + (amout*(10**6)) - 100

    @pytest.mark.skip
    def test_admin_send_to_user_006(self):
        """管理员给用户转钱"""
        amount = 100000
        user = "testname011"
        super_name = "superadmin"
        # 获取用户地址
        addre = Query.Key.address_of_name(username=user)
        super_addr = Query.Key.address_of_name(username=super_name)
        # 先查询用户余额，
        start_balances = self.http_query.Bank.query_balances(addr=addre)
        # 发起转账
        self.tx.Bank.send_tx(from_addr=super_addr,to_addr=addre,amount=amount)
        # 等待出块
        self.tx.Wait.wait_five_seconds()
        # 再查询用户余额
        end_balances = self.http_query.Bank.query_balances(addr=addre)
        # 断言
        assert end_balances==start_balances + (amount*(10**6))

    @pytest.mark.skip
    def test_create_validator_007(self):
        """
        新增验证者节点的测试
        """
        node_name = 'node4'
        amount = 50000000
        # 创建验证者节点
        self.tx.Staking.create_validator(node_name=node_name,amout=amount)
        # 等待出块后
        self.tx.Wait.wait_five_seconds()
        # 查询验证者节点
        # node_list = self.http_query.Staking.validator()
        # 解析数据
        # nade_name_list = []  # 新建空列表等下用来接收查询出来的全部node_name
        # for i in nade_dict.get('validators'):
        # nade_name_list.append(i.get('description').get('moniker')) # # 追加进这个空列表里面

        # node_name_list = [i.get('description').get('moniker') for i in node_list]  # 用推导式的写法
        # logger.info(node_name_list)
        # print(node_name_list)
        # 判断自己新建的节点在不在查询的表里面
        assert node_name in [i.get('description').get('moniker') for i in self.http_query.Staking.validator()]

    @pytest.mark.skip
    def test_create_region_008(self):
        """
        区绑定对应的节点

        """
        node_name = "node4"
        region_name = "KOR"


        # 将区绑定到对应的节点
        self.tx.Staking.create_region(from_addr=self.tx.super_addr,region_name=region_name,node_name=node_name)
        # 等待出块
        self.tx.Wait.wait_five_seconds()
        # 查询区有没有在区列表里面
        # region_dict = self.http_query.Staking.region()
        # 遍历出区域名称，
        region_name_list = [i.get('name') for i in self.http_query.Staking.region().get('region')]
        logger.info(f"{inspect.stack()[0][3]}: {region_name_list}")
        assert region_name in region_name_list

    @pytest.mark.skip
    def test_new_kyc_009(self):
        """
        测试普通用户是否可以newkyc成功
        """
        user_name = "testnamekyc003"
        region_id = "jpn"
        addr = self.q.Key.address_of_name(username=user_name)
        logger.info(f"{inspect.stack()[0][3]}: {addr}")


        # 认证KYC
        self.tx.Staking.new_kyc(user_addr=addr,region_id=region_id,from_addr=self.tx.super_addr)
        self.tx.Wait.wait_five_seconds()
        # 查询用户地址，

        # 查询KYC列表
        kyc_list = self.http_query.Staking.kyc()
        kyc_address_list = [i.get('account') for i in kyc_list.get('kyc')]  # 遍历出来KYC用户地址
        logger.info(f"{inspect.stack()[0][3]}:{kyc_address_list}")
        # 断言是否在KYC列表里面
        # assert addr in kyc_address_list
        assert addr in kyc_address_list


    @pytest.mark.skip
    def test_staking_nokyc_delegate_010(self):
        """
        非KYC活期委托测试用例
        """
        test_name = "testname011"
        addr = self.q.Key.address_of_name(username=test_name)
        delegate_amount = 10000
        fee = self.tx.fees
        start_balances = self.http_query.Bank.query_balances(addr=addr)
        logger.info(f"{inspect.stack()[0][3]}用户发起委托前的余额为: {start_balances}")
        # print("用户发起委托前的余额为：", start_balances)
        # 1 发起活期委托
        self.tx.Staking.delegate(from_addr=addr,amount=delegate_amount)
        self.tx.Wait.wait_five_seconds()
        time.sleep(2)
        # 2 查询用户委托出去时，自己的余额

        # print(type(start_balances))

        # 3 查询当前活期委托
        start_height = self.http_query.Staking.delegation(addr=addr).get('startHeight')
        logger.info(f"{inspect.stack()[0][3]}开始委托时的快高为: {start_height}")
        print("开始委托时的快高为：", start_height)
        self.tx.Wait.wait_five_seconds()
        self.tx.Wait.wait_five_seconds()
        self.tx.Wait.wati_five_height()

        # 4 赎回活期委托
        end_hash = self.tx.Staking.undelegate_nokyc(amount=delegate_amount,from_addr=addr).get('txhash')
        time.sleep(5)
        end_height  = int(self.http_query.Tx.query_tx(tx_hash=end_hash).get('height'))

        self.tx.Wait.wait_five_seconds()
        print(end_height,type(end_height))
        # 5 查询委托结束时的余额
        end_balances = self.http_query.Bank.query_balances(addr=addr)
        logger.info(f"{inspect.stack()[0][3]}委托赎回后，用户的余额为: {end_balances}")
        print("委托赎回后，用户的余额为：", end_balances)
        # 6 非KYC用户的收益 = 结束余额 - 开始余额
        rewards = (end_balances - (start_balances - (delegate_amount*(10**6))-fee-fee))
        logger.info(f"{inspect.stack()[0][3]}用户扣两次手续费后实际到账的收益为: {rewards}")
        print("用户扣两次手续费后实际到账的收益为：", rewards)
        # 7 手动计算块高和收益，结束时的块高 - 开始时的块高
        course_height = end_height - start_height
        logger.info(f"{inspect.stack()[0][3]}经历的块高为: {course_height}")
        print("经历的块高为：",course_height)
        # 7.2 根据块高收益
        re = self.reward.reward_nokyc(stake=delegate_amount,end_height=end_height,start_height=start_height)
        logger.info(f"{inspect.stack()[0][3]}手动计算的收益为: {re}")

        # 8 判断余额差值是否等于手动计算的收益
        assert rewards == re

    @pytest.mark.skip
    def test_staking_kyc_delegate_011(self):
        """KYC用户活期委托测试用例"""
        test_name = "testnamekyc001"
        addr = self.q.Key.address_of_name(username=test_name)
        delegate_amount = 100000
        fee = self.tx.fees
        # 1 发起活期委托
        self.tx.Staking.delegate(from_addr=addr,amount=delegate_amount)
        self.tx.Wait.wait_five_seconds()
        time.sleep(2)
        # 2、查询发起后的余额是多少
        start_balances = self.http_query.Bank.query_balances(addr=addr)
        logger.info(f"{inspect.stack()[0][3]}用户发起委托后的余额为: {start_balances}")
        # print("用户发起委托后的余额为：", start_balances)
        # 3 查询当前活期委托 且获得开始委托时的块高。
        start_height = self.http_query.Staking.delegation(addr=addr).get('startHeight')
        logger.info(f"{inspect.stack()[0][3]}开始委托时的快高为: {start_height}")
        # print("开始委托时的快高为：", start_height)
        self.tx.Wait.wait_five_seconds()
        self.tx.Wait.wait_five_seconds()
        self.tx.Wait.wati_five_height()

        # 4 赎回活期委托
        end_hash = self.tx.Staking.undelegate_kyc(amount=delegate_amount,from_addr=addr).get('txhash')
        time.sleep(5)
        end_height  = int(self.http_query.Tx.query_tx(tx_hash=end_hash).get('height'))

        self.tx.Wait.wait_five_seconds()
        print(end_height,type(end_height))
        # 5 查询委托结束时的余额
        end_balances = self.http_query.Bank.query_balances(addr=addr)
        logger.info(f"{inspect.stack()[0][3]}委托赎回后用户的余额为: {end_balances}")
        print("委托赎回后用户的余额为：", end_balances)
        # 6 非KYC用户的收益 = 结束余额 - 开始余额
        rewards = (end_balances - (start_balances+(delegate_amount*(10**6))-fee))
        logger.info(f"{inspect.stack()[0][3]}用户扣两次手续费后实际到账的收益为: {rewards}")
        print("用户扣两次手续费后实际到账的收益为：", rewards)
        # 7 手动计算块高和收益，结束时的块高 - 开始时的块高
        course_height = end_height - start_height
        logger.info(f"{inspect.stack()[0][3]}经历的块高为: {course_height}")
        print("经历的块高为：",course_height)
        # 7.2 根据块高收益
        re = self.reward.reward_kyc(stake=delegate_amount,end_height=end_height,start_height=start_height)
        logger.info(f"{inspect.stack()[0][3]}手动计算的收益为: {re}")
        print("手动计算的收益为：",re,type(re))

        # 8 判断余额差值是否等于手动计算的收益
        assert rewards == re

    @pytest.mark.skip
    def test_fixed_delegate_012(self):
        """
        设计发起定期委托的用例,先查询用户定期委托和全网定期委托，
        发起委托后，再查用户定期委托和全网委托，进行比较，另外再校验code是否等于0

        """

        user_name = "testnamekyc002"
        amount = 100
        month = 12
        addr = self.q.Key.address_of_name(username=user_name)
        fixed_list_all = self.http_query.Staking.fixed_deposit()  # 查询所有定期列表
        list_id_start = [i.get('id') for i in fixed_list_all]  # 发起定期委托前的所有定期委托id列表
        logger.info(f"{inspect.stack()[0][3]}发起定期委托前的所有定期委托id列表: {list_id_start}")
        # print("发起定期委托前的所有定期委托id列表",list_id_start)
        fixed_list_user_start = self.http_query.Staking.fixed_deposit(addr=addr)  # 发起定期委托前的个人定期委托列表
        list_id_user_start = [i.get('id') for i in fixed_list_user_start]
        logger.info(f"{inspect.stack()[0][3]}发起定期委托前的个人定期委托列表: {list_id_user_start}")
        print("发起定期委托前的个人定期委托列表",list_id_user_start)
        # 开始发起个人委托
        logger.info(f"{inspect.stack()[0][3]}: {self.tx.Staking.deposit_fixed(from_addr=addr,amount=amount,month=month)}")
        self.tx.Wait.wait_five_seconds()
        # 查询对应的费率时多少
        rate = float(self.http_query.Staking.fixed_deposit_rate(month=month))

        # 手动计算收益是多少
        reward = self.reward.fixed_reward(rate=rate,month=month,amount=amount)
        logger.info(f"{inspect.stack()[0][3]}手动计算的收益为: {reward}")
        print("手动计算的收益为：",reward)
        # 委托结束后，查询列表
        fixed_list_all_end = self.http_query.Staking.fixed_deposit()  # 查询委托后的所有定期列表
        list_id_end = [i.get('id') for i in fixed_list_all_end]  # 查询所有定期列表id
        # print("发起定期委托前的所有定期委托id列表", list_id_end)
        fixed_list_user_end = self.http_query.Staking.fixed_deposit(addr=addr)  # 发起定期委托前的个人定期委托列表
        list_id_user_end = [i.get('id') for i in fixed_list_user_end]

        assert len(list_id_user_end) == len(list_id_user_start) + 1
        assert len(list_id_end) == len(list_id_start) + 1
        # assert code == 0


if __name__ == '__main__':
    # pytest.main([ "-s","./testwang.py", "--log-level=debug",  "--capture=no","--alluredir=../report/wangtest", "--clean-alluredir"])
    # pytest.main(['-s', './'])
    print(os.path())
    # cmd 命令
    # pytest -s ./wangtestcase/testwang.py  --log-level=debug  --alluredir=./wangtestcase/report  --clean-alluredir
    # allure serve ./wangtestcase/report