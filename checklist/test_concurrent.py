# -*- coding: utf-8 -*-
import multiprocessing
import os
import time
from multiprocessing import Process

from cases import unitcases

test_kyc = unitcases.Kyc()


def work(count):
    print( f'{count}, user_info: {1}')


# def main():
#     pool = multiprocessing.Pool(5)
#     result_list = []
#     for i in range(5):
#         result = pool.apply_async(func=work, args=(i,))  # 异步添加任务
#         result_list.append(result)
#     for res in result_list:
#         print(res.get())



def work_01(user):
    for i in range(5):
        time.sleep(1)
        print(f" 我是:{user} 在听音乐,我的进程pid是{os.getpid()},我的父级pid是：{os.getppid()}")


def work_02(user):
    for j in range(8):
        time.sleep(1)
        print(f" 我是:{user} 在工作,我的进程pid是{os.getpid()},我的父级pid是：{os.getppid()}")


def main():
    p1 = Process(target=work, args=("1",), name="听歌进程")
    p2 = Process(target=work, args=("2",), name="工作进程")
    p2.daemon = True
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    time.sleep(5)
    print(f"hi... 我是主进程，我的主进程PID是:{os.getpid()}")

if __name__ == '__main__':
    # work(1)
    main()
