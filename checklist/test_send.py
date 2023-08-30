# -*- coding: utf-8 -*-
import time
# import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from functools import partial
from cases import unitcases
from tools.compute import Compute
from tools.parse_response import HttpResponse
import pytest

def operation1():
    # 模拟操作1
    print("Operation 1 started")
    # 进行一些操作
    print("Operation 1 completed")


def operation2():
    # 模拟操作2
    print("Operation 2 started")
    # 进行一些操作
    print("Operation 2 completed")


class TestSend(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    base_cfg = test_bank.tx

    @pytest.mark.test_0829
    def test_send_tow_user(self, creat_two_nokyc):
        """
        双用户，A给B转钱，B给A转钱。同一个块内互相转钱
        """
        # 创建两个用户
        user_addr_a, user_addr_b, balances = creat_two_nokyc
        time.sleep(7)
        # 转账数据定义
        send_data_1 = dict(from_addr=user_addr_a,
                           to_addr=user_addr_b, amount=1)
        send_data_2 = dict(from_addr=user_addr_b,
                           to_addr=user_addr_a, amount=2)

        partial_function = partial(self.test_bank.test_send, **send_data_1)
        partial_function2 = partial(self.test_bank.test_send, **send_data_2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 提交操作1和操作2到进程池中并发执行
            future1 = executor.submit(partial_function)
            future2 = executor.submit(partial_function2)
            #
            #     # 等待操作1和操作2执行完成
            future1.result()
            future2.result()

        # B给A转
        # 算账
        user_a_balances = HttpResponse.get_balance_unit(user_addr=user_addr_a)
        user_b_balances = HttpResponse.get_balance_unit(user_addr=user_addr_b)
        logger.info(f"user_1_balances ={user_a_balances}")
        logger.info(f"user_2_balances ={user_b_balances}")
        assert user_a_balances == balances - Compute.to_u(1) + Compute.to_u(2) - 100
        assert user_b_balances == balances - Compute.to_u(2) + Compute.to_u(1) - 100
        pass

    @pytest.mark.test_0829
    def test_send_tow_user_node(self, creat_two_kyc):
        """
        两个KYC双用户,不同的区，A给B转钱，B给A转钱。同一个块内互相转钱,指定不同的节点
        """
        # 创建两个用户
        user_addr_a, user_addr_b, balances = creat_two_kyc
        time.sleep(6)
        # 转账数据定义
        send_data_1 = dict(from_addr=user_addr_a,
                           to_addr=user_addr_b, amount=1, node_ip="localhost:26657")
        send_data_2 = dict(from_addr=user_addr_b,
                           to_addr=user_addr_a, amount=2, node_ip="localhost:14002")

        partial_function1 = partial(self.test_bank.test_send, **send_data_1)
        partial_function2 = partial(self.test_bank.test_send, **send_data_2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 提交操作1和操作2到进程池中并发执行
            future1 = executor.submit(partial_function1)
            future2 = executor.submit(partial_function2)
            #     # 等待操作1和操作2执行完成
            future1.result()
            future2.result()
        # B给A转
        # 算账
        user_a_balances = HttpResponse.get_balance_unit(user_addr=user_addr_a)
        user_b_balances = HttpResponse.get_balance_unit(user_addr=user_addr_b)
        logger.info(f"user_1_balances ={user_a_balances}")
        logger.info(f"user_2_balances ={user_b_balances}")
        assert user_a_balances == balances - Compute.to_u(1) + Compute.to_u(2) - 100
        assert user_b_balances == balances - Compute.to_u(2) + Compute.to_u(1) - 100
        pass

    @pytest.mark.test_0829
    def test_send_tow_user_node_fees(self, creat_two_kyc):
        """
        两个KYC双用户，A给B转钱，B给A转钱。同一个块内互相转钱,指定不同的节点,手续费差异
        """
        # 创建两个用户
        user_addr_a, user_addr_b, balances = creat_two_kyc
        time.sleep(6)
        # 转账数据定义
        send_data_1 = dict(from_addr=user_addr_a,
                           to_addr=user_addr_b, amount=1, fees=100, node_ip="localhost:26657")
        send_data_2 = dict(from_addr=user_addr_b,
                           to_addr=user_addr_a, amount=2, fees=200, node_ip="localhost:14007")

        partial_function1 = partial(self.test_bank.test_send, **send_data_1)
        partial_function2 = partial(self.test_bank.test_send, **send_data_2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 提交操作1和操作2到进程池中并发执行
            future1 = executor.submit(partial_function1)
            future2 = executor.submit(partial_function2)
            #     # 等待操作1和操作2执行完成
            future1.result()
            future2.result()
        # B给A转
        # 算账
        user_a_balances = HttpResponse.get_balance_unit(user_addr=user_addr_a)
        user_b_balances = HttpResponse.get_balance_unit(user_addr=user_addr_b)
        logger.info(f"user_1_balances ={user_a_balances}")
        logger.info(f"user_2_balances ={user_b_balances}")
        assert user_a_balances == balances - Compute.to_u(1) + Compute.to_u(2) - 100
        assert user_b_balances == balances - Compute.to_u(2) + Compute.to_u(1) - 200
        pass

    @pytest.mark.test_0829
    def test_send_sequence(self, creat_two_nokyc):
        """
        一个用户在一个块内向一个用户发起两笔不同的转账，指定sequence
        """
        # 创建两个用户，
        user_addr_a, user_addr_b, balances = creat_two_nokyc
        # user_addr_a = "me1yvrw8l724k4wdd50wzw6vyxnf0mx245kf8ruar"
        # user_addr_b = "me10esf6004mf8tcv4hk8wuegtunwx3fcllgqdmfd"
        # 拿到这个用户的number和sequence
        number = (HttpResponse.q.Account.aunt_account_addr(addr=user_addr_a))['account_number']
        sequence = int((HttpResponse.q.Account.aunt_account_addr(addr=user_addr_a))['sequence'])
        logger.info(f"number={number},sequence={sequence},type={type(sequence)}")
        send_data_1 = dict(from_addr=user_addr_a,
                           to_addr=user_addr_b, amount=1, fees=100, node_ip="localhost:26657",
                           sequence=f"-s={sequence} -a={number}  --offline")
        send_data_2 = dict(from_addr=user_addr_a,
                           to_addr=user_addr_b, amount=2, fees=100, node_ip="localhost:26657",
                           sequence=f"-s={sequence + 1} -a={number}  --offline")
        self.test_bank.test_send(**send_data_1)
        self.test_bank.test_send(**send_data_2)
        time.sleep(5)

        # partial_function1 = partial(self.test_bank.test_send, **send_data_1)
        # partial_function2 = partial(self.test_bank.test_send, **send_data_2)
        # with ThreadPoolExecutor(max_workers=2) as executor:
        #     # 提交操作1和操作2到进程池中并发执行
        #     future1 = executor.submit(partial_function1)
        #     future2 = executor.submit(partial_function2)
        #     #     # 等待操作1和操作2执行完成
        #     future1.result()
        #     future2.result()
        # 查看余额有没有到账
        user_a_balances = HttpResponse.get_balance_unit(user_addr=user_addr_a)
        user_b_balances = HttpResponse.get_balance_unit(user_addr=user_addr_b)
        assert user_a_balances == balances - Compute.to_u(1 + 2) - 200
        assert user_b_balances == balances + Compute.to_u(1 + 2)
        assert 1 == 1
        pass

    @pytest.mark.test_0829
    def test_send_sequence_more(self, creat_one_kyc, creat_two_nokyc, creat_two_kyc):
        """
        一个用户，向多个不同的用户发起转账，指定sequence
        @Desc:
            - user1: 转账，同时向4位不同用户转账
            - user2、user3：非kyc用户
            - user4、user5：kyc用户
        """
        user_addr_1, user1_start = creat_one_kyc
        user_addr_2, user_addr_3, user23_start = creat_two_nokyc
        user_addr_4, user_addr_5, user45_start = creat_two_kyc

        number = (HttpResponse.q.Account.aunt_account_addr(addr=user_addr_1))['account_number']
        sequence = int((HttpResponse.q.Account.aunt_account_addr(addr=user_addr_1))['sequence'])
        logger.info(f"sequence={sequence}")
        send_data_1 = dict(from_addr=user_addr_1, to_addr=user_addr_2, amount=1, fees=100,
                           sequence=f"-s={sequence} -a={number}  --offline")
        send_data_2 = dict(from_addr=user_addr_1, to_addr=user_addr_3, amount=2, fees=100,
                           sequence=f"-s={sequence + 1} -a={number}  --offline")
        send_data_3 = dict(from_addr=user_addr_1, to_addr=user_addr_4, amount=3, fees=100,
                           sequence=f"-s={sequence + 2} -a={number}  --offline")
        send_data_4 = dict(from_addr=user_addr_1, to_addr=user_addr_5, amount=4, fees=100,
                           sequence=f"-s={sequence + 3} -a={number}  --offline")

        result1 = self.test_bank.tx.Bank.send_tx(**send_data_1)
        logger.info(f"result1={result1['txhash']}")
        result2 = self.test_bank.tx.Bank.send_tx(**send_data_2)
        logger.info(f"result2={result2}")

        result3 = self.test_bank.tx.Bank.send_tx(**send_data_3)
        logger.info(f"result3={result3}")

        result4 = self.test_bank.tx.Bank.send_tx(**send_data_4)
        logger.info(f"result4={result4}")
        time.sleep(5)

        user1_balances = HttpResponse.get_balance_unit(user_addr=user_addr_1)
        user2_balances = HttpResponse.get_balance_unit(user_addr=user_addr_2)
        user3_balances = HttpResponse.get_balance_unit(user_addr=user_addr_3)
        user4_balances = HttpResponse.get_balance_unit(user_addr=user_addr_4)
        user5_balances = HttpResponse.get_balance_unit(user_addr=user_addr_5)

        assert user1_balances == user1_start - Compute.to_u(1 + 2 + 3 + 4) - 400
        assert user2_balances == user23_start + Compute.to_u(1)
        assert user3_balances == user23_start + Compute.to_u(2)
        assert user4_balances == user45_start + Compute.to_u(3)
        assert user5_balances == user45_start + Compute.to_u(4)
        assert 1 == 1

        pass
