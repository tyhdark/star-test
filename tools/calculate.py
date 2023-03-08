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

from x.query import Query


def to_usrc(number: int, reverse: bool = True):
    """
    计算代币SRC 《==》 USRC , (number * 10 ** 8)
    :param number:
    :param reverse:
        - False -> 缩小 usrc转src
        - True  -> 放大 src转usrc
    :return:
    """
    if reverse:
        return number * (10 ** 6)
    return decimal.Decimal(number) / decimal.Decimal(10 ** 6)


def subtraction(total, pay, fees):
    """
    用于计算账户余额 传入src 返回 usrc
    :return usrc
    """
    total = to_usrc(total)
    pay = to_usrc(pay)
    fees = to_usrc(fees)
    return total - pay - fees


def add(numbers: list):
    """
    用于计算各金额相加
    :return:
    """
    return sum([to_usrc(i) for i in numbers])


def wait_block_height():
    """
    等待一个结算周期
    """
    block = Query().block
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


def ag_to_ac(number: int):
    """转换ag to ac"""
    return decimal.Decimal(number) / decimal.Decimal(400)
    pass


def border_value():
    """
    测试示例： 在块高100进行委托，101在次委托
    """
    block = Query().block
    current = int(block.query_block())

    num = 100 - (current % 100)

    wait_for_block = current + num
    while True:
        _block_height = int(block.query_block())
        logger.info(f"waitBlock:{_block_height}  ---->  {wait_for_block}")
        if _block_height >= wait_for_block:
            break
        else:
            time.sleep(0.5)
            continue


def border_value2():
    """
    测试示例： 在块高100进行委托，101在次委托
    """
    block = Query().block
    current = int(block.query_block())

    num = 99 - (current % 100)

    wait_for_block = current + num
    while True:
        _block_height = int(block.query_block())
        logger.info(f"waitBlock:{_block_height}  ---->  {wait_for_block}")
        if _block_height >= wait_for_block:
            break
        else:
            time.sleep(0.5)
            continue


if __name__ == '__main__':
    a = ag_to_ac(10000000200000068000)
    b = to_usrc(int(a), False)
    print(a)
    print(b)
