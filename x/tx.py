# -*- coding: utf-8 -*-
import inspect
import random
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
            cmd = Tx.work_home + f"{Tx.chain_bin} tx bank send {from_addr} {to_addr} {amount}{Tx.coin['c']} --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y -b=block"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def send_to_admin(amount: int, fees=Fees):
            """国库往超管转钱，不需要传参,传金额就行，保留"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx bank sendToAdmin {amount}{Tx.coin['c']} --from={Tx.super_addr} --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y -b=block"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

    class Staking(object):

        @staticmethod
        def create_region(region_name, node_name, fees=Fees):
            """
            创建一个区
            :param from_addr: 发起方地址 需要区域管理员
            :param region_name: 区名称
            :param node_name: 节点名称，方便找节点地址
            :param fees: Gas费用
            :param gas: 默认为 200000
            :return:
            """
            params_a = "region_id, total_as, fee_rate, totalStakeAllow, userMaxDelegateAC,userMinDelegateAC, delegators_limit=-1,  gas=GasLimit,"
            # c = "./me-chaind tx staking new-region  CHN  #验证者节点地址  --from=#超管地址  --keyring-backend=test --chain-id=me-chain --fees=0.00mec "
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking new-region {region_name} " \
                                 f"$(./me-chaind q staking validators | grep -w \"{node_name}\" -A 6 | awk '/address/{{print$2}}')" \
                                 f" --from={Tx.super_addr} --fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y -b=block"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def create_validator(node_name: str, amount=None, fees=Fees, ):
            """创建验证者节点，需要传入对应的node几,可用，"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking create-validator  --amount={amount}{Tx.coin['c']}  " \
                                 f"--pubkey=$({Tx.chain_bin} tendermint show-validator --home=../nodes/{node_name})  " \
                                 f"--moniker=\"{node_name}\" " \
                                 f" --commission-rate=\"0.10\" --commission-max-rate=\"0.20\"  " \
                                 f" --commission-max-change-rate=\"0.01\" --from={Tx.super_addr}  " \
                                 f"--fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def validator_stake_unstake(operator_address=None, stake_or_unstake=None, amount=None, fees=Fees):
            """
            修改区信息
            :param operator_address: 节点地址
            :param stake_or_unstake: 传入stake就是增加，untake减少
            :param amount: 金额
            :return:
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking {stake_or_unstake} {operator_address} {amount}{Tx.coin['c']}" \
                                 f" --from={Tx.super_addr} --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def edit_validator(operator_address, owner_address, fees=Fees, ):
            """
            Only used to modify the Region ID of the verifier 把节点售卖给别人
            :param operator_address: Validator address
            :param owner_address: 卖给谁
            :param fees: fees
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking edit-validator {operator_address} " \
                                 f"--owner-address={owner_address} --from={Tx.super_addr} --fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def delegate(from_addr, amount, fees=Fees):
            """创建/追加 活期质押
            :param from_addr: 用户地址
            :param amount: 金额
            :return 交易结果，含哈希，记得提取"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking delegate {amount}{Tx.coin['c']} --from={from_addr} " \
                                 f"--fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y -b=block"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def undelegate_nokyc(from_addr, amount, fees=Fees):
            """
            非KYC减少活期质押可用:
            1.减少质押金额 >= 实际质押额 则按实际质押额兑付 并主动发放收益
            2.减少质押金额 < 实际质押额 则按传入金额兑付, 收益重新计算但不主动发放
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking unKycUnbond {amount}{Tx.coin['c']} --from={from_addr} " \
                                 f" --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def undelegate_kyc(from_addr, amount, fees=Fees):
            """
            KYC减少活期质押有用:
            1.减少质押金额 >= 实际质押额 则按实际质押额兑付 并主动发放收益
            2.减少质押金额 < 实际质押额 则按传入金额兑付, 收益重新计算但不主动发放
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking unbond {amount}{Tx.coin['c']} --from={from_addr} " \
                                 f" --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def deposit_fixed(from_addr, amount, month=None, fees=Fees):
            """创建定期质押
            :param from_addr: 用户地址
            :param amount: 金额
            :param month: 月数，1、3、6、12、24、36、48 如果不填就会随机选一个
            """
            if month is None:
                mon = random.choice([1, 3, 6, 12, 24, 36, 48])
            else:
                mon = month
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking deposit-fixed {amount}{Tx.coin['c']} Term_{mon}_Months " \
                                 f"--from={from_addr}  --fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def withdraw_fixed(from_addr, fixed_delegation_id, fees=Fees):
            """提取定期质押 可用"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking withdraw-fixed {fixed_delegation_id} --from={from_addr}  " \
                                 f"--fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def withdraw_rewards(from_addr, fees=Fees):
            """用户提取活期收益，不区分KYC用户"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx distribution withdraw-rewards --from={from_addr} --fees={fees}{Tx.coin['uc']}  {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def set_fixed_deposit_interest_rate(term, rate, fees=Fees):
            """更改定期委托的费率
            :param term: 定期枚举值
            :param rate: 定期费率
            :param fees:
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking set-fixed-deposit-interest-rate {term} {rate}  " \
                                 f"--from={Tx.super_addr} --fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def new_kyc( region_id,user_addr, fees=Fees):
            """
            把用户认证成KYC
            :param user_addr: kyc address
            :param region_id: 所绑定区域ID
            :param from_addr: 发起地址 区管理员 or 全局管理员
            :param fees: Gas费用 {Tx.coin['c']}
            :return: tx Hash
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx staking new-kyc {user_addr} {region_id} --from={Tx.super_addr} " \
                                 f"--fees={fees}{Tx.coin['uc']} {Tx.chain_id} {Tx.keyring_backend} -y -b=block"

            # if from_addr != Tx.super_addr:  # 区管理员 不能创建 KYC_ROlE_ADMIN
            #     assert role == config["chain"]["role"]["user"]
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)


    class Group(object):
        @staticmethod
        def create_group(admin_addr, fees=Fees):
            """
            创建群，
            """
            cmd = Tx.work_home + f"{Tx.chain_bin} tx group create-group {admin_addr} --from {Tx.super_addr}  --fees={fees}{Tx.coin['uc']} {Tx.keyring_backend} {Tx.chain_id} -y "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def update_group_member(user_addr, group_id, fees=Fees):
            """新增群成员"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx group update-group-member {user_addr} {group_id} --from {Tx.super_addr}  --fees={fees}{Tx.coin['uc']} {Tx.keyring_backend} {Tx.chain_id} -y -b=block"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def leove_group(user_addr, group_id, fees=Fees):
            """退出群"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx group leave-group {user_addr} {group_id} --from {Tx.super_addr}  --fees={fees}{Tx.coin['uc']} {Tx.keyring_backend} {Tx.chain_id} -y "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

        @staticmethod
        def detele_group(group_id, fees=Fees):
            """解散该群"""
            cmd = Tx.work_home + f"{Tx.chain_bin} tx group delete-group {group_id} --from {Tx.super_addr}  --fees={fees}{Tx.coin['uc']} {Tx.keyring_backend} {Tx.chain_id} -y "
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return Tx._executor(cmd)

    class Keys(object):

        @staticmethod
        def add(username):
            """添加用户 重名也会新增,地址不一样"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys add {username} {Tx.keyring_backend} && echo 'pass'"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")

            print(Tx.channel.send_ready())
            Tx.channel.send('echo "pass111" \n')

            print(Tx.channel.recv_ready())
            print(Tx.channel.recv(1024 * 5))

            print("----------------")

            Tx.channel.send(cmd + "\n")
            time.sleep(3)
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
            """导出私钥 有用"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys export {username} --unsafe --unarmored-hex {Tx.keyring_backend}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(1)
            resp_info = Interaction.ready(Tx.channel)
            if "private key will be exported" in resp_info:
                resp_info = Interaction.yes_or_no(Tx.channel)

            return Result.split_esc(resp_info)

        @staticmethod
        def delete(user_name=None):
            """根据用户名称在本地删除用户，保留"""
            cmd = Tx.work_home + f"{Tx.chain_bin} keys delete {user_name} {Tx.keyring_backend} -y"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            Tx.channel.send(cmd + "\n")
            time.sleep(1)
            resp_info = Interaction.ready(Tx.channel)

            if "Error" in resp_info:
                return "key not found"
            else:
                return resp_info

            # assert "**Important**" in resp_info

    class Wait(object):
        @staticmethod
        def wait_five_seconds():
            """等待5秒"""
            for i in range(6):
                print(i)
                i += 1
                time.sleep(1)

        @staticmethod
        def wati_five_height():
            """等待5个块高"""
            for i in range(26):
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
    # print(Tx.Bank.send_to_admin(amount=100)) # 国库转钱给管理员
    # Tx.Wait.wait_five_seconds()
    # time.sleep(2)
    print(Tx.Keys.delete(user_name="usersdHwy"))

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
