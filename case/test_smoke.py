"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 13:39
@Version :  V1.0
@Desc    :  None
"""
import sys
import time

from loguru import logger

from bank.bank import Bank
from srstaking.region import Region
from srvault.kyc import KYC
from user.keys import User

logger.remove()
handler_id = logger.add(sys.stdout, level="INFO")
logger.add("logs/case_{time}.log", rotation="500MB", level="DEBUG")

super_admin_addr = "sil17xneh8t87qy0z0z4kfx3ukjppqrnwpazwg83dc"


def test_create_region():
    user = User()
    kyc = KYC()
    region = Region()
    bank = Bank()

    region_id = 9876543
    region_name = "beijing-05"

    # 添加用户
    user_info = user.keys_add("wang55")
    logger.info(f"新增用户信息: {user_info}")
    user_addr = user_info[0][0]['address']

    balances_info = bank.query_balances(user_addr)
    logger.info(f"账户余额信息: {balances_info}")

    # 认证kyc 为区管理员
    kyc_info = kyc.new_kyc(addr=user_addr, region_id=region_id, role="KYC_ROLE_ADMIN",
                           delegate_limit=200, from_addr=super_admin_addr, fees=1)
    logger.info(f"认证kyc 为管理员信息: {kyc_info}")

    time.sleep(3)
    # 使用SuperAdmin给区管理转账
    send_tx_info = bank.send_tx(from_addr=super_admin_addr, to_addr=user_addr, amount=100, fees=1.01, from_super=True)
    logger.info(f"转账信息: {send_tx_info}")

    # 创建区域
    time.sleep(3)
    region_info = region.create_region(region_name=region_name, region_id=region_id, power_limit=100000,
                                       delegators_limit=200, fee_rate=0.5, from_addr=user_addr, stake_up=100000,
                                       fees=1)
    logger.info(f"创建区信息: {region_info}")
    pass


if __name__ == '__main__':
    test_create_region()
