# -*- coding: utf-8 -*-
import pytest
import time
from loguru import logger
# from config import chain
from tools import handle_query
from tools import handle_resp_data
from x.query import Query
from x.tx import Tx


@pytest.mark.P0
class TestMe(object):
    tx = Tx()
    # key = Tx.Keys()
    q = Query()

    # handle_q = handle_query.HandleQuery()

    def test01(self):
        assert 1 + 2 == 3

    def test02(self):
        assert 1 + 3 == 4

    @pytest.mark.skip
    def test03(self):
        l = [1, 2, 3, 5, 6, 7, 8, 9]
        print("试一下是会跳过这条用例的断言还是该函数方法，如果出现了这个字段，就是跳过测试断言")
        assert 3 in l

    @pytest.mark.skip
    def test004(self):
        name = "test005"
        # self.tx.Keys.add(username=name)
        # time.sleep(5)
        name_list = self.tx.Keys.lists_test()
        name_user_list = []
        # for i in name_list:
        #     name_user= i.get('name')
        #     name_user_list.append(name_user)
        #     return name_user_list

        print(name_list)
        assert name in name_list

    # TODO 设计给用户转账是否成功的测试用例
    @pytest.mark.skip
    def test_send_bank_005(self):
        testusername = "test003"
        test_amouts = 100
        # 查询用户余额先 拿到原有的余额 应该是0
        testusername_balances = self.tx.Query.query_bank_balance_username(username=testusername)
        print(testusername_balances)
        print(type(testusername_balances))
        # 第二： 发起转账
        self.tx.SendToAdmin.send_admin_to_user(to_account=testusername,amounts=100,fees=0)
        # 第三： 等待几秒钟再查
        self.tx.SendToAdmin.count_down_5s()
        time.sleep(2)
        # 第四：查询余额
        testusername_balances_later = self.tx.Query.query_bank_balance_username(username=testusername)
        # 第五，将转账之后的余额，减去转账之前的余额，等于一个差值，
        result = testusername_balances_later - testusername_balances
        # mec转换单位umec
        test_amouts_u = test_amouts * 10 **6
        # 最后 校验这个差值，是否等于转账金额
        assert result==test_amouts_u

    # TODO 设计发送活期是否成功，计算收益
    def test_staking_delegate(self):
        pass
        # 1 查询现有 余额
        # 2 发起活期委托
        # 3 赎回活期委托
        # 4 查询余额
        # 5 手动计算收益
        # 5 计算余额是否等于手动计算的收益


if __name__ == '__main__':
    # pytest.main(["./testwang.py", "-s", "--log-level=debug", "--alluredir=../report/wangtest", "--clean-alluredir"])
    pytest.main(["./testwang.py"])
