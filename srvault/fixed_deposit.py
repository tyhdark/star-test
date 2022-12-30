"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 16:39
@Version :  V1.0
@Desc    :  None
"""
import inspect

from loguru import logger

from base.base import BaseClass
from tools import handle_data, handle_input, calculate


class Deposit(BaseClass):

    def list_fixed_deposit(self):
        cmd = self.ssh_home + f"./srs-poad query srvault list-fixed-deposit --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        return handle_data.handle_yaml_to_dict(self.ssh_client.ssh(cmd))

    def show_fixed_deposit_by_id(self, deposit_id):
        cmd = self.ssh_home + f"./srs-poad query srvault show-fixed-deposit {deposit_id} --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        return handle_data.handle_yaml_to_dict(self.ssh_client.ssh(cmd))

    def show_fixed_deposit_by_addr(self, addr):
        cmd = self.ssh_home + f"./srs-poad query srvault show-fixed-deposit-by-acct {addr} --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        return handle_data.handle_yaml_to_dict(self.ssh_client.ssh(cmd))

    def do_fixed_deposit(self, amount, period, from_addr, fees):
        amount = calculate.calculate_src(amount, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srvault do-fixed-deposit src {amount} {period} --from {from_addr} --fees={fees}src --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")

        self.channel.send(cmd + "\n")

        handle_input.input_password(self.channel)
        resp_info = handle_input.ready_info(self.channel)

        if "confirm" in resp_info:
            resp_info = handle_input.yes_or_no(self.channel)

        return handle_data.handle_split_esc(resp_info)
