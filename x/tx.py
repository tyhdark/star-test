# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import inspect
import json
import time

from loguru import logger

from tools import handle_resp_data, handle_console_input
from x.base import BaseClass

"""
Tx交易,(第五)
"""


class Tx(BaseClass):

    def __init__(self):
        self.bank = self.Bank()
        self.staking = self.Staking()
        self.keys = self.Keys()

    class Bank(object):

        @staticmethod
        def send_tx(from_addr, to_addr, amount, fees=0, gas=200000):
            """发送转账交易"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank send {from_addr} {to_addr} {amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(2)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

    class SendToAdmin(object):

        @staticmethod
        def send_to_admin():
            """创世时国库给超管打钱，无手续费，作为初始用"""

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank sendToAdmin 10000mec --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.keyring_backend}  {Tx.chain_id}"

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # 这里是logger插入
            # Tx.channel.sen 是调用了Host类，对服务器进行；连接，且查看响应，send发送cmd命令且\n脱敏
            Tx.channel.send(cmd + "\n")  # 对命令进行\n处理，因为linux不能识别\n
            """Tx.channel是对引用了Host类，当调用时就是自动对服务器进行连接，且查看响应且返回内容，resp_info就是返回结果"""
            """handle_console_input.ready_info是捕获你插入的cmd命令展示出来Logger"""
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:  # 如果你输入cmd后你响应的内容里面有confirm 那就是提示你y/n确认，执行下面这步
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        def send_to_admin_fees(amount: int, fees=100):
            """普通时国库给超管转钱，有手续费，作为一种场景"""

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank sendToAdmin {amount}{Tx.coin.get('c')} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.keyring_backend}  {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')}"

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # 这里是logger插入
            # Tx.channel.sen 是调用了Host类，对服务器进行；连接，且查看响应，send发送cmd命令且\n脱敏
            Tx.channel.send(cmd + "\n")  # 对命令进行\n处理，因为linux不能识别\n
            """Tx.channel是对引用了Host类，当调用时就是自动对服务器进行连接，且查看响应且返回内容，resp_info就是返回结果"""
            """handle_console_input.ready_info是捕获你插入的cmd命令展示出来Logger"""
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:  # 如果你输入cmd后你响应的内容里面有confirm 那就是提示你y/n确认，执行下面这步
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def send_admin_to_user(to_account: str, amounts=100, fees=100):
            """创世后超管往个人打钱，前提是超管有钱！"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank send $({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend}) $({Tx.chain_bin} keys show {to_account} -a {Tx.keyring_backend}) {amounts}mec {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')} "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def tx_bank_send(from_address: str, to_address: str, amounts: int, fees=100):
            """根据用户名，A用户给B用户打钱"""

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank send {Tx.Keys.private_export_meuser(username=from_address)} {Tx.Keys.private_export_meuser(username=to_address)} {amounts}umec {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')} "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            # print(Tx.Query.query_bank_balance_adders(address=to_address))

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def creation_validator_node(node_name: str, amounts=100, fees=100):
            """创世后创建验证者节点  传入node_name将节点升级成验证者"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking create-validator --amount={amounts}{Tx.coin.get('c')} --pubkey=$(./me-chaind tendermint show-validator --home {node_name}) --moniker={node_name} --commission-rate=\"0.10\" --commission-max-rate=\"0.20\" --commission-max-change-rate=\"0.01\" --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend}) {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def creation_region(region_id: int, region_name: str, validator_node_name: str, fees=100):
            """传入区id、区名称、节点名称 来创建区"""
            # node_name = validator_node_name
            validator_address = Tx.Query.query_staking_validator_from_node_name(node_name=validator_node_name)
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking new-region {region_id} {region_name} {validator_address}  --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)
            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def new_kyc_for_username(user_name: str, region_id: int, fees=100):
            """传入用户名称，和区id，进行用户kyc认证"""

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking new-kyc {Tx.Keys.show_address_for_username(username=user_name)}  {region_id} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.keyring_backend}  {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')} "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def count_down_5s():
            for i in range(5, 0, -1):
                print(i)
                time.sleep(1)

            print("next!")

        @staticmethod
        def start_script():
            """创世脚本跑完后，链起来之后的一系列操作"""
            # 国库转钱给超管
            Tx.SendToAdmin.send_to_admin_fees(amout=Tx.amout, fees=0)
            Tx.SendToAdmin.count_down_5s()
            # 查询验证者节点列表
            validator_list_before = Tx.Query.query_staking_validator_list()
            for validators_before in validator_list_before["validators"]:
                print(validators_before)
            # 超管创建节点
            Tx.SendToAdmin.creation_validator_node(node_name=Tx.node_name)
            Tx.SendToAdmin.count_down_5s()
            # 超管给个人打钱
            Tx.SendToAdmin.send_admin_to_user(to_account=Tx.to_account)
            Tx.SendToAdmin.count_down_5s()
            # 查询验证者节点
            validator_list_later = Tx.Query.query_staking_validator_list()
            for validators_later in validator_list_later["validators"]:
                print(validators_later)
            # 查询区列表
            region_list_before = Tx.Query.query_staking_list_region()
            for regions_later_before in region_list_before["region"]:
                print(regions_later_before)
            # 创建区绑定节点
            Tx.SendToAdmin.creation_region(region_id=Tx.region_id, region_name=Tx.region_name,
                                           validator_node_name=Tx.node_name)
            Tx.SendToAdmin.count_down_5s()
            # 查询区列表
            region_list_later = Tx.Query.query_staking_list_region()
            for regions_later in region_list_later["region"]:
                print(regions_later)
            # 将用户认证成KYC
            Tx.SendToAdmin.new_kyc_for_username(user_name=Tx.to_account, region_id=Tx.region_id)
            Tx.SendToAdmin.count_down_5s()
            # 查询KYC列表
            kyc_list = Tx.Query.query_staking_list_kyc()

            for kycs in kyc_list["kyc"]:
                print(kycs)

            print("恭喜，所有的方法都执行成功了，初始化成功，")

    class Staking(object):

        @staticmethod
        def ag_to_ac(ag_amount, from_addr, fees):
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking ag-to-ac {ag_amount}{Tx.coin['g']} --from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def create_region(region_name, region_id, total_as, delegators_limit, fee_rate,
                          from_addr, totalStakeAllow, userMaxDelegateAC, userMinDelegateAC, fees, gas=200000):
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
            :param gas: gas 默认为 200000
            :return:
            """

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking create-region --region-name={region_name} " \
                                f"--region-id={region_id} --total-as={total_as} " \
                                f"--delegators-limit={delegators_limit} " \
                                f"--totalStakeAllow={totalStakeAllow} " \
                                f"--fee-rate={fee_rate} " \
                                f"--userMaxDelegateAC={userMaxDelegateAC} " \
                                f"--userMinDelegateAC={userMinDelegateAC} " \
                                f"--from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            # handle_console_input.input_password(Tx.channel)
            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            try:
                return handle_resp_data.handle_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def update_region(region_id, from_addr, fees, region_name=None, delegators_limit=None,
                          fee_rate=None, totalStakeAllow=None, userMaxDelegateAC=None,
                          userMinDelegateAC=None, isUndelegate=None):
            """
            修改区信息
            :param region_name: 区名称
            :param region_id: 区ID
            :param delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
            :param fee_rate: 区内KYC用户手续费比例
            :param from_addr: 发起方地址
            :param totalStakeAllow: 质押水位上限
            :param userMaxDelegateAC: 区内用户最大质押额
            :param userMinDelegateAC: 区内用户最小质押额
            :param fees: Gas费用
            :return:
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking update-region --from={from_addr} --region-id={region_id} " \
                                f"--fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend} "
            if region_name:
                region_name = f"--region-name={region_name} "
                cmd += f"{region_name}"
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
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)
            try:
                return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def create_validator(pubkey, moniker, from_addr, fees):
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking create-validator --pubkey={pubkey} --moniker={moniker} " \
                                f"--from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend} "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            try:
                return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info

        @staticmethod
        def update_validator(operator_address, region_name, from_addr, fees):
            """Only used to modify the Region ID of the verifier"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking update-validator --validator-address={operator_address} " \
                                f"--region-name={region_name} --from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend} "

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            try:
                return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
            except Exception:
                error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
                return error_info


        @staticmethod
        def delegate(amount: int, username: str, fees=100):
            """创建/追加 活期质押，已修改"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking delegate  {amount}{Tx.coin.get('c')} --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)


        # TODO 取消或者减少委托
        @staticmethod
        def delegate(amount: int, username: str, fees=100):
            """创建/追加 活期质押，修改"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking delegate  {amount}{Tx.coin.get('c')} --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        @staticmethod
        def undelegate(from_addr, amount, fees):
            """
            减少活期质押:
            1.减少质押金额 >= 实际质押额 则按实际质押额兑付 并主动发放收益
            2.减少质押金额 < 实际质押额 则按传入金额兑付, 收益重新计算但不主动发放
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking undelegate --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def exit_delegate(from_addr, delegator_address, fees):
            """
            退出活期质押
            :param from_addr: 发起方地址  【超管、区管理员、用户自己】
            :param delegator_address: 被清退质押者地址
            :param fees:
            :return:
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking exit-delegate --from={from_addr} " \
                                f"--delegator-address={delegator_address} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"

            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def delegate_fixed(from_addr, amount, term, fees):
            """创建活期周期质押"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking delegate-fixed --from={from_addr} --amount={amount}{Tx.coin['c']} --fixed_delegation_term={term} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def delegate_infinite(from_addr, amount, fees):
            """创建活期永久质押"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking delegate-infinite --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def undelegate_fixed(from_addr, fixed_delegation_id, fees, gas=200000):
            """减少活期周期质押"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking undelegate-fixed --from={from_addr} --fixed_delegation_id={fixed_delegation_id} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def undelegate_infinite(from_addr, amount, fees):
            """减少活期永久质押"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking undelegate-infinite --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def withdraw(addr, fees, gas=200000):
            """KYC用户提取活期收益"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking withdraw --from={addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def create_fixed_deposit(amount, period, from_addr, fees=1, gas=200000):
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking deposit-fixed {amount}{Tx.coin['c']} {period} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def withdraw_fixed_deposit(deposit_id, from_addr, fees=1, gas=200000):
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking withdraw-fixed {deposit_id} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def set_fixed_deposit_interest_rate(region_id, rate, period, from_addr, fees):
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking set-fixed-deposit-interest-rate {region_id} {rate} {period} " \
                                f"--from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            handle_console_input.input_password(Tx.channel)
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def new_kyc(addr, region_id, role, from_addr, fees=1, gas=200000):
            """
            创建KYC用户
            :param gas: gas限制 默认200000
            :param addr: kyc address
            :param region_id: 所绑定区域ID
            :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
            :param from_addr: 发起地址 区管理员 or 全局管理员
            :param fees: Gas费用 单位{Tx.coin['c']}
            :return: tx Hash
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking new-kyc {addr} {region_id} {role} --from {from_addr} " \
                                f"-y --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"

            if from_addr != Tx.super_addr:
                # 区管理员 不能创建 KYC_ROlE_ADMIN
                assert "KYC_ROLE_USER" == role
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def remove_kyc(addr, from_addr, fees):
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking remove-kyc {addr} --from={from_addr} -y --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def query_kyc_list():
            """查询KYC用户列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking list-kyc"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            # 没有交互的窗口，直接查询，再来考虑要不要处理
            resp_info = handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

            return resp_info

    class Keys(object):

        @staticmethod
        def add(username):
            """添加用户 重名也会新增,地址不一样  1.3可以用"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys add {username} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(1)
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "existing" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)
            else:
                resp_info = "-" + resp_info.split("-")[-1]

            if "**Important**" in resp_info:
                return handle_resp_data.handle_add_user(resp_info)

        @staticmethod
        def lists():
            """查询用户列表 需要密码,1.3可以直接调用"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys list {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def show(username):
            """查询用户信息， 1.3可以直接用"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys show {username} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def show_address_for_username(username):
            """查询用户地址"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def private_export(username):
            """导出私钥, 1.3已经不能用了"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys export {username} --unsafe --unarmored-hex {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(3)
            resp_info = handle_console_input.ready_info(Tx.channel)
            if "private key will be exported" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def private_export_meuser(username=None):
            """传入name导出用户私钥，1.3可用"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

    class Query(object):
        """ 这个类主要用来查询相关操作"""

        @staticmethod
        def query_staking_validator():
            """查看验证者节点列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} query staking validators"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_bank_balance_username(username: str):
            """根据用户名，查询余额"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q bank balances {Tx.Keys.private_export_meuser(username)} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            dict_resp_info = handle_resp_data.handle_yaml_to_dict(resp_info)
            if dict_resp_info.get('balances') == []:  # 判断余额是否为空，为空就余额等于0，用作下面计算
                return 0
            else:
                return int(dict_resp_info.get('balances')[0].get('amount'))

            # return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_bank_balance_adders(address: str):
            """根据地址私钥，查询余额 ，一般用作模块账户查找"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q bank balances {address} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_validator_list():
            """查找验证者列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} query staking validators"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        # @staticmethod
        # def query_staking_validator_from_node_name(node_name: str):
        #     """根据node名称查找对应的节点地址"""
        #     dict_validator_list = Tx.Query.query_staking_validator_list()
        #     moniker_to_find = node_name
        #     operator_address = None
        #     for validator in dict_validator_list['validators']:
        #         if validator['description']['moniker'] == moniker_to_find:
        #             operator_address = validator['operator_address']
        #             break
        #     return operator_address
        #     # return dicta

        @staticmethod
        def query_staking_list_region():
            """查看区列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking list-region {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_list_kyc():
            """查看区列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking list-kyc {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_delegate(username: str):
            """根据用户名区，查看自己的活期委托"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking delegation $({Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}) {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)


if __name__ == '__main__':
    username = "nokycwangzhibiao"
    adderss = "cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77"
    # 国库转给管理员
    # Tx.SendToAdmin.send_to_admin_fees(amount=10000,fees=100)
    # 用户转账
    # Tx.SendToAdmin.send_admin_to_user(to_account="nokycwangzhibiao",amounts=10000,fees=100)
    # Tx.SendToAdmin.count_down_5s()
    # 查询余额
    # print(Tx.Query.query_bank_balance_username(username="nokycwangzhibiao"))
    # 查询用户address
    # print(Tx.Keys.private_export_meuser(username=username))
    # 发起质押
    Tx.Staking.delegate(amount=1, username=username, fees=100)
    # 查询质押
    Tx.SendToAdmin.count_down_5s()
    print(Tx.Query.query_staking_delegate(username=username))

    # print(Tx.Staking.query_kyc_list())
    # py_01 = Tx().staking.remove_kyc("sil1jqjtm7dge0ja64spr3wfgs8f6rnfg9ayj0lu6x",
    #                                 "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh", 1, True)
    # print(py_01)
    # pub = '\'{"type": "tendermint/PubKeyEd25519","value": "a9UxLb0DuMJ0Y584VjSe+FWvJiglV4STErFSfT0Cd0Q="}\''

    # res = Tx().staking.create_validator(pub, "node2", "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh", 1)
    # res = Tx().staking.update_validator("silvaloper1jxrauca2fdrwyvtzmelv5td84wpjqd9f6rks4c", "CZE",
    #                                     "sil1xxvavly4p87d6t3jkktp6pvt0jhystt48kwglh", 1)
    # res = Tx().staking.do_fixed_deposit(10, "PERIOD_3_MONTHS", "sil155mv39aqtl234twde44wrjdd5phxx28mg46u3p", 1)
    # print(res)

    # send_user = tx.SendToAdmin.send_admin_to_user()
    # v = tx.SendToAdmin.creation_validator_node()
    # q = tx.SendToAdmin.query_staking_validator()
    # riegion = tx.SendToAdmin.creation_region(region_id=8,region_name="KOR")
    # riegion_list = tx.SendToAdmin.query_staking_list_region()
    # keys_list = tx.Keys.lists()

    # add_key = tx.Keys.show("testpython")
    # print(add_key)
    # print(type(add_key))
    # print(keys_list)
    # print(type(keys_list))
    # pe = tx.keys.private_export_meuser("kycwangzhibiao")
    # print(pe)
    # print(type(pe))
    # print(q)
    # print(type(q))
    #
    # print(Tx.Keys.private_export_meuser(username="kycwangzhibiao"))
    # print(r)
    # print(Tx.query.query_staking_validator())
    # print(Tx.SendToAdmin.tx_bank_send(from_address="superadmin", to_address="kycwangzhibiao", amounts=1))
    # print(Tx.SendToAdmin.query_bank_balance(address="kycwangzhibiao"))
    # print(send_user)
    # print(Tx.SendToAdmin.query_staking())
    # print(Tx.SendToAdmin.query_staking_validator_from())
    # print(type(Tx.SendToAdmin.query_staking_validator_from()))
    import sys
    # print("1")
    # print(Tx.Query.query_bank_balance_adders(adders="cosmos1quarn305vjusjaqxzdm8du09w63gjx36ue0aqq"))
    # print(Tx.SendToAdmin.send_to_admin_fees(amout=13000,fees=100))
    # time.sleep(5)
    # print(Tx.Query.query_bank_balance_username(username="superadmin"))
    # print(Tx.Query.query_bank_balance_adders(adders="cosmos1quarn305vjusjaqxzdm8du09w63gjx36ue0aqq"))
    # print(Tx.Query.query_staking_list_kyc())

    # print(Tx.SendToAdmin.send_admin_to_user(to_account="kycwangzhibiao", amounts=1000000, fees=100))
    # time.sleep(5)
    # print(Tx.Keys.show_address_for_username("kycwangzhibiao"))
    # print(Tx.Query.query_bank_balance_username(username="kycwangzhibiao"))
    # print(Tx.Query.query_staking_delegate(username="kycwangzhibiao"))
    # dict2 = Tx.Query.query_staking_validator_list()
    # for key,value in dict2.items():
    #     print(key,value)
    # def fun():
    #     dict2 = Tx.Query.query_staking_validator_list()
    #     moniker_to_find = 'node2'
    #     operator_address = None
    #     for validator in dict2['validators']:
    #         if validator['description']['moniker'] == moniker_to_find:
    #             operator_address = validator['operator_address']
    #             break
    #     return operator_address
    # dict2 = Tx.Query.query_staking_validator_list()
    # for k in dict2['validators']:
    #     print(k)
    # print(Tx.SendToAdmin.creation_validator_node(node_name="node3", amounts=1000))
    # print(Tx.SendToAdmin.creation_region(region_id=3, region_name="KOR", validator_node_name="node3"))
    # print(Tx.Keys.show_address_for_username(username="kycwangzhibiao"))
    # print(Tx.Query.query_staking_validator_from_node_name(node_name="node1"))
    # print(type(dict2))
    # for key, value in dict2.items():
    #     print(key, value)
    # d = Tx.Keys.lists()
    # for v in d:
    #     print(v)
    # Tx.SendToAdmin.start_script()
    # Tx.SendToAdmin.send_to_admin()
    # Tx.SendToAdmin.count_down_5s()
    # Tx.SendToAdmin.send_admin_to_user(to_account="nokycwangzhibiao003",amounts=10000,fees=0)
    # a = "cosmos1vw6kpnmtuffex6qfp4m3uck7pxn9yn7f7hldk0"
    # Tx.SendToAdmin.count_down_5s()
    # print(Tx.Query.query_bank_balance_username(username="nokycwangzhibiao002"))
    # print(type(Tx.Query.query_bank_balance_username(username="nokycwangzhibiao002")))
    # print(Tx.Query.query_staking_delegate(username="nokycwangzhibiao003"))
    # Tx.SendToAdmin.tx_bank_send(from_address="nokycwangzhibiao002",to_address="nokycwangzhibiao003",amounts=312500000,fees=)
    # Tx.SendToAdmin.send_to_admin_fees(amout=1000,fees=0)
    # Tx.SendToAdmin.send_admin_to_user(to_account="nokycwangzhibiao002",amounts=100,fees=100)
    # key_list = Tx.Keys.lists()
    # for i in key_list:
    #     print(i)
    # Tx.SendToAdmin.send_admin_to_user(to_account="nokycwangzhibiao")
    # print(Tx.Query.query_bank_balance_username(username="nokycwangzhibiao002"))
    # validator_list = Tx.Query.query_staking_validator_list()
    # for validators in validator_list["validators"]:
    #     print(validators)
    # print(type(r_list))
    # list2 = Tx.Query.query_staking_list_kyc()
    # for k in list2["kyc"]:
    #     print(k)
    # print(list2)
    # print(type(list2))
    # # info_data = Tx.Query.query_staking_validator()
    # print(Tx.Query.query_bank_balance_adders(adders="cosmos1quarn305vjusjaqxzdm8du09w63gjx36ue0aqq"))
    # Tx.SendToAdmin.send_to_admin_fees(amout=1000000,fees=100)
    # time.sleep(5)
    # print(Tx.Query.query_bank_balance_adders(adders="cosmos1quarn305vjusjaqxzdm8du09w63gjx36ue0aqq"))
