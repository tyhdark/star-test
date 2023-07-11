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
        def send_tx(from_addr, to_addr, amount, fees=Fees):
            """发送转账交易"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx bank send {from_addr} {to_addr} {amount}{Tx.coin['c']} --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def send_to_admin(amout: int, fees=Fees):
            """国库往超管转钱，不需要传参,传金额就行"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx bank sendToAdmin {amout}{Tx.coin['c']} --from={Tx.super_addr} --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

    class Staking(object):

        # @staticmethod
        # def ag_to_ac(ag_amount, from_addr, fees=Fees, gas=GasLimit):
        #     cmd = Tx.work_home + f"{Tx.chain_bin} tx srstaking ag-to-ac {ag_amount}{Tx.coin['g']} --from={from_addr} --fees={fees}{Tx.coin['c']} --gas={gas} {Tx.chain_id} {Tx.keyring_backend} -y"
        #     logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        #     return Tx._executor(cmd)

        @staticmethod
        def create_region(from_addr, region_name, node_name, fees=Fees):
            """
            创建一个区
            :param from_addr: 发起方地址 需要区域管理员
            :param region_name: 区名称
            :param node_name: 节点名称，方便找节点地址
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
            params_a="region_id, total_as, fee_rate, totalStakeAllow, userMaxDelegateAC,userMinDelegateAC, delegators_limit=-1,  gas=GasLimit,"
            # c = "./me-chaind tx staking new-region  CHN  #验证者节点地址  --from=#超管地址  --keyring-backend=test --chain-id=me-chain --fees=0.00mec "
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking new-region {region_name}  " \
                                 f"$(./me-chaind q staking validators | grep \"{node_name}\" -A 6 | awk '/address/{{print$2}}')" \
                                 f" --from={from_addr} --fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
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
        def create_validator(node_name: str, amout=None, fees=Fees, ):
            """创建验证者节点，需要传入对应的node几,可用"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking create-validator  --amount={amout}{Tx.coin['c']}  " \
                                 f"--pubkey=$({Tx.chain_bin} tendermint show-validator --home=../nodes/{node_name})  " \
                                 f"--moniker=\"{node_name}\" " \
                                 f" --commission-rate=\"0.10\" --commission-max-rate=\"0.20\"  " \
                                 f" --commission-max-change-rate=\"0.01\" --from={Tx.super_addr}  " \
                                 f"--fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
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
            :param gas:
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
        def new_kyc(user_addr, region_id, from_addr, fees=Fees, gas=GasLimit):
            """
            把用户认证成KYC
            :param addr: kyc address
            :param region_id: 所绑定区域ID
            :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
            :param from_addr: 发起地址 区管理员 or 全局管理员
            :param fees: Gas费用 {Tx.coin['c']}
            :param gas: 默认100
            :return: tx Hash
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking new-kyc {user_addr} {region_id}  --from {from_addr} " \
                                 f"--fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"

            # if from_addr != Tx.super_addr:  # 区管理员 不能创建 KYC_ROlE_ADMIN
            #     assert role == config["chain"]["role"]["user"]
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
            # for i in list_region:
            #     print(i)

            return handle_resp_data.handle_yaml_to_dict(resp_info)

        @staticmethod
        def query_staking_list_kyc():
            """查看kyc用戶列表"""
            cmd = Tx.work_home + f"{Tx.chain_bin} q staking list-kyc {Tx.chain_id}"
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

        # TODO 将节点和节点所对应的区组合成一个字典
        @staticmethod
        def node_name_zip_region_name():
            """
            将node名字和区名字组合匹配起来，
            """
            node_name = Tx.Query.query_staking_validator()  # 获取节点信息，包含验node名称和验证者节点地址
            region_name = Tx.Query.query_staking_list_region()  # 获取区信息，包含区对应的验证者地址和区名称
            v_dict = {v.get("operator_address"): v.get("description").get("moniker") for v in
                      node_name.get("validators")}
            r_dict = {r.get("operator_address"): r.get('name') for r in region_name.get("region")}
            # print(v_dict)
            # print(r_dict)
            # 用普通方式写
            node_region = {}
            for key, value in v_dict.items():
                if key in r_dict:
                    node_region[value] = r_dict[key]

            # 用推导式写：
            new_node_region = {v_dict[key]: r_dict[key] for key in v_dict if key in r_dict}
            # print(new_node_region)
            return node_region

        # TODO 计算块高
        @staticmethod
        def count_height():
            pass

    class Wait(object):
        @staticmethod
        def wait_five_seconds():
            for i in range(6):
                print(i)
                i += 1
                time.sleep(1)


if __name__ == '__main__':
    # username = "nokycwangzhibiao003"
    # username = "test001"  # cosmos1cjsvfrth4ygc0hqdw9y7hnpwgzdt5mh6vv2lqj
    # username = "test002" # cosmos1lkaqrt9s6glk6lcgk9tt0dnc9a9gmxqlq56pyv
    # username = "wangzhibiao001"

    # username="wangzhibiao001"
    # username = "wangzhibiao001"
    # username = "superadmin"
    # yue = "1999900"
    # node_name = "node2"
    # region_name = "USA"
    # adderss = "cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77"
    print("======" * 5, "初始化起始线", "======" * 5)
    # print(Tx.Staking.creation_validator_region_many())
    # print(Tx.Query.node_name_zip_region_name())
    # print(Tx.Keys.add(username=username))                         # 添加用戶
    # Tx.SendToAdmin.count_down_5s()
    #
    # print(Tx.Bank.send_to_admin(amout=100)) # 国库转钱给管理员
    Tx.Wait.wait_five_seconds()
    # time.sleep(2)

    # Tx.SendToAdmin.send_admin_to_user(to_account=username, amounts=10001, fees=100) # 管理员给用户转账
    # Tx.SendToAdmin.count_down_5s()
    # time.sleep(1)
    # print(f"{username}该用户余额为:",Tx.Query.query_bank_balance_username(username=username))   # 查询该用户余额
    # print(f"{username}该用户地址为:", Tx.Keys.private_export_meuser(username=username))  # 查询用户address
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

    # print(Tx.Staking.deposit_fixed(amount=10, months=3, username=username))  # 发起定期委托
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
    # 提交一下
    print("======" * 5, "最后结束线", "======" * 5)
