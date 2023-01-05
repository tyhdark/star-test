"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 18:34
@Version :  V1.0
@Desc    :  None
"""
import decimal
import time

from loguru import logger

from block.block import Block


def calculate_src(number: int, reverse: bool = False):
    """
    计算代币SRC 《==》 USRC , (number * 10 ** 8)
    :param number:
    :param reverse:
        - False -> 缩小 usrc转src
        - True  -> 放大 src转usrc
    :return:
    """
    if reverse:
        return number * (10 ** 8)
    return decimal.Decimal(number) / decimal.Decimal(10 ** 8)


def wait_block_height():
    """
    等待一个结算周期
    """
    block = Block()
    current = int(block.query_block())

    num = 101 - (current % 100)

    wait_for_block = current + num
    while True:
        _block_height = int(block.query_block())
        logger.info(f"waitBlock:{_block_height}  ---->  {wait_for_block}")
        if _block_height > wait_for_block:
            break
        else:
            time.sleep(10)
            continue


def calculate_srg_to_src(number: int):
    """转换ag to ac"""
    return decimal.Decimal(number) / decimal.Decimal(400)
    pass


if __name__ == '__main__':
    a = calculate_srg_to_src(10000000200000068000)
    b = calculate_src(int(a))
    print(a)
    print(b)
