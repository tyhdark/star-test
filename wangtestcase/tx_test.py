# -*- coding:utf-8 -*-
import os
import sys
import threading
# from x.tx import Tx
from x.tx import Tx
from x.query import Query, HttpQuery
import time
from multiprocessing import Process
from decimal import Decimal

dirname1 = sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

path3 = os.path.dirname(os.path.dirname(__file__))
tx = Tx()
query = Query()
# namea = {'names': ['userGSMUI241', 'userONdlhXf9', 'userZobRav1e', 'userb4DUfrX2', 'useroCu43Vyq', 'useruU5PRT30']}
# for i in namea['names']:
#     tx.Keys.delete(user_name=i)
#     time.sleep(1)
# print(path3)
# p = Process()
# username = "nokycwangzhibiao003"
# username = "test001"  # cosmos1cjsvfrth4ygc0hqdw9y7hnpwgzdt5mh6vv2lqj
# username = "test002" # cosmos1lkaqrt9s6glk6lcgk9tt0dnc9a9gmxqlq56pyv
# username = "wangzhibiao001"
# node_name = "node1"
# region_name = "CHN"
# node_name = "node2"
# region_name = "USA"
node_name = "node1"
region_name = "CHN"
# node_name = "node4"
# region_name = "NZL"
# node_name = "node5"
# region_name = "MAC"
# node_name = "node6"
# region_name = "TWN"
# node_name = "node7"
# region_name = "HKG"
# username1 = "wangzhibiao003"

# username = "userDaniel"
# username = "testnamekyc001"
username = "test_bank"
# username = "superadmin"
# addre = "me1ex3k095qcl2acc02zjj5kczu42j6yxhqjf4rwk"
# name = Query.Key.name_of_addre(addr="me17fkfasmd7rj94r06rcqae4gxp9zpw0qz68pp0u")
# print("用户的名字为：",name)
addre = Query.Key.address_of_name(username=username)
print(addre)
# Tx.Bank.send_tx(from_addr=addre,to_addr="me12437lurmk23cl0a6wvyp7tukjpt6x3jcr5v9jn",amount=100)
# print("用户的地址为：",addre)
# print(f"superadmin地址为：{query.Key.address_of_name(username='superadmin')}")
# print(Query.super_addr)

# adderss = "cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77"
# def one1(name):
#     addr = query.Key.address_of_name(username=name)
#     return addr
# def two2(name):
#     addr = query.Key.address_of_name(username=name)
#     return addr
print("======" * 5, "初始化起始线", "========" * 5)
# tx.Keys.add(username="testname003")
#
# treasury_addr = Query.Account.auth_account(pool_name="treasury_pool")
# treasury_balance_start = HttpQuery.Bank.query_balances(addr=treasury_addr)
# print("国库余额", treasury_balance_start)
# print(Tx.Keys.add(username=username))                   # 添加用戶
# Tx.Wait.wait_five_seconds()
# print(Tx.Bank.send_to_admin(amount=2917149)) # 国库转账给管理员37348154444253
# Tx.Wait.wait_five_seconds()
print("查询管理员余额：", HttpQuery.Bank.query_balances(addr=Query.super_addr))  # 查询管理员余额
# print("superadmin余额",Query.Bank.query_balances(addr=Query.super_addr))
# print( "查询管理员余额：",Query.Bank.query_balances(addr=Query.super_addr))
# print(Tx.Bank.send_tx(from_addr=Tx.super_addr,to_addr=addre,amount=5447548)) # 管理员给用户转钱
# Tx.Wait.wait_five_seconds()
#
# node='localhost:14007'
# res=Tx.Bank.send_tx(from_addr=addre,to_addr="me1m78psak70p4xtywcxfm25nclx6fnezw3lxzzy6",amount=20,fees=200,node="localhost:26657") # 用户给用户地址转钱
# print(res)
# print(f"{username}该用户余额为:",Query.Bank.query_balances(addr=addre))  # 查询该用户余额
#
# Tx.Staking.new_kyc(user_addr="me1jzd5acys9m0um9susxt2u00cyt8gqygfga0eyc",region_id="bhs")  # new kyc 认证KYC
# Tx.Staking.delegate(amount=400, from_addr="me1w5xhsf98c9z0uaghcxuhh3auz07yclvam5wq09")                               # 发起质押 不区分KYC
# Tx.Wait.wait_five_seconds()
# print(type(Tx.Staking.undelegate_nokyc(from_addr="me1ex3k095qcl2acc02zjj5kczu42j6yxhqjf4rwk",amount=35)))         # 非KYC用户赎回质押
# Tx.Staking.undelegate_kyc()                                                 #  KYC用户赎回质押

# print(f"{username}该用户活期委托本金为:", HttpQuery.Staking.delegation(addr="me12437lurmk23cl0a6wvyp7tukjpt6x3jcr5v9jn"))  # 查询质押
# print(f"{username}该用户活期委托实时收益为:",Tx.Query.query_distribution_rewards_form_addr(addr=addre))  # 查询用户活期委托所产生的利息
# print(Tx.Staking.withdraw_rewards(addr=addre))                              # 用户提取自己的活期收益，不分KYC

# print(Tx.Staking.undelegate_kyc(from_addr=addre,amount=100000))   # KYC赎回质押

# print("======" * 5, "委托起始线", "======" * 5)

# print(Tx.Staking.create_validator(node_name=node_name, amount=50000000)) # 创建验证者节点
# Tx.Wait.wait_five_seconds()

# print(Tx.Staking.create_region(region_name=region_name, node_name=node_name)) # 创建区
# Tx.Wait.wait_five_seconds()
# time.sleep(2)
# print("查询节点列表")
dict1 = HttpQuery.Staking.validator()  # 查询节点列表
# print(Query.Bank.query_balances(addr=addre))
# print(dict1)
for v in dict1:
    print(v)
# print("查询节点node列表推导式结果为：",[ i.get('description').get('moniker') for i in dict1 ] )# 推导式方式写)

# print("查询区列表")
region_list = Query.Staking.list_region()  # 查询区列表
for region in region_list:
    print(region)
print(region_list)
# node1 = "bhs"
# node2 = "nic"
# node7 = "ita"
# print("查询区名称列表推导式结果为",[i.get('name') for i in (region_list.get('region'))])

# print(Tx.Staking.deposit_fixed(from_addr=addre,amount=1,month=6))     #发起定期委托
# Tx.Staking.withdraw_fixed(from_addr=addre,fixed_delegation_id=0)      # 根据ID赎回定期委托
# user_fixed = HttpQuery.Staking.fixed_deposit(addr="me1tyzme6d7c62zjk0gta5cdn9aedxp0x33ymffmc")               # 查询个人或者全网所有的定期列表
# print(user_fixed)
# print (f"定期委托的id列表为：{[f.get('id') for f in user_fixed][0]}")
# 增加或减少节点对应的staking值
# Tx.Staking.validator_stake_unstake(operator_address="mevaloper1hmrk36p0mcjqlsmklw37qkj3jvpys8e03vlkuk",stakeorunstake="unstake",amount=200)


# Tx.Staking.edit_validator(operator_address="",owner_address="") # 修改验证者节点的归属者
# result=Tx.Staking.validator_stake_unstake(operator_address='mevaloper1d3x9vtq55mz5c440lc53eu4te4jtyhg28vqe2p',stake_or_unstake="stake",amount="850000000")
# print(result)
#
# keys_list = Query.Key.keys_list()  # 查询用户列表
# for i in keys_list:  # 查询用户列表
#     print("用户列表：",i)  # 查询用户列表
# print(f"用户的名称组合的列表为：{[n.get('name') for n in keys_list]}")
#
# piv = Tx.Keys.private_export(username="superadmin")  # 导出用户私钥
# piv=Tx.Keys.private_export(username="tyh_node5_test1")
#
# a = HttpQuery.Bank.query_balances(addr="me15njp78gwj3dh8dfrzp64ukglqdzmqygchlsh6k")
# print("a=",a)
# for i in Query.Staking.list_kyc().get("kyc"):
#     print("KYC用戶如下：",i)
# print("KYC用户地址列表为：",[i.get('account') for i in HttpQuery.Staking.kyc().get('kyc')])


# result = Query.Key.keys_list()
# print(f"result={result}")
# i = 0
# for entry in result:
#     name = entry.get('name')
#
#     if name and len(name) == 12 and name.startswith('user'):
#         print('name=', name)
#         Tx.Keys.delete(user_name=name)
#         i += 1
#         print(f"删除第{i}个")

# r2=HttpQuery.Staking.kyc(addr="me1rmhnq4uwpgcq52kpg76up65ndgh43nc9q7dxt2")['kyc']['regionId']
# print(r2)
# r=HttpQuery.Tx.query_tx(tx_hash="EB1132B8382B4FE61D7E92AD29D06AEB8F61E03AF6F307D14C31FE1DC9EE9DAC")
# print(r)
# r2=HttpQuery.Staking.fixed_deposit(addr="me149u2jq4smyh40v7qzdqvsqnlk9a8tderqxlcqr")
# r3 = max([i['id'] for i in r2])
# print(r2)
# print(r3)


# Tx.Bank.send_tx(from_addr=addre,to_addr="me149u2jq4smyh40v7qzdqvsqnlk9a8tderqxlcqr",amount=0.01)

# result1 = Tx.Staking.withdraw_rewards(from_addr="me1kpc32s5svs8hd5rpvgukd2jas7k8tzmyty6w08")
# print("hash=", result1['txhash'])
# result2 = HttpQuery.Tx.query_tx(tx_hash=result1['txhash'])
# result = Query.Account.aunt_account_addr(addr=addre)
# print(result['account_number'])
# print(result['sequence'])


print("======" * 10, "最后结束线", "======" * 10)
