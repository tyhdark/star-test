# -*- coding:utf-8 -*-
import threading
from x.tx import Tx
from x.query import Query,HttpQuery
import time
tx = Tx()
queru = Query()
# username = "nokycwangzhibiao003"
# username = "test001"  # cosmos1cjsvfrth4ygc0hqdw9y7hnpwgzdt5mh6vv2lqj
# username = "test002" # cosmos1lkaqrt9s6glk6lcgk9tt0dnc9a9gmxqlq56pyv
# username = "wangzhibiao001"
# node_name = "node1"
# region_name = "CHN"
# node_name = "node2"
# region_name = "USA"
node_name = "node3"
region_name = "JPN"
# node_name = "node4"
# region_name = "NZL"
# node_name = "node5"
# region_name = "MAC"
# node_name = "node6"
# region_name = "TWN"
# node_name = "node7"
# region_name = "HKG"
# username1 = "wangzhibiao003"

username = "userDaniel"
# username = "testnamekyc001"
# username = "testname011"
# username = "superadmin"
# addre = "me14ywd6peegppyk9jmjmzgytf9rx6p2lf77egqzr"
name = Query.Key.name_of_addre(addr="me17fkfasmd7rj94r06rcqae4gxp9zpw0qz68pp0u")
# print("用户的名字为：",name)
addre = Query.Key.address_of_name(username=username)

print("用户的地址为：",addre)
print(f"superadmin地址为：{Query.Key.address_of_name(username='superadmin')}")
print(Query.super_addr)




# adderss = "cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77"
print("======" * 5, "初始化起始线", "========" * 5)
# print(Tx.Keys.add(username=username))                         # 添加用戶
# Tx.Wait.wait_five_seconds()
# print(Tx.Bank.send_to_admin(amount=1000000)) # 国库转账给管理员
# Tx.Wait.wait_five_seconds()
print("查询管理员余额：",HttpQuery.Bank.query_balances(addr=Query.super_addr))  # 查询管理员余额

# print(Tx.Bank.send_tx(from_addr=Tx.super_addr,to_addr=addre,amount=10000)) # 管理员给用户转钱
# Tx.Wait.wait_five_seconds()
#
# Tx.Bank.send_tx() # 用户给用户地址转钱

print(f"{username}该用户余额为:",HttpQuery.Bank.query_balances(addr=addre))  # 查询该用户余额

# Tx.Staking.new_kyc(user_addr=addre,region_id="kor",from_addr=Tx.super_addr)  # new kyc 认证KYC
# Tx.Staking.delegate(amount=1000, from_addr=addre)                               # 发起质押 不区分KYC
# Tx.Wait.wait_five_seconds()
# print(type(Tx.Staking.undelegate_nokyc(from_addr=addre,amount=10000)))         # 非KYC用户赎回质押
# Tx.Staking.undelegate_kyc()                                                 #  KYC用户赎回质押

# print(f"{username}该用户活期委托本金为:", HttpQuery.Staking.delegation(addr=addre))  # 查询质押
# print(f"{username}该用户活期委托实时收益为:",Tx.Query.query_distribution_rewards_form_addr(addr=addre))  # 查询用户活期委托所产生的利息
# print(Tx.Staking.withdraw_rewards(addr=addre))                              # 用户提取自己的活期收益，不分KYC

# print(Tx.Staking.undelegate_kyc(from_addr=addre,amount=100000))   # KYC赎回质押

# print("======" * 5, "委托起始线", "======" * 5)

# print(Tx.Staking.create_validator(node_name=node_name, amount=50000000)) # 创建验证者节点
# Tx.Wait.wait_five_seconds()

# print(Tx.Staking.create_region(region_name=region_name, node_name=node_name, from_addr=Tx.super_addr)) # 创建区
# Tx.Wait.wait_five_seconds()
# time.sleep(2)
# print("查询节点列表")
# dict1 = HttpQuery.Staking.validator()   # 查询节点列表
# print(dict1)
# print("查询节点node列表推导式结果为：",[ i.get('description').get('moniker') for i in dict1 ] )# 推导式方式写)

# print("查询区列表")
# region_list = HttpQuery.Staking.region()      # 查询区列表
# print(region_list)
# print("查询区名称列表推导式结果为",[i.get('name') for i in (region_list.get('region'))])

print(Tx.Staking.deposit_fixed(from_addr=addre,amount=100,month=6))     #发起定期委托
# Tx.Staking.withdraw_fixed(from_addr=addre,fixed_delegation_id=0)      # 根据ID赎回定期委托
# user_fixed = HttpQuery.Staking.fixed_deposit()               # 查询个人或者全网所有的定期列表
# print (f"定期委托的id列表为：{[f.get('id') for f in user_fixed]}")
# 增加或减少节点对应的staking值
# Tx.Staking.validator_stake_unstake(operator_address="mevaloper1hmrk36p0mcjqlsmklw37qkj3jvpys8e03vlkuk",stakeorunstake="unstake",amount=200)


# Tx.Staking.edit_validator(operator_address="",owner_address="") # 修改验证者节点的归属者


#
keys_list = Query.Key.keys_list()  # 查询用户列表
# for i in keys_list:  # 查询用户列表
#     print("用户列表：",i)  # 查询用户列表
# print(f"用户的名称组合的列表为：{[n.get('name') for n in keys_list]}")
#
# piv = Tx.Keys.private_export(username=username)  # 导出用户私钥
#

# for i in Query.Staking.list_kyc().get("kyc"):
#     print("KYC用戶如下：",i)
print("KYC用户地址列表为：",[i.get('account') for i in HttpQuery.Staking.kyc().get('kyc')])


#


print("======" * 5, "最后结束线", "======" * 5)
