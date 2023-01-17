"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/1/3 15:05
@Version :  V1.0
@Desc    :  None
"""
import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_resp_data, calculate, handle_console_input


class Delegate(BaseClass):

    def create_delegate(self, from_addr, amount, region_id, fees):
        """创建活期质押"""
        amount = calculate.calculate_src(amount, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srstaking create-delegate --from={from_addr} --amount={amount} " \
                              f"--region-id={region_id} --fees={fees}src --chain-id=srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_console_input.input_password(self.channel)
        time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        resp_info = handle_console_input.ready_info(self.channel)

        if "confirm" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        return handle_resp_data.handle_split_esc(resp_info)

    def add_delegate(self, from_addr, amount, fees):
        """追加活期质押"""
        amount = calculate.calculate_src(amount, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srstaking add-delegate --from={from_addr} --amount={amount} --fees={fees}src --chain-id=srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_console_input.input_password(self.channel)
        time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        resp_info = handle_console_input.ready_info(self.channel)

        if "confirm" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        return handle_resp_data.handle_split_esc(resp_info)

        pass
