# -*- coding: utf-8 -*-
import decimal
import time

from loguru import logger
from swagger_client.rest import ApiException

from x.api import api_instance


class Compute:

    @staticmethod
    def to_uc(number, reverse: bool = False):
        """
        计算代币AC 《==》 UAC , (number * 10 ** 6)
        :param number:
        :param reverse:
            - False  ->  ac转uac
            - True   ->  uac转ac
        """

        return number * (10 ** 6) if not reverse else decimal.Decimal(number) / decimal.Decimal(10 ** 6)

    @staticmethod
    def interest(amount: int, period: int, rate: float):
        """计算利息"""
        return rate * period / 12 * amount

    @property
    def get_blocks_per_year(self) -> int:
        try:
            mint_params = api_instance.query.cosmos_mint_v1_beta1_params()
            blocks_per_year = int(mint_params.params.blocks_per_year)
        except ApiException as e:
            raise ("Exception when calling QueryApi->cosmos_mint_v1_beta1_params: %s\n" % e)
        return blocks_per_year

    @property
    def get_current_block(self) -> int:
        try:
            base_block = api_instance.service.cosmos_base_tendermint_v1_beta1_get_latest_block()
            current_height = base_block.block.header.height
        except ApiException as e:
            raise ("Exception when calling QueryApi->cosmos_base_tendermint_v1_beta1_get_latest_block: %s\n" % e)
        return current_height

    def period_block(self):
        blocks_per_year = self.get_blocks_per_year
        period_block = {
            1: blocks_per_year // 12,
            3: blocks_per_year // 12 * 3,
            6: blocks_per_year // 2,
            12: blocks_per_year,
            24: blocks_per_year * 2,
            48: blocks_per_year * 4,
        }
        return period_block

    def wait_block_for_height(self, height: int):
        current_height = self.get_current_block
        if height < current_height:
            return f"wait_block_for_height:{height} < current_height:{current_height}"
        while True:
            _current = self.get_current_block
            logger.info(f"waitBlock:{_current}  ---->  {height}")
            if _current > int(height):
                break
            else:
                time.sleep(10)
                continue


if __name__ == '__main__':
    print(Compute().to_uc(200))
    pass
