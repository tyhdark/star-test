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

from tools.handle_query import HandleQuery
from x.query import Query


def to_usrc(number, reverse: bool = True):
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
    用于计算各金额相加  numbers中参数单位为src
    :return: usrc
    """
    return sum([to_usrc(i) for i in numbers])


def period_wait_block():
    for_year = HandleQuery.get_test_blocks_per_year()

    period_block = {
        1: for_year / 12,
        3: for_year / 12 * 3,
        6: for_year / 12 * 6,
        12: for_year,
        24: for_year * 2,
        48: for_year * 4,
    }
    return period_block


def wait_block_for_height(height):
    """等待块高"""
    current = HandleQuery.get_block()
    if int(height) < current:
        return "wait_block_for_height < current_block"
    while True:
        _current = HandleQuery.get_block()
        logger.info(f"waitBlock:{_current}  ---->  {height}")
        if _current > int(height):
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

    a = decimal.Decimal(10) / decimal.Decimal(400) / decimal.Decimal(100000)
    a_str = '{:.20f}'.format(a)
    print(a_str)
