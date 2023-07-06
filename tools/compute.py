# -*- coding: utf-8 -*-
import decimal
import time

from loguru import logger

from config.chain import config
from tools.parse_response import HttpResponse


class Compute:

    @classmethod
    def to_u(cls, number, reverse: bool = False):
        """
        计算代币AC 《==》 UAC , (number * 10 ** 8)
        :param number:
        :param reverse:
            - False  ->  ac转uac
            - True   ->  uac转ac
        """
        if not reverse:
            return number * (10 ** 6)
        return decimal.Decimal(number) / decimal.Decimal(10 ** 6)

    @classmethod
    def ag_to_ac(cls, number: int, reverse: bool = False):
        """转换ag to ac"""
        if not reverse:
            return decimal.Decimal(number) / decimal.Decimal(400)
        return number * 400

    @classmethod
    def as_to_ac(cls, number: int, reverse: bool = False):
        if reverse:
            return decimal.Decimal(number) / decimal.Decimal(400)
        return number * 400

    @classmethod
    def all_to_uc(cls, *args):
        for i in args:
            yield cls.to_u(i)

    @classmethod
    def interest(cls, amount: int, period: int, rate: float):
        """计算利息"""
        return rate * period / 12 * amount


class WaitBlock:

    @staticmethod
    def period_wait_block():
        blocks_per_year = config["compute"]["BlocksPerYear"]
        # test environment
        blocks_per_year /= 43800

        period_block = {
            1: blocks_per_year / 12,
            3: blocks_per_year / 12 * 3,
            6: blocks_per_year / 12 * 6,
            12: blocks_per_year,
            24: blocks_per_year * 2,
            48: blocks_per_year * 4,
        }
        return period_block

    @staticmethod
    def wait_block_for_height(height: int):
        """等待块高"""
        current = HttpResponse.get_current_block()
        if int(height) < current:
            return "wait_block_for_height < current_block"
        while True:
            _current = HttpResponse.get_current_block()
            logger.info(f"waitBlock:{_current}  ---->  {height}")
            if _current > int(height):
                break
            else:
                time.sleep(10)
                continue


if __name__ == '__main__':
    # a = decimal.Decimal(10) / decimal.Decimal(400) / decimal.Decimal(100000)
    # a_str = '{:.20f}'.format(a)
    # print(a_str)
    b = Compute.interest(10, 1, 0.06)
    print(b, type(b))
