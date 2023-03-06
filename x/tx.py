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
from tools import handle_resp_data, calculate, handle_console_input


class Tx(BaseClass):

    def __init__(self):
        self.bank = self.Bank()
        self.staking = self.Staking()
        self.keys = self.Keys()

    class Bank(object):

        @staticmethod
        def send_tx(from_addr, to_addr, amount, fees, from_super=False):
            """发送转账交易"""
            cmd = Tx.ssh_home + f"./srs-poad tx bank send {from_addr} {to_addr} {amount}src --fees={fees}src {Tx.chain_id}"
            if from_super:
                cmd += " --home node1"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(2)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

    class Staking(object):

        @staticmethod
        def create_region(region_name, region_id, region_total_as, region_delegators_limit, region_income_rate,
                          from_addr, region_totalStakeAllow, region_userMaxDelegateAC, region_userMinDelegateAC, fees):
            """
            创建区
            :param region_name: 区名称
            :param region_id: 区ID
            :param region_total_as: 区所占AS权重
            :param region_delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
            :param region_income_rate: 区内KYC用户手续费比例
            :param from_addr: 发起方地址
            :param region_totalStakeAllow: 质押水位上限
            :param region_userMaxDelegateAC: 区内用户最大质押额
            :param region_userMinDelegateAC: 区内用户最小质押额
            :param fees: Gas费用
            :return:
            """

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking create-region --region-name={region_name} " \
                                f"--region-id={region_id} --region-total-as={region_total_as} " \
                                f"--region-delegators-limit={region_delegators_limit} " \
                                f"--region-totalStakeAllow={region_totalStakeAllow} " \
                                f"--region-income-rate={region_income_rate} " \
                                f"--region-userMaxDelegateAC={region_userMaxDelegateAC} " \
                                f"--region-userMinDelegateAC={region_userMinDelegateAC} " \
                                f"--from={from_addr} --fees={fees}src {Tx.chain_id} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            try:
                return handle_resp_data.handle_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def new_kyc(addr, region_id, role, from_addr, fees, from_super=True):
            """
            创建区管理员 和 创建区内KYC用户
            :param addr: kyc address
            :param region_id: 所绑定区域ID
            :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
            :param from_addr: 发起地址 区管理员 or 全局管理员
            :param from_super: 发起地址 是超级管理员 需要找到其超管私钥目录
            :param fees: Gas费用 单位src
            :return: tx Hash
            """
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking new-kyc {addr} {region_id} {role}  " \
                                f"--from {from_addr} -y --fees={fees}src {Tx.chain_id}"

            if from_super:
                cmd += " --home node1"
            else:
                # 区管理员 不能创建 KYC_ROlE_ADMIN
                assert "KYC_ROLE_USER" == role

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            resp_info = handle_console_input.ready_info(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def kyc_withdraw_bonus(addr, fees):
            """KYC用户提取注册所赠1src收益"""
            fees = calculate.calculate_src(fees, reverse=True)

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking withdraw --from {addr} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def ag_exchange_ac(ag_amount, fees, from_addr):
            ag_amount = calculate.calculate_src(ag_amount, reverse=True)
            fees = calculate.calculate_src(fees, reverse=True)

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking ag-to-ac {ag_amount} --from={from_addr} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def do_fixed_deposit(amount, period, from_addr, fees):
            amount = calculate.calculate_src(amount, reverse=True)
            fees = calculate.calculate_src(fees, reverse=True)

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking do-fixed-deposit src {amount} {period} --from {from_addr} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")

            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def create_delegate(from_addr, amount, region_id, fees):
            """创建活期质押"""
            amount = calculate.calculate_src(amount, reverse=True)
            fees = calculate.calculate_src(fees, reverse=True)

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking create-delegate --from={from_addr} --amount={amount} " \
                                f"--region-id={region_id} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def add_delegate(from_addr, amount, fees):
            """追加活期质押"""
            amount = calculate.calculate_src(amount, reverse=True)
            fees = calculate.calculate_src(fees, reverse=True)

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking add-delegate --from={from_addr} --amount={amount} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

    class Keys(object):

        @staticmethod
        def add(username):
            """
            添加用户 重名也会新增,地址不一样
            :param username:
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad keys add {username}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "existing" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            if "**Important**" in resp_info:
                return handle_resp_data.handle_add_user(resp_info)

        @staticmethod
        def list():
            """查询用户列表 需要密码"""
            cmd = Tx.ssh_home + "./srs-poad keys list"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)

            resp_info = handle_console_input.ready_info(Tx.channel)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def show(username):
            """
            查询用户信息
            :param username:
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad keys show {username}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            resp_info = handle_console_input.ready_info(Tx.channel)
            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def private_export(username):
            """
            导出私钥
            :param username:
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad keys export {username} --unsafe --unarmored-hex"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)
            if "private key will be exported" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            if "Enter keyring passphrase:" in resp_info:
                Tx.channel.send("12345678" + "\n")
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)
            return handle_resp_data.handle_split_esc(resp_info)


if __name__ == '__main__':
    py_01 = Tx().keys.add("py-01")
    print(py_01)
