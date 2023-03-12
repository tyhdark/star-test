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

from config import chain
from tools import handle_resp_data, handle_console_input
from x.base import BaseClass


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
                cmd += chain.super_addr_home
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
        def ag_to_ac(ag_amount, from_addr, fees):
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking ag-to-ac {ag_amount}srg --from={from_addr} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def create_region(region_name, region_id, total_as, delegators_limit, fee_rate,
                          from_addr, totalStakeAllow, userMaxDelegateAC, userMinDelegateAC, fees):
            """
            创建区
            :param region_name: 区名称
            :param region_id: 区ID
            :param total_as: 区所占AS权重
            :param delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
            :param fee_rate: 区内KYC用户手续费比例
            :param from_addr: 发起方地址
            :param totalStakeAllow: 质押水位上限
            :param userMaxDelegateAC: 区内用户最大质押额
            :param userMinDelegateAC: 区内用户最小质押额
            :param fees: Gas费用
            :return:
            """

            cmd = Tx.ssh_home + f"./srs-poad tx srstaking create-region --region-name={region_name} " \
                                f"--region-id={region_id} --total-as={total_as} " \
                                f"--delegators-limit={delegators_limit} " \
                                f"--totalStakeAllow={totalStakeAllow} " \
                                f"--fee-rate={fee_rate} " \
                                f"--userMaxDelegateAC={userMaxDelegateAC} " \
                                f"--userMinDelegateAC={userMinDelegateAC} " \
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
        def update_region(region_id, from_addr, fees, region_name=None, region_delegators_limit=None,
                          region_income_rate=None, region_totalStakeAllow=None, region_userMaxDelegateAC=None,
                          region_userMinDelegateAC=None):
            """
            修改区信息
            :param region_name: 区名称
            :param region_id: 区ID
            :param region_delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
            :param region_income_rate: 区内KYC用户手续费比例
            :param from_addr: 发起方地址
            :param region_totalStakeAllow: 质押水位上限
            :param region_userMaxDelegateAC: 区内用户最大质押额
            :param region_userMinDelegateAC: 区内用户最小质押额
            :param fees: Gas费用
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking update-region --from={from_addr} --region-id={region_id} " \
                                f"--fees={fees}src {Tx.chain_id} "
            if region_name:
                region_name = f"--region-name={region_name} "
                cmd += f"{region_name}"
            if region_delegators_limit:
                cmd += f"--region-delegators-limit={region_delegators_limit} "
            if region_income_rate:
                cmd += f"--region-income-rate={region_income_rate} "
            if region_totalStakeAllow:
                cmd += f"--region-totalStakeAllow={region_totalStakeAllow} "
            if region_userMaxDelegateAC:
                cmd += f"--region-userMaxDelegateAC={region_userMaxDelegateAC} "
            if region_userMinDelegateAC:
                cmd += f"--region-userMinDelegateAC={region_userMinDelegateAC} "

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            try:
                return handle_resp_data.handle_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def create_validator(pubkey, moniker, from_addr, fees, from_super=True):
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking create-validator --pubkey={pubkey} --moniker={moniker} " \
                                f"--from={from_addr} --fees={fees}src {Tx.chain_id}"
            if from_super:
                cmd += chain.super_addr_home

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            try:
                return handle_resp_data.handle_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def update_validator(operator_address, region_name, from_addr, fees, from_super=True):
            """Only used to modify the Region ID of the verifier"""
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking update-validator --validator-address={operator_address} " \
                                f"--region-name={region_name} --from={from_addr} --fees={fees}src {Tx.chain_id}"
            if from_super:
                cmd += chain.super_addr_home
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            try:
                return handle_resp_data.handle_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def delegate(from_addr, amount, fees):
            """创建/追加 活期质押"""
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking delegate --from={from_addr} --amount={amount}src " \
                                f"--fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def undelegate(from_addr, amount, fees):
            """减少活期质押: 减少质押金额 >= 实际质押额 则按实际质押额兑付"""
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking undelegate --from={from_addr} --amount={amount}src --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def exit_delegate(from_addr, delegator_address, fees, from_super=False):
            """
            退出活期质押
            :param from_addr: 发起方地址  【超管、区管理员、用户自己】
            :param delegator_address: 被清退质押者地址
            :param from_super: True from_addr是超管需要添加私钥目录地址
            :param fees:
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking exit-delegate --from={from_addr} " \
                                f"--delegator-address={delegator_address} --fees={fees}src {Tx.chain_id}"
            if from_super:
                cmd += chain.super_addr_home
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def withdraw(addr, fees):
            """KYC用户提取活期收益"""
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking withdraw --from={addr} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def do_fixed_deposit(amount, period, from_addr, fees=1, gas=200000):
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking do-fixed-deposit {amount}src {period} --from={from_addr} --fees={fees}src --gas={gas} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def do_fixed_withdraw(deposit_id, from_addr, fees=1, gas=200000):
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking do-fixed-withdraw {deposit_id} --from={from_addr} --fees={fees}src {gas} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def set_fixed_deposit_interest_rate(region_id, rate, period, from_addr, fees):
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking set-fixed-deposit-interest-rate {region_id} {rate} {period} " \
                                f"--from={from_addr} --fees={fees}src {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def new_kyc(addr, region_id, role, from_addr, fees=1, gas=200000, from_super=False):
            """
            创建KYC用户
            :param gas: gas限制 默认200000
            :param addr: kyc address
            :param region_id: 所绑定区域ID
            :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
            :param from_addr: 发起地址 区管理员 or 全局管理员
            :param from_super: 发起地址 是超级管理员 需要找到其超管私钥目录
            :param fees: Gas费用 单位src
            :return: tx Hash
            """
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking new-kyc {addr} {region_id} {role}  " \
                                f"--from {from_addr} -y --fees={fees}src --gas={gas} {Tx.chain_id}"

            if from_super:
                cmd += chain.super_addr_home
            else:
                # 区管理员 不能创建 KYC_ROlE_ADMIN
                assert "KYC_ROLE_USER" == role

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            resp_info = handle_console_input.ready_info(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def remove_kyc(addr, from_addr, fees, from_super=False):
            cmd = Tx.ssh_home + f"./srs-poad tx srstaking remove-kyc {addr} --from={from_addr} -y --fees={fees}src {Tx.chain_id}"
            if from_super:
                cmd += chain.super_addr_home

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            handle_console_input.input_password(Tx.channel)
            resp_info = handle_console_input.ready_info(Tx.channel)

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

            time.sleep(4)
            resp_info = handle_console_input.ready_info(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def show(username, from_super=False):
            """
            查询用户信息
            :param username:
            :param from_super: 默认不是超管
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad keys show {username}"
            if from_super:
                cmd += chain.super_addr_home
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            resp_info = handle_console_input.ready_info(Tx.channel)
            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def private_export(username, from_super=False):
            """
            导出私钥
            :param username:
            :param from_super: 默认不是超管
            :return:
            """
            cmd = Tx.ssh_home + f"./srs-poad keys export {username} --unsafe --unarmored-hex"
            if from_super:
                cmd += chain.super_addr_home

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
    # py_01 = Tx().staking.remove_kyc("sil1jqjtm7dge0ja64spr3wfgs8f6rnfg9ayj0lu6x",
    #                                 "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh", 1, True)
    # print(py_01)
    pub = '\'{"type": "tendermint/PubKeyEd25519","value": "a9UxLb0DuMJ0Y584VjSe+FWvJiglV4STErFSfT0Cd0Q="}\''

    # res = Tx().staking.create_validator(pub, "node2", "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh", 1)
    # res = Tx().staking.update_validator("silvaloper1jxrauca2fdrwyvtzmelv5td84wpjqd9f6rks4c", "CZE",
    #                                     "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh", 1)
    # res = Tx().staking.do_fixed_deposit(10, "PERIOD_3_MONTHS", "sil155mv39aqtl234twde44wrjdd5phxx28mg46u3p", 1)
    # print(res)
    res = Tx().keys.private_export("user-ElznPKTwH9Aj")
    print(res)
