# -*- coding: utf-8 -*-
import pytest
import time
from loguru import logger
# from config import chain
from tools import handle_query
from tools import handle_resp_data
from x.query import Query
from x.tx import Tx


class TestMe(object):
    tx = Tx()
    # key = Tx.Keys()
    q = Query()

    # handle_q = handle_query.HandleQuery()
    # def setup_class(self):
    #     print("类级别的前置")
    # def teardown_class(self):
    #     print("类级别的后置")
    # def setup(self):
    #     print("每次用例前置执行")
    # def teardown(self):
    #     print("每次用例后置执行")

    @pytest.mark.skip
    def test01(self):
        assert 1 + 2 == 3

    @pytest.mark.skip
    def test02(self):
        assert 1 + 3 == 4

    @pytest.mark.skip
    def test03(self):
        l = [1, 2, 3, 5, 6, 7, 8, 9]
        print("试一下是会跳过这条用例的断言还是该函数方法，如果出现了这个字段，就是跳过测试断言")
        assert 3 in l

    @pytest.mark.skip
    def test004(self):
        """测试创建用户是否成功"""
        name = "testname004"
        self.tx.Keys.add(username=name)
        self.tx.SendToAdmin.count_down_5s()
        name_list = self.tx.Keys.lists_test()
        name_user_list = []
        # for i in name_list:
        #     name_user= i.get('name')
        #     name_user_list.append(name_user)
        #     return name_user_list

        print(name_list)
        assert name in name_list

    @pytest.mark.skip
    def test_send_bank_005(self):
        testusername = "testname002"
        test_amouts = 1
        fees = 100
        # 查询用户余额先 拿到原有的余额 应该是0
        testusername_balances = self.tx.Query.query_bank_balance_username(username=testusername)
        print(testusername_balances)
        print(type(testusername_balances))
        # 第二： 发起转账
        self.tx.SendToAdmin.send_admin_to_user(to_account=testusername, amounts=test_amouts, fees=fees)
        # 第三： 等待几秒钟再查
        self.tx.SendToAdmin.count_down_5s()
        time.sleep(2)
        # 第四：查询余额
        testusername_balances_later = self.tx.Query.query_bank_balance_username(username=testusername)
        # 第五，将转账之后的余额，减去转账之前的余额，等于一个差值，
        result = testusername_balances_later - testusername_balances
        # mec转换单位umec
        test_amouts_u = test_amouts * 10 ** 6
        # 最后 校验这个差值，是否等于转账金额
        assert result == test_amouts_u

    @pytest.mark.skip
    def test_staking_nokyc_delegate_006(self):
        """
        非KYC活期委托测试用例

        """
        test_name = "testname002"
        delegate_amount = 10000
        self.tx.Staking.delegate(amount=delegate_amount, username=test_name, fees=100)  # 1 发起活期委托
        self.tx.SendToAdmin.count_down_5s()
        time.sleep(2)
        start_balances = self.tx.Query.query_bank_balance_username(username=test_name)  # 2 查询用户委托出去时，自己的余额
        print("用户发起委托后的余额为：", start_balances)
        print(type(start_balances))
        self.tx.SendToAdmin.count_down_5s()
        self.tx.SendToAdmin.count_down_5s()
        self.tx.SendToAdmin.count_down_5s()
        self.tx.SendToAdmin.count_down_5s()
        start_height = self.tx.Query.query_staking_delegate_start_height(username=test_name)  # 3 查询当前活期委托
        print("开始委托时的快高为：", start_height)
        print(type(start_height))
        end_hash = self.tx.Staking.delegate_unkycunbond_txhash(amount=delegate_amount, username=test_name,
                                                               fees=100)  # 4 赎回活期委托
        end_height = self.tx.Query.query_tx_height(hash_value=end_hash)
        print("结束委托时的块高为：", end_height)
        self.tx.SendToAdmin.count_down_5s()
        end_balances = self.tx.Query.query_bank_balance_username(username=test_name)  # 5 查询委托结束时的余额
        print("委托赎回后，用户的余额为：", end_balances)
        rewards = end_balances - start_balances  # 6 非KYC用户的收益 = 结束余额 - 开始余额
        print("用户实际到账的收益为：", rewards)

        course_height = end_height - start_height  # 7 手动计算块高和收益，结束时的块高 - 开始时的块高
        count_rewards = self.tx.Bank.rewards_nokyc_for_course_height_amount(amount=delegate_amount,
                                                                            course_height=course_height)  # 7.2 根据块高收益
        print("手动计算的收益为：", count_rewards)

        # 8 判断余额差值是否等于手动计算的收益
        assert rewards == count_rewards

    @pytest.mark.skip
    def test_staking_kyc_delegate_007(self):
        """KYC用户活期委托测试用例"""
        test_name = "testnamekyc002"
        delegate_amount = 100
        # 1、发起活期委托
        self.tx.Staking.delegate(amount=delegate_amount, username=test_name, fees=100)  # 1 发起活期委托
        self.tx.SendToAdmin.count_down_5s()
        time.sleep(2)
        # 2、查询用户委托出去后，自己的余额
        start_balances = self.tx.Query.query_bank_balance_username(username=test_name)  # 2 查询用户委托出去时，自己的余额
        print("用户发起委托后的余额为：", start_balances)
        print(type(start_balances))
        self.tx.SendToAdmin.count_down_5s()
        # self.tx.SendToAdmin.count_down_5s()
        # self.tx.SendToAdmin.count_down_5s()
        self.tx.SendToAdmin.count_down_5s()
        # 3、查询当前活期委托
        start_height = self.tx.Query.query_staking_delegate_start_height(username=test_name)  # 3 查询当前活期委托
        print("开始委托时的快高为：", start_height)
        print(type(start_height))
        # 4、赎回活期委托
        end_hash = self.tx.Staking.delegate_kycunbond_txhash(amount=delegate_amount, username=test_name, fees=100)
        end_height = self.tx.Query.query_tx_height(hash_value=end_hash)
        print("结束委托时的块高为：", end_height)
        self.tx.SendToAdmin.count_down_5s()
        end_balances = self.tx.Query.query_bank_balance_username(username=test_name)  # 5 查询委托结束时的余额
        print("委托赎回后，用户的余额为：", end_balances)
        rewards = end_balances - (start_balances + (delegate_amount * 10 ** 6))  # 6 非KYC用户的收益 = 结束余额 - 开始余额
        print("用户实际到账的收益为：", rewards)
        # 7、手动计算块高和收益，结束时的块高-开始时的块高
        course_height = end_height - start_height  # 7 手动计算块高和收益，结束时的块高 - 开始时的块高
        # 7。2 根据块高计算收益
        count_rewards = self.tx.Bank.rewards_nokyc_for_course_height_amount(amount=delegate_amount,
                                                                            course_height=course_height)  # 7.2 根据块高收益
        # 8、 做断言，判断，实际收益是否等于预期收益
        print("手动计算的收益为：", count_rewards)

        assert rewards == count_rewards

    @pytest.mark.skip
    def test_bank_send(self):
        """用户转账测试用例"""
        from_name = "wangzhibiao001"
        to_name = "testname004"
        amounts = 1
        fees = 100
        # 查询A用户余额
        start_balances_from = self.tx.Query.query_bank_balance_username(username=from_name)
        print("转出用户开始余额", start_balances_from)
        print(type(start_balances_from))
        # 查询B用户余额
        start_balances_to = self.tx.Query.query_bank_balance_username(username=to_name)
        print("转入用户开始余额", start_balances_to)
        print(type(start_balances_to))
        # A用户给B用户转一笔金额
        self.tx.SendToAdmin.tx_bank_send(from_address_name=from_name, to_address_name=to_name, amounts=amounts,
                                         fees=fees)
        self.tx.SendToAdmin.count_down_5s()
        # 查询A用户余额
        end_balances_from = self.tx.Query.query_bank_balance_username(username=from_name)
        print("转出用户结束余额", end_balances_from)
        # 查询B用户余额
        end_balances_to = self.tx.Query.query_bank_balance_username(username=to_name)
        print("转入用户结束余额", end_balances_to)
        # 校验，转出用户的结束余额是否等于开始余额 - 转账金额，转入用户的结束余额是否等于开始余额 + 转账金额
        assert end_balances_from == (start_balances_from - (amounts * 10 ** 6) - fees)
        assert end_balances_to == start_balances_to + (amounts * 10 ** 6)


    # @pytest.mark.skip
    def test_create_vaildator(self):
        """
        新增验证者节点的测试
        """
        node_name = "node2"
        amount = 50000000
        fees = 100
        # 创建验证者节点
        self.tx.Staking.creation_validator_node(node_name=node_name, amounts=amount, fees=fees)
        self.tx.SendToAdmin.count_down_5s()
        # 查询验证者节点
        nade_dict = self.tx.Query.query_staking_validator()  # 用一个变量去接收查询出来的结果字典
        # nade_name_list = []  # 新建空列表等下用来接收查询出来的全部node_name
        # for i in nade_dict.get('validators'):
            # nade_name_list.append(i.get('description').get('moniker')) # # 追加进这个空列表里面

        node_name_list = [i.get('description').get('moniker') for i in (nade_dict.get('validators'))]  # 用推导式的写法
        assert node_name in node_name_list


    @pytest.mark.skip
    def test_create_region(self):
        """
        区绑定对应的节点

        """
        node_name = "node2"
        region_name = "USA"
        fees = 100
        # 将区绑定到对应的节点
        self.tx.Staking.new_region(region_name=region_name,node_name=node_name,fees=fees)
        self.tx.SendToAdmin.count_down_5s()
        # 查询区有没有在区列表里面
        region_dict = self.tx.Query.query_staking_list_region()
        # 遍历出区域名称，
        region_name_list = [i.get('name') for i in (region_dict.get('region'))]
        assert region_name in region_name_list


    @pytest.mark.skip
    def test_new_kyc(self):
        """
        测试普通用户是否可以newkyc成功
        """
        user_name = "testnamekyc002"
        region_name = "JPN"
        fees = 100
        # 认证KYC
        self.tx.Staking.new_kyc_for_username(user_name=user_name,region_name=region_name,fees=fees)
        self.tx.SendToAdmin.count_down_5s()
        # 查询用户地址，
        user_name_address = self.tx.Keys.show_address_for_username(username=user_name)
        # 查询KYC列表
        kyc_list = Tx.Query.query_staking_list_kyc()  # 查询KYC列表
        kyc_address_list = [i.get('account') for i in kyc_list.get('kyc')] # 遍历出来KYC用户地址
        # 断言是否在KYC列表里面
        assert user_name_address in kyc_address_list

    # TODO 设计发起定期委托 校验定期列表
    @pytest.mark.skip
    def test_fixed_delegate(self):
        """
        设计发起定期委托的用例

        """
        # 用户发起委托
        user_name = "testnamekyc002"
        amount = 100
        mouth = 3
        fees = 100
        self.tx.Staking.deposit_fixed(amount=amount,months=mouth,username=user_name,fees=fees)
        self.tx.SendToAdmin.count_down_5s()
        # 查询委托列表
        self.tx.Query.query_list_fixed_deposit()
        # 校验是否存在委托列表里面
        pass
if __name__ == '__main__':
    # pytest.main(["./testwang.py", "-s", "--log-level=debug", "--alluredir=../report/wangtest", "--clean-alluredir"])
    pytest.main(['-s', './'])
