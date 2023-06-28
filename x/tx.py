# -*- coding: utf-8 -*-
import inspect
import time

from loguru import logger

from config.chain import config, GasLimit, Fees
from tools.console import Interaction, Result
from x.base import BaseClass


class Tx(BaseClass):

    def __init__(self):
        self.bank = self.Bank()
        self.staking = self.Staking()
        self.keys = self.Keys()

    @staticmethod
    def _executor(cmd):
        resp_info = Tx.ssh_client.ssh(cmd, strip=False)
        if resp_info.failed:
            logger.info(f"{inspect.stack()[0][3]} resp_info.stderr: {resp_info.stderr}")
            return resp_info.stderr
        return Result.yaml_to_dict(resp_info.stdout)

    class Bank(object):

        @staticmethod
        def send_tx(from_addr, to_addr, amount, fees=Fees, gas=GasLimit):
            """发送转账交易"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx bank send {from_addr} {to_addr} {amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

    class Staking(object):

        @staticmethod
        def ag_to_ac(ag_amount, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking ag-to-ac {ag_amount}{Tx.coin['g']} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def create_region(from_addr, region_name, region_id, total_as, fee_rate, totalStakeAllow, userMaxDelegateAC,
                          userMinDelegateAC, delegators_limit=-1, fees=Fees, gas=GasLimit):
            """
            创建区
            :param from_addr: 发起方地址 需要区域管理员
            :param region_name: 区名称
            :param region_id: 区ID
            :param total_as: 区所占AS权重
            :param fee_rate: 区内KYC用户手续费比例
            :param totalStakeAllow: 质押水位上限
            :param userMaxDelegateAC: 区内用户最大质押额
            :param userMinDelegateAC: 区内用户最小质押额
            :param delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
            :param fees: Gas费用
            :param gas: 默认为 200000
            :return:
            """

            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking create-region --region-name={region_name} " \
                                 f"--region-id={region_id} --total-as={total_as} " \
                                 f"--delegators-limit={delegators_limit} " \
                                 f"--totalStakeAllow={totalStakeAllow} " \
                                 f"--fee-rate={fee_rate} " \
                                 f"--userMaxDelegateAC={userMaxDelegateAC} " \
                                 f"--userMinDelegateAC={userMinDelegateAC} " \
                                 f"--from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def update_region(region_id, from_addr, region_name=None, delegators_limit=None, fee_rate=None,
                          totalStakeAllow=None, userMaxDelegateAC=None, userMinDelegateAC=None, isUndelegate=None,
                          fees=Fees, gas=GasLimit):
            """
            修改区信息
            :param region_id: 区ID
            :param from_addr: 发起方地址
            :param region_name: 区名称
            :param delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
            :param fee_rate: 区内KYC用户手续费比例
            :param totalStakeAllow: 质押水位上限
            :param userMaxDelegateAC: 区内用户最大质押额
            :param userMinDelegateAC: 区内用户最小质押额
            :param isUndelegate: 控制区内永久质押开关,默认 false 不可提取
            :param fees: 费用
            :param gas: GasLimit
            :return:
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking update-region --from={from_addr} --region-id={region_id} " \
                                 f"--fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y "
            if region_name:
                cmd += f"--region-name={region_name} "
            if delegators_limit:
                cmd += f"--delegators-limit={delegators_limit} "
            if fee_rate:
                cmd += f"--fee-rate={fee_rate} "
            if totalStakeAllow:
                cmd += f"--totalStakeAllow={totalStakeAllow} "
            if userMaxDelegateAC:
                cmd += f"--userMaxDelegateAC={userMaxDelegateAC} "
            if userMinDelegateAC:
                cmd += f"--userMinDelegateAC={userMinDelegateAC} "
            if isUndelegate:
                cmd += f"--isUndelegate={isUndelegate} "

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def create_validator(pubkey, moniker, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking create-validator --pubkey={pubkey} --moniker={moniker} " \
                                 f"--from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def update_validator(operator_address, region_name, from_addr, fees=Fees, gas=GasLimit):
            """
            Only used to modify the Region ID of the verifier
            :param operator_address: Validator address
            :param region_name: region name
            :param from_addr: must owner address is admin
            :param gas: gas limit
            :param fees: fees
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking update-validator --validator-address={operator_address} " \
                                 f"--region-name={region_name} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def delegate(from_addr, amount, fees=Fees, gas=GasLimit):
            """创建/追加 活期质押"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking delegate --from={from_addr} --amount={amount}{Tx.coin['c']} " \
                                 f"--fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def undelegate(from_addr, amount, fees=Fees, gas=GasLimit):
            """
            减少活期质押:
            1.减少质押金额 >= 实际质押额 则按实际质押额兑付 并主动发放收益
            2.减少质押金额 < 实际质押额 则按传入金额兑付, 收益重新计算但不主动发放
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking undelegate --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def exit_delegate(from_addr, delegator_address, fees=Fees, gas=GasLimit):
            """
            退出活期质押
            :param from_addr: 发起方地址  【超管、区管理员、用户自己】
            :param delegator_address: 被清退质押者地址
            :param fees:
            :return:
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking exit-delegate --from={from_addr} " \
                                 f"--delegator-address={delegator_address} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def delegate_fixed(from_addr, amount, term, fees=Fees, gas=GasLimit):
            """创建活期周期质押"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking delegate-fixed --from={from_addr} --amount={amount}{Tx.coin['c']} --fixed_delegation_term={term} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def delegate_infinite(from_addr, amount, fees=Fees, gas=GasLimit):
            """创建活期永久质押"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking delegate-infinite --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def undelegate_fixed(from_addr, fixed_delegation_id, fees=Fees, gas=GasLimit):
            """减少活期周期质押"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking undelegate-fixed --from={from_addr} --fixed_delegation_id={fixed_delegation_id} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def undelegate_infinite(from_addr, amount, fees=Fees, gas=GasLimit):
            """减少活期永久质押"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking undelegate-infinite --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def withdraw(addr, fees=Fees, gas=GasLimit):
            """KYC用户提取活期收益"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking withdraw --from={addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def create_fixed_deposit(amount, period, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking deposit-fixed {amount}{Tx.coin['c']} {period} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def withdraw_fixed_deposit(deposit_id, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking withdraw-fixed {deposit_id} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def set_fixed_delegation_interest_rate(region_id, rate, term, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking set-fixed-deposit-interest-rate {region_id} {rate} {term} " \
                                 f"--from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def set_fixed_deposit_interest_rate(region_id, rate, period, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking set-fixed-deposit-interest-rate {region_id} {rate} {period} " \
                                 f"--from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def new_kyc(addr, region_id, role, from_addr, fees=Fees, gas=GasLimit):
            """
            创建KYC用户
            :param addr: kyc address
            :param region_id: 所绑定区域ID
            :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
            :param from_addr: 发起地址 区管理员 or 全局管理员
            :param fees: Gas费用 {Tx.coin['c']}
            :param gas: 默认200000
            :return: tx Hash
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking new-kyc {addr} {region_id} {role} --from {from_addr} " \
                                 f"--fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"

            if from_addr != Tx.super_addr:  # 区管理员 不能创建 KYC_ROlE_ADMIN
                assert role == config["chain"]["role"]["user"]
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def remove_kyc(addr, from_addr, fees=Fees, gas=GasLimit):
            cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking remove-kyc {addr} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

    class Keys(object):

        @staticmethod
        def add(username):
            """添加用户 重名也会新增,地址不一样"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys add {username} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(1)
            resp_info = Interaction.ready(Tx.channel)

            if "existing" in resp_info:
                resp_info = Interaction.yes_or_no(Tx.channel)

            assert "**Important**" in resp_info

        @staticmethod
        def list():
            """查询本地用户列表"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys list {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def show(username):
            """查询本地用户信息"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys show {username} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Result.yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def private_export(username):
            """导出私钥"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys export {username} --unsafe --unarmored-hex {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(1)
            resp_info = Interaction.ready(Tx.channel)
            if "private key will be exported" in resp_info:
                resp_info = Interaction.yes_or_no(Tx.channel)

            return Result.split_esc(resp_info)


if __name__ == '__main__':
    # py_01 = Tx().bank.send_tx("gea12g50h9fa7jp4tu47f4mn906s3274urjamcvyrd",
    #                           "gea1pv54mu2fa72vhz9wkx3dmw94f8nf6ncppae9pk", 1000, 1)
    # print(py_01)
    pass
