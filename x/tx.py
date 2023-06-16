# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import inspect
import json
import math
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

        @staticmethod
        def rewards_nokyc(username: str, amount: int, fees=100):
            """
            获取收益的方法
            Args:
                username(str): 质押的用户
                amount(int) : 质押金额和取出的金额

            """
            balances = Tx.Query.query_bank_balance_username(username=username)  # 查询用户余额，且把余额金额拿出来
            print("该用户起始的余额为：", balances)
            Tx.Staking.delegate(amount=amount, username=username, fees=100)  # 先委托存进去一定金额
            Tx.SendToAdmin.count_down_5s()  # 等待五秒 查询开始快高
            Tx.SendToAdmin.count_down_5s()  # 怕太快了，再等等
            Tx.SendToAdmin.count_down_5s()  # 怕太快了，再等等
            start_height = Tx.Query.query_staking_delegate_start_height(username=username)  # 查询质押 返回质押开始时的快高

            hash_value = Tx.Staking.delegate_unkycunbond_height(amount=amount, username=username)  # 取出来并且取得哈希
            # time.sleep(6)
            # end_height =Tx.Staking.delegate_unkycunbond_height(amount=amount,username=username) # 取出全部质押，且获取取出时的快高
            end_height = Tx.Query.query_tx_height(hash_value=hash_value)  # 根据取出来的hash，获得取出时的块高

            oneself_height_reward = math.ceil(((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))  # 单块全网总收益 793mec
            rewards_one_blok = oneself_height_reward * (amount / (200 * 10 ** 8))  # 全网总收益 x 全网质押比例， 就是出块时个人出块总收益mec
            rewaeds = (rewards_one_blok * (end_height - start_height)) * 10 ** 6  # 单块个人收益乘以经历的块数 等于单人在这个区块差之间的收益总收益

            # b = '( 结束块高 - 开始块高 )  - 手续费'
            # 最终余额为：开始余额+收益减去两次手续费
            end_balances = balances - (amount * 10 ** 6) + rewaeds - fees - fees
            print("该用户活期委托结束后经过计算的余额为：", end_balances)
            query_balances = Tx.Query.query_bank_balance_username(username=username)  # 查询用户余额，
            print("看看是不是相等的最后查询到的余额为：", query_balances)
            return end_balances

        @staticmethod
        def rewards_nokyc_for_course_height_amount(amount: int, course_height: int):
            """
            非KYC用户，传入快高差，委托金额，计算收益

            Args:
                amount(int): 被委托的金额，
                course_height(int): 经历的快高

            Return:
                收益金额 单位umec
            """
            oneself_height_reward = math.ceil(((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))  # 单块全网总收益 793mec
            rewards_one_blok = oneself_height_reward * (amount / (200 * 10 ** 8))  # 全网总收益 x 全网质押比例， 就是出块时个人出块总收益mec
            rewaeds = (rewards_one_blok * course_height) * 10 ** 6  # 单块个人收益乘以经历的块数 等于单人在这个区块差之间的收益总收益 且换算成了umec
            rewaeds_umec_unfees = rewaeds - 100
            # print(type(rewaeds_umec_unfees))

            return int(rewaeds_umec_unfees)

        @staticmethod
        def rewards_kyc_for_course_height_amount(amount: int, course_height: int):
            """
            非KYC用户，传入快高差，委托金额，计算收益

            Args:
                amount(int): 被委托的金额，
                course_height(int): 经历的快高

            Return:
                收益金额 单位umec
            """
            oneself_height_reward = math.ceil(((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))  # 单块全网总收益 793mec
            rewards_one_blok = oneself_height_reward * (
                    (amount + 1) / (200 * 10 ** 8))  # 全网总收益 x 全网质押比例， 就是出块时个人出块总收益mec
            rewaeds = (rewards_one_blok * course_height) * 10 ** 6  # 单块个人收益乘以经历的块数 等于单人在这个区块差之间的收益总收益 且换算成了umec
            rewaeds_umec_unfees = rewaeds - 100
            # print(type(rewaeds_umec_unfees))

            return int(rewaeds_umec_unfees)

        @staticmethod
        def rewards_kyc(username: str, amount: int, fees=100):
            """
            获取收益的方法
            Args:
                username(str): 质押的用户
                amount(int) : 质押金额和取出的金额

            """
            balances = Tx.Query.query_bank_balance_username(username=username)  # 查询用户余额，且把余额金额拿出来
            print("该用户起始的余额为：", balances)
            Tx.Staking.delegate(amount=amount, username=username, fees=100)  # 先委托存进去一定金额
            Tx.SendToAdmin.count_down_5s()  # 等待五秒 查询开始快高
            Tx.SendToAdmin.count_down_5s()  # 怕太快了，再等等
            Tx.SendToAdmin.count_down_5s()  # 怕太快了，再等等
            start_height = Tx.Query.query_staking_delegate_start_height(username=username)  # 查询质押 返回质押开始时的快高

            hash_value = Tx.Staking.delegate_unkycunbond_height(amount=amount, username=username)  # 取出来并且取得哈希
            time.sleep(6)
            # end_height =Tx.Staking.delegate_unkycunbond_height(amount=amount,username=username) # 取出全部质押，且获取取出时的快高
            end_height = Tx.Query.query_tx_height(hash_value=hash_value)  # 根据取出来的hash，获得取出时的块高

            oneself_height_reward = math.ceil(((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))  # 单块全网总收益 793mec
            rewards_one_blok = oneself_height_reward * (
                    (amount + 1) / (200 * 10 ** 8))  # 全网总收益 x 全网质押比例， 就是出块时个人出块总收益mec
            rewaeds = (rewards_one_blok * (end_height - start_height)) * 10 ** 6  # 单块个人收益乘以经历的块数 等于单人在这个区块差之间的收益总收益

            # b = '( 结束块高 - 开始块高 )  - 手续费'
            # 最终余额为：开始余额+收益减去两次手续费
            end_balances = balances + rewaeds - fees - fees
            print("该用户活期委托结束后经过计算的余额为：", end_balances)
            query_balances = Tx.Query.query_bank_balance_username(username=username)  # 查询用户余额，
            print("看看是不是相等的最后查询到的余额为：", query_balances)
            return end_balances

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

        def send_to_treasury_fees(amount: int, fees=100):
            """管理员转钱给国库，有手续费，作为一种场景"""

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank sendToTreasury {amount}{Tx.coin.get('c')} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.keyring_backend}  {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')}"

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
        def tx_bank_send(from_address_name: str, to_address_name: str, amounts: float, fees=100):
            """
            根据用户名，A用户给B用户打钱

            Args:
                from_address_name: 转出用户的名字
                to_address_name: 接收转账的用户的名字
                amounts: 转账的金额 单位是mec
                fees: 手续费 单位是umec

            Return:
                返回的是控制台的输出结果
            """

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx bank send {Tx.Keys.private_export_meuser(username=from_address_name)} {Tx.Keys.private_export_meuser(username=to_address_name)} {amounts}{Tx.coin.get('c')} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')} "
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
            Tx.SendToAdmin.send_to_admin_fees(amout=10000, fees=0)
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
        #
        # @staticmethod
        # def ag_to_ac(ag_amount, from_addr, fees):
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking ag-to-ac {ag_amount}{Tx.coin['g']} --from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(3)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def create_region(region_name, region_id, total_as, delegators_limit, fee_rate,
        #                   from_addr, totalStakeAllow, userMaxDelegateAC, userMinDelegateAC, fees, gas=200000):
        #     """
        #     创建区
        #     :param region_name: 区名称
        #     :param region_id: 区ID
        #     :param total_as: 区所占AS权重
        #     :param delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
        #     :param fee_rate: 区内KYC用户手续费比例
        #     :param from_addr: 发起方地址
        #     :param totalStakeAllow: 质押水位上限
        #     :param userMaxDelegateAC: 区内用户最大质押额
        #     :param userMinDelegateAC: 区内用户最小质押额
        #     :param fees: Gas费用
        #     :param gas: gas 默认为 200000
        #     :return:
        #     """
        #
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking create-region --region-name={region_name} " \
        #                         f"--region-id={region_id} --total-as={total_as} " \
        #                         f"--delegators-limit={delegators_limit} " \
        #                         f"--totalStakeAllow={totalStakeAllow} " \
        #                         f"--fee-rate={fee_rate} " \
        #                         f"--userMaxDelegateAC={userMaxDelegateAC} " \
        #                         f"--userMinDelegateAC={userMinDelegateAC} " \
        #                         f"--from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #     # handle_console_input.input_password(Tx.channel)
        #     time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     try:
        #         return handle_resp_data.handle_split_esc_re_code(resp_info)
        #     except Exception:
        #         error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
        #         return error_info
        #
        # @staticmethod
        # def update_region(region_id, from_addr, fees, region_name=None, delegators_limit=None,
        #                   fee_rate=None, totalStakeAllow=None, userMaxDelegateAC=None,
        #                   userMinDelegateAC=None, isUndelegate=None):
        #     """
        #     修改区信息
        #     :param region_name: 区名称
        #     :param region_id: 区ID
        #     :param delegators_limit: 区内委托上限人数（-1表示没有限制，0表示不允许质押，其他数值表示人数限制）
        #     :param fee_rate: 区内KYC用户手续费比例
        #     :param from_addr: 发起方地址
        #     :param totalStakeAllow: 质押水位上限
        #     :param userMaxDelegateAC: 区内用户最大质押额
        #     :param userMinDelegateAC: 区内用户最小质押额
        #     :param fees: Gas费用
        #     :return:
        #     """
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking update-region --from={from_addr} --region-id={region_id} " \
        #                         f"--fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend} "
        #     if region_name:
        #         region_name = f"--region-name={region_name} "
        #         cmd += f"{region_name}"
        #     if delegators_limit:
        #         cmd += f"--delegators-limit={delegators_limit} "
        #     if fee_rate:
        #         cmd += f"--fee-rate={fee_rate} "
        #     if totalStakeAllow:
        #         cmd += f"--totalStakeAllow={totalStakeAllow} "
        #     if userMaxDelegateAC:
        #         cmd += f"--userMaxDelegateAC={userMaxDelegateAC} "
        #     if userMinDelegateAC:
        #         cmd += f"--userMinDelegateAC={userMinDelegateAC} "
        #     if isUndelegate:
        #         cmd += f"--isUndelegate={isUndelegate} "
        #
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #     try:
        #         return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #     except Exception:
        #         error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
        #         return error_info
        #
        # @staticmethod
        # def create_validator(pubkey, moniker, from_addr, fees):
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking create-validator --pubkey={pubkey} --moniker={moniker} " \
        #                         f"--from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend} "
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     try:
        #         return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #     except Exception:
        #         error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
        #         return error_info
        #
        # @staticmethod
        # def update_validator(operator_address, region_name, from_addr, fees):
        #     """Only used to modify the Region ID of the verifier"""
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking update-validator --validator-address={operator_address} " \
        #                         f"--region-name={region_name} --from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend} "
        #
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     try:
        #         return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #     except Exception:
        #         error_info = handle_resp_data.HandleRespErrorInfo.handle_rpc_error(resp_info)
        #         return error_info

        #
        # @staticmethod
        # def undelegate(from_addr, amount, fees):
        #     """
        #     减少活期质押:
        #     1.减少质押金额 >= 实际质押额 则按实际质押额兑付 并主动发放收益
        #     2.减少质押金额 < 实际质押额 则按传入金额兑付, 收益重新计算但不主动发放
        #     """
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking undelegate --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def exit_delegate(from_addr, delegator_address, fees):
        #     """
        #     退出活期质押
        #     :param from_addr: 发起方地址  【超管、区管理员、用户自己】
        #     :param delegator_address: 被清退质押者地址
        #     :param fees:
        #     :return:
        #     """
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking exit-delegate --from={from_addr} " \
        #                         f"--delegator-address={delegator_address} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def delegate_fixed(from_addr, amount, term, fees):
        #     """创建活期周期质押"""
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking delegate-fixed --from={from_addr} --amount={amount}{Tx.coin['c']} --fixed_delegation_term={term} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def delegate_infinite(from_addr, amount, fees):
        #     """创建活期永久质押"""
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking delegate-infinite --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def undelegate_fixed(from_addr, fixed_delegation_id, fees, gas=200000):
        #     """减少活期周期质押"""
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking undelegate-fixed --from={from_addr} --fixed_delegation_id={fixed_delegation_id} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def undelegate_infinite(from_addr, amount, fees):
        #     """减少活期永久质押"""
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking undelegate-infinite --from={from_addr} --amount={amount}{Tx.coin['c']} --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def withdraw(addr, fees, gas=200000):
        #     """KYC用户提取活期收益"""
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking withdraw --from={addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(1)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def create_fixed_deposit(amount, period, from_addr, fees=1, gas=200000):
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking deposit-fixed {amount}{Tx.coin['c']} {period} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(3)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def withdraw_fixed_deposit(deposit_id, from_addr, fees=1, gas=200000):
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking withdraw-fixed {deposit_id} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #
        #     time.sleep(3)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
        #
        # @staticmethod
        # def set_fixed_deposit_interest_rate(region_id, rate, period, from_addr, fees):
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking set-fixed-deposit-interest-rate {region_id} {rate} {period} " \
        #                         f"--from={from_addr} --fees={fees}{Tx.coin['c']} {Tx.chain_id}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     Tx.channel.send(cmd + "\n")
        #     handle_console_input.input_password(Tx.channel)
        #     time.sleep(3)
        #     resp_info = handle_console_input.ready_info(Tx.channel)
        #
        #     if "confirm" in resp_info:
        #         resp_info = handle_console_input.yes_or_no(Tx.channel)
        #
        #     return handle_resp_data.handle_split_esc(resp_info)
        #
        # @staticmethod
        # def new_kyc(addr, region_id, role, from_addr, fees=1, gas=200000):
        #     """
        #     创建KYC用户
        #     :param gas: gas限制 默认200000
        #     :param addr: kyc address
        #     :param region_id: 所绑定区域ID
        #     :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
        #     :param from_addr: 发起地址 区管理员 or 全局管理员
        #     :param fees: Gas费用 单位{Tx.coin['c']}
        #     :return: tx Hash
        #     """
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking new-kyc {addr} {region_id} {role} --from {from_addr} " \
        #                         f"-y --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend}"
        #
        #     if from_addr != Tx.super_addr:
        #         # 区管理员 不能创建 KYC_ROlE_ADMIN
        #         assert "KYC_ROLE_USER" == role
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))
        #
        # @staticmethod
        # def remove_kyc(addr, from_addr, fees):
        #     cmd = Tx.ssh_home + f"{Tx.chain_bin} tx srstaking remove-kyc {addr} --from={from_addr} -y --fees={fees}{Tx.coin['c']} {Tx.chain_id} {Tx.keyring_backend}"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

        @staticmethod
        def delegate(amount: int | float, username: str, fees=100):
            """
            创建/追加 活期质押，已修改，返回的是发起交易时的块高，方便后面计算用
            Args:
                amount(int | float): "是以mec为单位传入的"
                username(str): "用户名称，可以通过配置文件的变量传入，"
                fees(int): ”是以umec为单位传入的，默认是100umec“

            """

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking delegate  {amount}{Tx.coin.get('c')} --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            # time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)
                time.sleep(1)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

            return resp_info_dict.get("txhash")

        @staticmethod
        def query_kyc_list():
            """查询KYC用户列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking list-kyc"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            # 没有交互的窗口，直接查询，再来考虑要不要处理
            resp_info = handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))

            return resp_info

        @staticmethod
        def delegate_kycunbond_txhash(amount: int, username: str, fees=100):
            """
            KYC用户取消或者减少 活期质押， 返回的值是交易的hash
            Args:
                amount(int): 减少的金额
                username(str): 用户的name
                fees(int): 手续费
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking unbond {amount}{Tx.coin.get('c')} --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

            return resp_info_dict.get("txhash")

        @staticmethod
        def delegate_unkycunbond_txhash(amount: int, username: str, fees=100):
            """
            非KYC用户取消或者减少 活期质押， 返回的值是交易的hash
            Args:
                amount(int): 减少的金额
                username(str): 用户的name
                fees(int): 手续费
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking unKycUnbond {amount}{Tx.coin.get('c')} --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

            return resp_info_dict.get("txhash")

        @staticmethod
        def delegate_unkycunbond_height(amount: int | float, username: str, fees=100):
            """
            非KYC用户取消或者减少 活期质押， 返回的值是交易的hash
            Args:
                amount(int | float): 减少的金额
                username(str): 用户的name
                fees(int): 手续费，不填就是默认100
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking unKycUnbond {amount}{Tx.coin.get('c')} --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
            hash_value = resp_info_dict.get("txhash")
            # Tx.Query.query_tx_height()
            # time.sleep(1)

            return hash_value


        @staticmethod
        def distribution_withdraw_rewards(username: str, fees=100):
            """
            设计提取自己活期的收益的方法

            Args:
                username: 用户的名字

            Return:
                返回的是交易时的哈希，方便查询错误
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx distribution withdraw-rewards --from={Tx.Keys.private_export_meuser(username=username)} {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)
            hash_value = resp_info_dict.get("txhash")
            return resp_info_dict

        @staticmethod
        def deposit_fixed(amount:int | float,months: int, username: str,fees=100):
            """
            发起定期委托的方法，
            Args:
                amount(int | float): 委托金额
                months(int): 委托期限，月数，1，3，6，12，36，48
                username(str): 用户名称，根据用户名称会自动转换成地址
                fees(int): 手续费，默认100已设置好，可以不用传

            Return:
                返回出去的是code为0和哈希值，没有做其他的事
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking deposit-fixed {amount}{Tx.coin.get('c')} Term_{months}_MONTHS --from=$({Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}) {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            # time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)
                time.sleep(1)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

            return resp_info_dict


        @staticmethod
        def withdraw_fixed(fixed_id: int, username: str, fees=100):
            """
            取出定期,传入定期的id和用户的名称去取
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking withdraw-fixed {fixed_id}  --from=$({Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}) {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")

            # time.sleep(1)  # 执行速度太快会导致 控制台信息未展示完全就将数据返回
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)
                time.sleep(1)

            resp_info_dict = handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

            return resp_info_dict

        @staticmethod
        def creation_validator_node(node_name: str, amounts=100, fees=100):
            """
            创世后创建验证者节点  传入node_name将节点升级成验证者
            Args:
                node_name(str): 节点名称，node2之类
                amounts(int): 节点staking值 默认100 可不填
                fees(int): 默认100，不用填

            return：
                返回页面？
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking create-validator --amount={amounts}{Tx.coin.get('c')} --pubkey=$(./me-chaind tendermint show-validator --home {node_name}) --moniker={node_name} --commission-rate=\"0.10\" --commission-max-rate=\"0.20\" --commission-max-change-rate=\"0.01\" --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend}) {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)


        @staticmethod
        def edit_validator_owner_address(node_name: str, to_username: str, fees=100):
            """
            修改验证者节点的gas费归属用户

            Args:
                node_name: 节点名称
                username: 需要售卖的用户名称
            """
            cmd = Tx.ssh_home + f"./me-chaind tx staking edit-validator $(./me-chaind  q staking validators | grep '{node_name}' -A 6 | awk '/operator_address/ {{print $2}}')  --owner-address=$({Tx.chain_bin} keys show {to_username} -a {Tx.keyring_backend}) {Tx.chain_id} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend}) {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')} {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def validator_node_stake_increase(node_name: str, amount: int, fees=100):
            """
            根据区名称查找节点的地址，再根据节点地址增加验证者节点的staking值，
            Args:
                node_name(str): 区名称
                amount(int): 需要增加的金额
                fees: 固定100umec
            """
            cmd = Tx.ssh_home + f"./me-chaind tx staking stake {Tx.Query.query_staking_validator_from_node_name(node_name=node_name)}  {amount}{Tx.coin.get('c')} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend}) {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def validator_node_stake_unstake(node_name: str, amount: int, fees=100):
            """
            根据区名称查找节点的地址，再根据节点地址减少验证者节点的staking值，
            Args:
                node_name(str): 区名称
                amount(int): 需要增加的金额
                fees: 固定100umec
            """
            cmd = Tx.ssh_home + f"./me-chaind tx staking unstake {Tx.Query.query_staking_validator_from_node_name(node_name=node_name)}  {amount}{Tx.coin.get('c')} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend}) {Tx.chain_id} {Tx.keyring_backend} --fees={fees}{Tx.coin.get('uc')}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def new_region(region_name: str, node_name=None, fees=100):
            """
            根据node_name获取节点地址
            根据节点地址，绑定对应的区
            Args:
                region_name(str): 区名称，可以用来
                node_name(str): 节点名称，可以使用你创建验证者节点时的名称
                fees(int): 默认100，不用填

            return：
                返回的是页面？，可以改成返回区id？

            """
            region_id = f"{region_name}id"
            validator_address = Tx.Query.query_staking_validator_from_node_name(node_name=node_name)
            # print(validator_address)
            # validator_address2 = f"{Tx.chain_bin} q staking validators | grep {node_name} -A 6 | awk '\/operator_address/{print $2}\'"
            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking new-region {region_id} {region_name}  {validator_address}  --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.keyring_backend} {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')} "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            Tx.channel.send(cmd + "\n")  # 发送命令行
            resp_info = handle_console_input.ready_info(Tx.channel)  # 抓取输出的命令行
            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)  # 处理yee or no

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

        @staticmethod
        def new_kyc_for_username(user_name: str, region_name: str, fees=100):
            """
            传入用户名称，和区名称，进行用户kyc认证，区名称会自动转化成区ID，
            """
            # 根据区名称查询区ID？因为区名称已经被定义了。

            region_id = f"{region_name}id"

            cmd = Tx.ssh_home + f"{Tx.chain_bin} tx staking new-kyc {Tx.Keys.show_address_for_username(username=user_name)}  {region_id} --from=$({Tx.chain_bin} keys show superadmin -a {Tx.keyring_backend})  {Tx.keyring_backend}  {Tx.chain_id} --fees={fees}{Tx.coin.get('uc')} "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 当有需要交互的时候，调用Tx下的channel下的send方法
            Tx.channel.send(cmd + "\n")
            resp_info = handle_console_input.ready_info(Tx.channel)

            if "confirm" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_input_y_split_esc_re_code(resp_info)

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
        def lists_test():
            """
            查询用户列表 返回出去的是用户姓名的列表
             """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys list {Tx.keyring_backend}"
            # logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            keys_list = handle_resp_data.handle_yaml_to_dict(Tx.ssh_client.ssh(cmd))
            name = []
            for i in keys_list:
                a = i.get('name')
                name.append(a)

            return name

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
            """
            根据用户的名字，导出用户的私钥

            Args:
                username(str): 用户名字

            Return:
                用户私钥
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} keys export {username} --unsafe --unarmored-hex {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(2)
            resp_info = handle_console_input.ready_info(Tx.channel)
            if "private key will be exported" in resp_info:
                resp_info = handle_console_input.yes_or_no(Tx.channel)

            return handle_resp_data.handle_split_esc(resp_info)

        @staticmethod
        def private_export_meuser(username=None):
            """
            传入name导出用户地址，1.3可用

            Args:
                username(str): 用户名称

            Return:
                返回用户的地址
            """
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
            """
            根据用户名，查询余额

            Return:
                用户余额数字，如果没有就返回0
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q bank balances {Tx.Keys.private_export_meuser(username)} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            dict_resp_info = handle_resp_data.handle_yaml_to_dict(resp_info)
            if dict_resp_info == None:
                return ("没有查询到该用户")

            elif dict_resp_info.get('balances') == []:  # 判断余额是否为空，为空就余额等于0，用作下面计算
                return 0
            else:
                return int(dict_resp_info.get('balances')[0].get('amount'))

            # return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_bank_balance_for_adders(address: str):
            """
            根据地址，查询余额 ，一般用作模块账户查找

            Args:
                address(str):用户地址
            Return:
                用户余额
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q bank balances {address} {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_validator_list():
            """查找验证者列表 已经遍历了，无需print"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} query staking validators"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            validator_list = handle_resp_data.handle_yaml_to_dict(resp_info).get('validators')
            for i in validator_list:
                print(i)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_validator_from_node_name(node_name: str):
            """根据node名称查找对应的节点地址"""
            dict_validator_list = Tx.Query.query_staking_validator_list()
            moniker_to_find = node_name
            operator_address = None
            for validator in dict_validator_list['validators']:
                if validator['description']['moniker'] == moniker_to_find:
                    operator_address = validator['operator_address']
                    break
            return operator_address
            # return dicta

        @staticmethod
        def query_staking_list_region():
            """
            查看区列表，无需传参，已经遍历了，不用print，
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking list-region {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            list_region = handle_resp_data.handle_yaml_to_dict(resp_info).get('region')
            for i in list_region:
                print(i)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_list_kyc():
            """查看kyc用戶列表"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking list-kyc {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_delegate(username: str):
            """根据用户名，查看自己的活期委托,返回的结果没有做处理，需要print"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking delegation $({Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}) {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            logger.info(inspect.stack())
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_distribution_rewards_form_name(username: str):
            """
            实时查询用户活期委托所产生的利息，
            Args:
                username(str): 用户名称
            Return:
                return: 返回全部
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} query distribution rewards $({Tx.chain_bin} keys show {username} -a {Tx.keyring_backend})"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_delegate_start_height(username: str):
            """根据用户名区，查看自己的活期委托"""
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q staking delegation $({Tx.chain_bin} keys show {username} -a {Tx.keyring_backend}) {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            resp_info_dict = handle_resp_data.handle_yaml_to_dict(resp_info)  # 接收响应内容
            print("开始快高为：", resp_info_dict.get("delegation").get('startHeight'))

            return int(resp_info_dict.get("delegation").get('startHeight'))  # 获取快高，且返回成int类型供后面计算

        @staticmethod
        def query_tx_height(hash_value=None):
            """
            根据响应回来的hash值，查询响应结果，并且返回块高
            """
            # time.sleep(1)
            Tx.SendToAdmin.count_down_5s()
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q tx {hash_value} --chain-id=me-chain"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            resp_info = Tx.ssh_client.ssh(cmd)

            # time.sleep(2)
            # print("resp_info内容是：",resp_info)
            # print("resp_info的类型是：", type(resp_info))
            # time.sleep(5)
            resp_info_dict = handle_resp_data.handle_yaml_to_dict(resp_info)
            # print(f"resp_info_dict的类型为：",type(resp_info_dict))
            # time.sleep(2)
            height = resp_info_dict.get("height")
            print("结束时的height快高是", height)
            # print("height的类型是",type(height))
            int_height = int(height)

            return int_height

        @staticmethod
        def query_tx_hash(hash_value=None):
            """
            根据响应回来的hash值，查询响应结果，并且返回块高
            """
            # time.sleep(1)
            # Tx.SendToAdmin.count_down_5s()
            cmd = Tx.ssh_home + f"{Tx.chain_bin} q tx {hash_value}  --chain-id=me-chain"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            resp_info = Tx.ssh_client.ssh(cmd)

            # time.sleep(2)
            # print("resp_info内容是：",resp_info)
            # print("resp_info的类型是：", type(resp_info))
            # time.sleep(5)
            resp_info_dict = handle_resp_data.handle_yaml_to_dict(resp_info)
            # print(f"resp_info_dict的类型为：",type(resp_info_dict))
            # time.sleep(2)
            # height = resp_info_dict.get("height")
            # print("结束时的height快高是", height)
            # print("height的类型是",type(height))
            # int_height = int(height)

            return resp_info_dict

        # 查询所有定期委托
        @staticmethod
        def query_list_fixed_deposit():
            """
            查询所有的定期委托列表，不需要传参，函数方法内已经进行了遍历打印，不需要print，

            Return:
                返回出的是一个列表，
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} query staking list-fixed-deposit"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            resp_info_dict = handle_resp_data.handle_yaml_to_dict(resp_info)
            resp_info_list = resp_info_dict.get('FixedDeposit')
            # fixde_dict = {key:value for key ,value in resp_info_list}
            # for e in resp_info_list:
            #
            for my_dict in resp_info_list:
                print(my_dict)
                # for i in my_dict.get('id'):
                # value = my_dict.get('id')
                # print(i)

            #     print(e)

            return resp_info_list


        @staticmethod
        def query_list_fixed_deposit_for_username(username):
            """
            根据个人用户名称查询个人所有的定期委托，返回出去的是个人所有委托的列表，如果没有委托，就返回一个没有元素的空列表
            """
            cmd = Tx.ssh_home + f"{Tx.chain_bin} query staking show-fixed-deposit-by-acct {Tx.Keys.show_address_for_username(username=username)}  ALL_STATE {Tx.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")  # logger插入
            # 如果是没有交互的话，直接查询这种情况，就调用Tx下的ssh_client.ssh方法就可以了
            resp_info = Tx.ssh_client.ssh(cmd)
            resp_info_dict = handle_resp_data.handle_yaml_to_dict(resp_info)
            resp_info_list = resp_info_dict.get('FixedDeposit')

            return resp_info_list

        # TODO 计算块高
        @staticmethod
        def count_height():
            pass


if __name__ == '__main__':
    # username = "nokycwangzhibiao003"
    # username = "test001"  # cosmos1cjsvfrth4ygc0hqdw9y7hnpwgzdt5mh6vv2lqj
    # username = "test002" # cosmos1lkaqrt9s6glk6lcgk9tt0dnc9a9gmxqlq56pyv
    # username = "wangzhibiao001"

    # username="wangzhibiao001"
    username = "wangzhibiao001"
    # username = "superadmin"
    yue = "1999900"
    node_name = "node2"
    region_name = "USA"
    # adderss = "cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77"
    print("======" * 5, "初始化起始线", "======" * 5)
    # print(Tx.Keys.add(username=username))                         # 添加用戶
    # Tx.SendToAdmin.count_down_5s()
    #
    # Tx.SendToAdmin.send_to_admin_fees(amount=10000, fees=100) # 国库转给管理员
    # Tx.SendToAdmin.count_down_5s()
    # time.sleep(2)
    # print("查询管理员余额：",Tx.Query.query_bank_balance_username("superadmin")) # 查询管理员余额

    # Tx.SendToAdmin.send_admin_to_user(to_account=username, amounts=10001, fees=100) # 管理员给用户转账
    # Tx.SendToAdmin.count_down_5s()
    # time.sleep(1)
    # print(f"{username}该用户余额为:",Tx.Query.query_bank_balance_username(username=username))   # 查询该用户余额
    print(f"{username}该用户地址为:", Tx.Keys.private_export_meuser(username=username))  # 查询用户address
    # Tx.SendToAdmin.tx_bank_send(from_address_name=username,to_address_name=username,amounts=46725,fees=100) # 用户给用户转账
    # Tx.SendToAdmin.count_down_5s()
    # time.sleep(2)
    # print(f"{username}该用户余额为:", Tx.Query.query_bank_balance_username(username=username))  # 查询该用户余额
    # Tx.Staking.new_kyc_for_username(user_name=username, region_name=region_name)  # NEW KYC
    # Tx.SendToAdmin.count_down_5s()
    # Tx.Staking.delegate(amount=20000, username=username, fees=100)                               # 发起质押
    # Tx.SendToAdmin.count_down_5s()
    # print(type(Tx.Staking.delegate_unkycunbond_height(amount=20, username=username, fees=100))) # 赎回质押
    # Tx.SendToAdmin.count_down_5s()
    # print(f"{username}该用户活期委托本金为:",Tx.Query.query_staking_delegate(username=username))  # 查询质押
    # print(f"{username}该用户活期委托实时收益为:",Tx.Query.query_distribution_rewards_form_name(username=username))  # 查询用户活期委托所产生的利息
    # print(Tx.Query.query_staking_delegate_start_height(username=username))

    # print(f"{username}该用户余额为:",Tx.Query.query_bank_balance_username(username=username)) # 查询该用户余额
    # a = Tx.Staking.delegate_unkycunbond_height(username=username, amount=1)   # 减少质押
    # print(a)
    # print(type(a))

    # print("======" * 5, "委托起始线", "======" * 5)
    # a = Tx.Bank.rewards_nokyc(username=username,amount=10,fees=100) #  非KYC发起质押且计算收益，扣除手续费后的收益
    # a = Tx.Bank.rewards_kyc(username=username, amount=10000)    # KYC发起质押且计算收益，扣除手续费后的收益
    # print(a)
    # print(type(a))
    # time.sleep(6)
    # print(f"{username}该用户余额为:",Tx.Query.query_bank_balance_username(username=username)) # 查询该用户余额

    # Tx.Query.query_bank_balance_for_adders()

    # a = "cosmosvaloper1klxpqfh48l57lxmql57ghsumel0ghdcsq97sr5"

    # Tx.Staking.creation_validator_node(node_name=node_name,amounts=50000000)   # 创建验证者节点
    # time.sleep(2)
    # Tx.SendToAdmin.count_down_5s()
    # Tx.Staking.new_region(region_name=region_name, node_name=node_name)   # 创建区
    # Tx.SendToAdmin.count_down_5s()
    # time.sleep(2)
    # print("查询节点列表")
    # Tx.Query.query_staking_validator_list()          # 查询节点列表
    # print("查询区列表")
    # Tx.Query.query_staking_list_region()        # 查询区列表
    # print(Tx.Keys.add(username=username))       # 添加用戶
    # Tx.SendToAdmin.count_down_5s()

    # print(Tx.Keys.show_address_for_username(username=username))  # 通过用户名称查询用户地址
    # Tx.SendToAdmin.count_down_5s()
    # Tx.Staking.new_kyc_for_username(user_name=username,region_name=region_name) #NEW KYC

    # Tx.SendToAdmin.count_down_5s()                # 暂停5秒

    # print(kyc_list)

    print(Tx.Staking.deposit_fixed(amount=10, months=3, username=username))  # 发起定期委托
    # print(Tx.Staking.deposit_fixed(amount=10,months=12,username=username))  #发起定期委托
    # Tx.SendToAdmin.count_down_5s()
    # Tx.Query.query_list_fixed_deposit()                # 查询所有定期委托列表
    # Tx.Query.query_staking_validator_list()
    # Tx.Query.query_staking_list_region()                   #  查询区列表
    # Tx.Staking.validator_node_stake_increase(node_name=node_name, amount=49989907)  # 增加节点对应的staking值
    # Tx.Staking.validator_node_stake_unstake(node_name=node_name,amount=3)  # 减少节点对应的staking值
    # Tx.SendToAdmin.count_down_5s()
    # time.sleep(2)
    # print(Tx.Query.query_staking_validator_from_node_name(node_name=node_name))
    # hash_v = "7E7631939F8497BB6577806F870CF2C7BC372A6C89700A727B2FFAA4D8DF27CA"
    # print(Tx.Query.query_tx_hash(hash_value=hash_v))
    # keys_list = Tx.Keys.lists()  # 查询用户列表
    # for i in keys_list:  # 查询用户列表
    #     print("用户列表：",i)  # 查询用户列表
    #
    # piv = Tx.Keys.private_export(username=username)  # 导出用户私钥
    # print(piv)

    # print("KYC用戶列表如下：")
    # time.sleep(1)
    # kyc_list = Tx.Query.query_staking_list_kyc()  # 查询KYC列表

    # for k in kyc_list.get('kyc'):
    #     print("KYC用户列表：",k)
    # a = Tx.Keys.lists_test()
    # c = Tx.Keys.lists()
    # print(c)
    # for i in a:
    #     print(i)
    #     print(i.get('name'))
    # b = "testname01"
    # if b in a:
    #     print("ture")
    # else:
    #     print("false")
    # print(type(a))
    # print(a)
    # print(f"{username}该用户余额为:", Tx.Query.query_bank_balance_username(username=username))  # 查询该用户余额

    # print(Tx.Bank.rewards_nokyc_for_course_height_amount(amount=10000, course_height=1))
    #
    print("======" * 5, "最后结束线", "======" * 5)
