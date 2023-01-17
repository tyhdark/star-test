"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/1/5 11:29
@Version :  V1.0
@Desc    :  None
"""

import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_resp_data, calculate, handle_console_input


class AgToAc(BaseClass):

    def ag_exchange_ac(self, ag_amount, fees, from_addr):
        ag_amount = calculate.calculate_src(ag_amount, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srvault ag-to-ac {ag_amount} --from={from_addr} --fees={fees}src --chain-id=srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")

        handle_console_input.input_password(self.channel)
        time.sleep(3)
        resp_info = handle_console_input.ready_info(self.channel)

        if "confirm" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        return handle_resp_data.handle_split_esc(resp_info)


if __name__ == '__main__':
    a = AgToAc()
    res = a.ag_exchange_ac(400, 1, "sil18vj3druvnwfmy03mxk0l7s9cuk0shscsx7qyaa")
    print(res)
