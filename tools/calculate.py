"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 18:34
@Version :  V1.0
@Desc    :  None
"""
import decimal


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
