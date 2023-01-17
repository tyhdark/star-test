"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 10:38
@Version :  V1.0
@Desc    :  None
"""
import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_resp_data, handle_console_input, calculate


class Bank(BaseClass):

    def query_balances(self, addr):
        """查询 addr 余额"""
        cmd = self.ssh_home + f"./srs-poad query bank balances {addr}"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd)
        return handle_resp_data.handle_yaml_to_dict(res)

    def send_tx(self, from_addr, to_addr, amount, fees, from_super=False):
        """发送转账交易"""
        amount = calculate.calculate_src(amount, reverse=True)
        fees = int(calculate.calculate_src(fees, reverse=True))

        cmd = self.ssh_home + f"./srs-poad tx bank send {from_addr} {to_addr} {amount}src --fees={fees}src --chain-id=srspoa"
        if from_super:
            cmd += " --home node1"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_console_input.input_password(self.channel)
        time.sleep(2)
        resp_info = handle_console_input.ready_info(self.channel)

        if "confirm" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        return handle_resp_data.handle_split_esc(resp_info)


if __name__ == '__main__':
    obj = Bank()
    a = obj.query_balances("sil1d9t7h877g5mpzq0azphdfuk3a567qnn2twmep9")
    print(a)
    b = obj.send_tx(from_addr="sil17xneh8t87qy0z0z4kfx3ukjppqrnwpazwg83dc",
                    to_addr="sil1d9t7h877g5mpzq0azphdfuk3a567qnn2twmep9",
                    amount=1000, fees=1.1, from_super=True)
    print(b)
