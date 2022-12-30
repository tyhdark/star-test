"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 09:16
@Version :  V1.0
@Desc    :  None
"""
import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_data, calculate, handle_input
from tools.handle_data import HandleRespErrorInfo


class Region(BaseClass):

    def create_region(self, region_name, region_id, power_limit, delegators_limit, fee_rate, from_addr, stake_up, fees):
        """
        创建区
        :param region_name: 区名称
        :param region_id: 区ID
        :param power_limit: 区所占AS权重
        :param delegators_limit: 区内委托上限人数
        :param fee_rate: 区内KYC用户手续费比例
        :param from_addr: 发起方地址
        :param stake_up: 质押水位上限
        :param fees: Gas费用
        :return:
        """
        power_limit = calculate.calculate_src(power_limit, reverse=True)
        stake_up = calculate.calculate_src(stake_up, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srstaking create-region --region-name={region_name} " \
                              f"--region-id={region_id} --commission-power-limit={power_limit} " \
                              f"--delegators-limit={delegators_limit} --region-KYCStakeUpQuota={stake_up} " \
                              f"--region-fee-rate={fee_rate} --from={from_addr} --fees={fees}src --chain-id=srspoa -y"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_input.input_password(self.channel)
        time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        resp_info = handle_input.ready_info(self.channel)

        try:
            return handle_data.handle_split_esc_re_code(resp_info)
        except Exception:
            error_info = HandleRespErrorInfo.handle_rpc_error(resp_info)
            return error_info

    def query_list_region(self):
        """查询区域列表"""
        cmd = self.ssh_home + f"./srs-poad query srstaking list-region --chain-id=srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd)
        return handle_data.handle_yaml_to_dict(res)


if __name__ == '__main__':
    a = Region()
    s = a.query_list_region()
    print(s)
