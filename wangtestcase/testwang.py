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

    def test03(self):
        l = [1, 2, 3, 5, 6, 7, 8, 9]
        assert 3 in l

    def test004(self):
        name = "testname01"
        # self.tx.Keys.add(username=name)
        # time.sleep(5)
        name_list = self.tx.Keys.lists_test()
        # print(name_list)
        assert name in name_list



if __name__ == '__main__':
    # pytest.main(["./testwang.py", "-s", "--log-level=debug", "--alluredir=../report/wangtest", "--clean-alluredir"])
    pytest.main(["./testwang.py"])
