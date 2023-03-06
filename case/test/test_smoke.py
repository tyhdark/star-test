"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 13:39
@Version :  V1.0
@Desc    :  None
"""
import sys
import time
import uuid

from loguru import logger

from x.bank import Bank
from x.region import Region
from x.fixed_deposit import Deposit
from x.kyc import KYC
from x.keys import User

logger.remove()
handler_id = logger.add(sys.stdout, level="INFO")
logger.add("logs/case_{time}.log", rotation="500MB", level="DEBUG")

super_admin_addr = "sil17xneh8t87qy0z0z4kfx3ukjppqrnwpazwg83dc"

user = User()
kyc = KYC()
region = Region()
bank = Bank()
deposit = Deposit()


def test_create_region():
    region_id = uuid.uuid1().hex
    region_name = f"test-{region_id}"

    # 添加用户
    user_name = "user-" + region_id
    user_info = user.keys_add(user_name)
    logger.info(f"新增用户信息: {user_info}")
    region_admin_addr = user_info[0][0]['address']

    balances_info = bank.query_balances(region_admin_addr)
    logger.info(f"账户余额信息: {balances_info}")

    # 认证kyc 为区管理员
    kyc_info = kyc.new_kyc(addr=region_admin_addr, region_id=region_id, role="KYC_ROLE_ADMIN",
                           delegate_limit=200, from_addr=super_admin_addr, fees=1)
    logger.info(f"认证kyc 为管理员信息: {kyc_info}")

    time.sleep(5)
    # 使用SuperAdmin给区管理转账
    send_tx_info = bank.send_tx(from_addr=super_admin_addr, to_addr=region_admin_addr, amount=100, fees=1.01,
                                from_super=True)
    logger.info(f"转账信息: {send_tx_info}")

    # 创建区域
    time.sleep(5)
    region_info = region.create_region(region_name=region_name, region_id=region_id, power_limit=1000000,
                                       delegators_limit=200, fee_rate=0.5, from_addr=region_admin_addr,
                                       stake_up=1000000,
                                       fees=1)
    logger.info(f"创建区信息: {region_info}")
    return region_admin_addr, region_id


def test_do_fixed_deposit(region_admin_addr, region_id):
    user_name = "user-" + uuid.uuid1().hex
    user_info = user.keys_add(user_name)
    logger.info(f"新增用户信息: {user_info}")
    region_user_addr = user_info[0][0]['address']

    # 认证kyc
    kyc_info = kyc.new_kyc(addr=region_user_addr, region_id=region_id, role="KYC_ROLE_USER",
                           delegate_limit=200000, from_addr=region_admin_addr, fees=1, from_super=False)
    logger.info(f"{region_id} 认证kyc: {kyc_info}")

    time.sleep(5)
    # 使用SuperAdmin给区kyc用户转账
    send_tx_info = bank.send_tx(from_addr=super_admin_addr, to_addr=region_user_addr, amount=1000, fees=1.1,
                                from_super=True)
    logger.info(f"转账信息: {send_tx_info}")

    # 区内kyc 发起定期存款
    time.sleep(5)
    res = deposit.do_fixed_deposit(amount=100, period="PERIOD_3_MONTHS", from_addr=region_user_addr, fees=1)
    print(res)


if __name__ == '__main__':
    # region_admin_addr, region_id = test_create_region()
    # print(f"region_admin_addr:{region_admin_addr}, region_id:{region_id}")
    region_admin_addr = "sil10s67dqj0ad6crd3vqz49zql4d7px9drc5m3jmc"
    region_id = "22398b92882311edaebd1e620a42e34a"
    test_do_fixed_deposit(region_admin_addr, region_id)
    region_user_addr = "sil1h82xmex6lhk6e802a0vs6re7rwc0mvey64aykj"


    # user_balance = 1087099740000
    #
    # 发送至 区管理员 = 10150130000
    # 发送1src   fees: 100020000
    #
    # 期望： user_balance:    1086899720000
    # 区管理： 10300140000
    #
    # 带备注发送1src  fees: 100020000
    # 期望： user_balance:    1086699700000
    # 区管理： 10450150000


