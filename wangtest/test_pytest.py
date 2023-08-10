import os

from loguru import logger
import pytest
import allure


class TestLogin():

    def setup_class(self):
        print("============这是执行测试前执行的方法，类级别setup===========")

    def test_login01(self):
        print("---test_login01----")
        assert 1 + 1 == 2

    def test_login02(self):
        logger.info("---test_login02----")
        print("---test_login02----")
        assert 1 + 2 == 3

    def teardown(self):
        print("=============这是执行测试后执行的方法，方法级别的teardown==========")


if __name__ == '__main__':
    # pytest.main(["test_func01.py", "-s", "-q", "--alluredir", "../report/tmp"])  # 框架自己调用函数　　需要打印对应的信息，需要在列表里面加-s
    # os.system("allure serve ../report/tmp")
    os.system("pytest ./wangtest/test_pytest.py -s -q --alluredir=./report/tmp")
    os.system("")
    # print(os.system("ls"))
