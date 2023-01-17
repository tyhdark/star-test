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
from data import test_data
from srstaking.delegate import Delegate
from srstaking.region import Region
from srvault.fixed_deposit import Deposit
from srvault.kyc import KYC
from tools.calculate import wait_block_height
from tx.tx import Tx
from user.keys import User

logger.remove()
handler_id = logger.add(sys.stdout, level="INFO")
# logger.add("logs/case_{time}.log", rotation="500MB", level="DEBUG")
logger.add("logs-RT4/case_{time}.log", rotation="500MB", level="DEBUG")

super_admin_addr = "sil1jmmxpun4s3nd93fznc49dt3hwfdqawhl226fuq"

user = User()
kyc = KYC()
region = Region()
bank = Bank()
deposit = Deposit()
delegate = Delegate()
tx = Tx()


def test_create_region():
    _region_id, region_name = test_data.create_region_id_and_name()
    user_name = test_data.random_username()

    user_info = user.keys_add(user_name)
    time.sleep(1)
    logger.info(f"新增用户信息: {user_info}")
    _region_admin_addr = user_info[0][0]['address']

    balances_info = bank.query_balances(_region_admin_addr)
    logger.info(f"账户余额信息: {balances_info}")

    # 认证kyc 为区管理员
    kyc_info = kyc.new_kyc(addr=_region_admin_addr, region_id=_region_id, role="KYC_ROLE_ADMIN",
                           delegate_limit=200, from_addr=super_admin_addr, fees=1)
    logger.info(f"认证kyc 为管理员信息: {kyc_info}")
    tx_hash = kyc_info['txhash']
    time.sleep(5)
    tx_resp = tx.query_tx(tx_hash)

    assert tx_resp['code'] == 0

    time.sleep(5)
    # 使用SuperAdmin给区管理转账 100src
    send_tx_info = bank.send_tx(from_addr=super_admin_addr, to_addr=_region_admin_addr, amount=100, fees=1.01,
                                from_super=True)
    logger.info(f"转账信息: {send_tx_info}")
    tx_resp = tx.query_tx(send_tx_info['txhash'])
    time.sleep(4)
    assert tx_resp['code'] == 0

    # 创建区域  占比1%
    time.sleep(4)
    region_info = region.create_region(region_name=region_name, region_id=_region_id, power_limit=2000000,
                                       delegators_limit=200, fee_rate=0.5, from_addr=_region_admin_addr,
                                       stake_up=2000000,
                                       fees=1)
    logger.info(f"创建区信息: {region_info}")

    tx_resp = tx.query_tx(region_info['txhash'])
    time.sleep(4)
    assert tx_resp['code'] == 0
    logger.info(f"区管理员地址: {_region_admin_addr}, 区ID: {_region_id}")
    return _region_admin_addr, _region_id


def test_add_region_kyc(region_id, region_admin_addr):
    user_name = test_data.random_username()
    user_info = user.keys_add(user_name)
    region_user_addr = user_info[0][0]['address']

    kyc_info = kyc.new_kyc(addr=region_user_addr, region_id=region_id, role="KYC_ROLE_USER",
                           delegate_limit=200000, from_addr=region_admin_addr, fees=1, from_super=False)
    logger.info(f"{region_id} 认证kyc: {kyc_info}")
    resp = tx.query_tx(kyc_info['txhash'])
    time.sleep(4)
    assert resp['code'] == 0
    return region_user_addr


def super_admin_tx_user(region_user_addr):
    time.sleep(5)
    # 使用SuperAdmin给区kyc用户转账1000
    send_tx_info = bank.send_tx(from_addr=super_admin_addr, to_addr=region_user_addr, amount=1000, fees=1.1,
                                from_super=True)
    logger.info(f"转账信息: {send_tx_info}")
    time.sleep(2)
    resp = tx.query_tx(send_tx_info['txhash'])
    assert resp['code'] == 0


def main():
    region_admin_addr, region_id = test_create_region()
    wait_block_height()  # 区金库没钱时 不能认证kyc
    region_user_addr = test_add_region_kyc(region_id, region_admin_addr)
    super_admin_tx_user(region_user_addr)
    del_info = delegate.create_delegate(region_user_addr, 10, region_id, 1)
    resp = tx.query_tx(del_info['txhash'])
    assert resp['code'] == 0


if __name__ == '__main__':
    # region_admin_addr, region_id = test_create_region()
    # print(f"region_admin_addr:{region_admin_addr}, region_id:{region_id}")
    # sil12l3ggfca85my22pfwgg4el2dueyd09fcedkwp4 ,  800b481c8b2c11eda4711e620a42e34a
    # 查询区管理员地址余额  还剩下99 即创建区的手续费都由区管理员所支付了，未按照比例设置的比例收取，在未设置区成功时，不知道手续费怎么收取

    # region_user_addr = test_add_region_kyc("b481c8b2c11eda4711e620a42e34a",
    #                                        "sil12l3ggfca85my22pfwgg4el2dueyd09fcedkwp4")
    # print(region_user_addr)  # sil1qy8pccn4as872ea84hu0xkch5hwnqf3yl2dr3x

    # super_admin_tx_user("sil1qy8pccn4as872ea84hu0xkch5hwnqf3yl2dr3x")

    # kyc用户有钱了，导出私钥
    # 0x411edebd082e0d2f43dc942d8b2b3bb499673ea48060172c26bfaa9ffec92223

    # res = delegate.create_delegate("sil1qy8pccn4as872ea84hu0xkch5hwnqf3yl2dr3x", 100,
    #                                "800b481c8b2c11eda4711e620a42e34a", 1)
    # print(res)

    main()
    # kyc_user02_addr = test_add_region_kyc(region_id='73685ac68b4c11ed99e21e620a42e34a', region_admin_addr='sil1c0t54fz5m5yc3jqrr7xvy6yeec70tgk6crs2pj')
    # print(kyc_user02_addr)

    # ye
    # user01 = test_add_region_kyc("2cfb26828d6c11ed8f731e620a42e34a", "sil1z7nmtdl8m8r08gwajldd80cclrw6fwa5m7eas0")
    # user02 = test_add_region_kyc("2cfb26828d6c11ed8f731e620a42e34a", "sil1z7nmtdl8m8r08gwajldd80cclrw6fwa5m7eas0")
    # print(f"user01:{user01}, user02:{user02}")

    # tx
    # super_admin_tx_user("sil1pkgz44we9w8qqk0gewxvnt3xphp7dwn7phgerj")
    # super_admin_tx_user("sil1p03sewpcpay27gvmzzze46rtm7c76dd7v2dhz9")

    # Jw
    # user01 = test_add_region_kyc("82a844aa961011ed8a681e620a42e349", "sil1wqa9t5ncphs9ynhu46c7nvqfuc06elz3wtymez")
    # super_admin_tx_user(user01)
    # logger.info(f"jw_kyc_user: {user01}")
    # pass
