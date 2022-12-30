"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 09:16
@Version :  V1.0
@Desc    :  None
"""
from base.base import BaseClass
from tools import handle_data, calculate, handle_input
from tools.handle_data import HandleRespErrorInfo


class Region(BaseClass):

    def create_region(self, region_name, region_id, power_limit, delegators_limit, fee_rate, from_addr, stake_up, fees):
        power_limit = calculate.calculate_src(power_limit, reverse=True)
        stake_up = calculate.calculate_src(stake_up, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srstaking create-region --region-name={region_name} " \
                              f"--region-id={region_id} --commission-power-limit={power_limit} " \
                              f"--delegators-limit={delegators_limit} --region-KYCStakeUpQuota={stake_up} " \
                              f"--region-fee-rate={fee_rate} --from={from_addr} --fees={fees}src --chain-id=srspoa -y"
        self.channel.send(cmd + "\n")
        handle_input.input_password(self.channel)
        resp_info = handle_input.ready_info(self.channel)

        try:
            return handle_data.handle_split_esc_re(resp_info)
        except Exception:
            error_info = HandleRespErrorInfo.handle_rpc_error(resp_info)
            return error_info
