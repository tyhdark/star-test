# -*- coding: utf-8 -*-

import multiprocessing
import os

from cases import unitcases

test_kyc = unitcases.Kyc()


def work(count):
    return f'当前进程是:{count},进程ID:{os.getpid()}, user_info: {test_kyc.test_add()}'


def main():
    pool = multiprocessing.Pool(5)
    result_list = []
    for i in range(5):
        result = pool.apply_async(func=work, args=(i,))  # 异步添加任务
        result_list.append(result)
    for res in result_list:
        print(res.get())


if __name__ == '__main__':
    main()
