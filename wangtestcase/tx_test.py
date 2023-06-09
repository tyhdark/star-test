# -*- coding:utf-8 -*-
import threading
from x.tx import Tx
import time
ttx = Tx()
# username = "nokycwangzhibiao003"
# username = "test001"  # cosmos1cjsvfrth4ygc0hqdw9y7hnpwgzdt5mh6vv2lqj
# username = "test002" # cosmos1lkaqrt9s6glk6lcgk9tt0dnc9a9gmxqlq56pyv
# username = "wangzhibiao001"

username1 = "wangzhibiao002"
username = "testnamekycNZL004"
# username = "testnamekyc001"
# username = "superadmin"
yue = "1999900"
node_name = "node3"
region_name = "NZL"
# adderss = "cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77"
print("======" * 5, "初始化起始线", "======" * 5)
# print(Tx.Keys.add(username=username))                         # 添加用戶
# Tx.SendToAdmin.count_down_5s()
Tx.SendToAdmin.send_to_treasury_fees(amount=1 ,fees=100)   # 管理员转账给国库
# Tx.SendToAdmin.count_down_5s()
# Tx.SendToAdmin.send_to_admin_fees(amount=100000, fees=100) # 国库转给管理员
# Tx.SendToAdmin.count_down_5s()
# time.sleep(2)
# print("查询管理员余额：",Tx.Query.query_bank_balance_username("superadmin")) # 查询管理员余额
#
# f1 = threading.Thread(target=Tx.SendToAdmin.send_to_treasury_fees,args=(10000,100)) # 管理员转账给国库
# f2 = threading.Thread(target=Tx.SendToAdmin.tx_bank_send,args=(username,username1,0.1,100)) # 用户给用户转账
# f1.start()
# f2.start()
# Tx.SendToAdmin.send_admin_to_user(to_account=username1, amounts=100000, fees=100) # 管理员给用户转账
# Tx.SendToAdmin.count_down_5s()
# time.sleep(1)
# print(f"{username}该用户余额为:",Tx.Query.query_bank_balance_username(username=username))   # 查询该用户余额
# print(f"{username}该用户地址为:",Tx.Keys.private_export_meuser(username=username))       # 查询用户address
Tx.SendToAdmin.tx_bank_send(from_address_name=username,to_address_name=username1,amounts=0.1,fees=10) # 用户给用户转账
# Tx.SendToAdmin.count_down_5s()
# time.sleep(2)
# print(f"{username}该用户余额为:", Tx.Query.query_bank_balance_username(username=username))  # 查询该用户余额
# Tx.Staking.new_kyc_for_username(user_name=username, region_name=region_name)  # NEW KYC
# Tx.SendToAdmin.count_down_5s()
# Tx.Staking.delegate(amount=1, username=username1, fees=100)                               # 发起质押
# Tx.SendToAdmin.count_down_5s()
# print(type(Tx.Staking.delegate_unkycunbond_height(amount=1000000, username=username, fees=100))) # 非KYC用户赎回质押
# Tx.Staking.delegate_kycunbond_txhash(amount=1000,username=username,fees=100)                  #  KYC用户赎回质押
# Tx.SendToAdmin.count_down_5s()
# print(f"{username}该用户活期委托本金为:", Tx.Query.query_staking_delegate(username=username))  # 查询质押
# print(f"{username}该用户活期委托实时收益为:",Tx.Query.query_distribution_rewards_form_name(username=username))  # 查询用户活期委托所产生的利息
# print(Tx.Staking.distribution_withdraw_rewards(username=username, fees=100))                              # 用户提取自己的活期收益，不分KYC
# print(Tx.Query.query_staking_delegate_start_height(username=username))
# Tx.SendToAdmin.count_down_5s()
# print(f"{username}该用户提取收益后的余额为:",Tx.Query.query_bank_balance_username(username=username)) # 查询该用户余额
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

# Tx.Staking.creation_validator_node(node_name=node_name,amounts=40000000)   # 创建验证者节点
# time.sleep(2)
# Tx.SendToAdmin.count_down_5s()
# Tx.Staking.new_region(region_name=region_name, node_name=node_name)   # 创建区
# Tx.SendToAdmin.count_down_5s()
# time.sleep(2)
# print("查询节点列表")
# dict1 = Tx.Query.query_staking_validator_list()          # 查询节点列表
# print(dict1)
# node_name_list = [ i.get('description').get('moniker') for i in (dict1.get('validators')) ] # 推导式方式写
# print(node_name_list)


# print(type(list))
# print("查询区列表")
# a = Tx.Query.query_staking_list_region()        # 查询区列表
# print(a)
# n_list = []
# r_list = a.get('region')
# for i in r_list:
#     n_list.append(i.get('name'))
# print(n_list)
# region_name_list = [i.get('name') for i in (a.get('region'))]
# print("推导式结果为",region_name_list)
# print(Tx.Keys.add(username=username))       # 添加用戶
# Tx.SendToAdmin.count_down_5s()

# print(Tx.Keys.show_address_for_username(username=username))  # 通过用户名称查询用户地址
# Tx.SendToAdmin.count_down_5s()
# Tx.Staking.new_kyc_for_username(user_name=username,region_name=region_name) #NEW KYC

# Tx.SendToAdmin.count_down_5s()                # 暂停5秒
# print(kyc_list)
# print(Tx.Staking.deposit_fixed(amount=88,months=1,username=username))  #发起定期委托
# Tx.Staking.withdraw_fixed(fixed_id=5,username=username,fees=100)      # 根据ID赎回定期委托
# print(Tx.Staking.deposit_fixed(amount=10,months=12,username=username))  #发起定期委托
# Tx.SendToAdmin.count_down_5s()
# ding = Tx.Query.query_list_fixed_deposit()                # 查询所有定期委托列表
# print("所有定期委托",ding)
# print(type(ding))
# for i in ding:
#     print(i)
# Tx.Query.query_staking_validator_list()
# Tx.Query.query_staking_list_region()                   #  查询区列表
# Tx.Staking.validator_node_stake_increase(node_name=node_name, amount=100)  # 增加节点对应的staking值
# Tx.SendToAdmin.count_down_5s()
# time.sleep(2)
# Tx.Staking.validator_node_stake_unstake(node_name=node_name,amount=100)  # 减少节点对应的staking值
# Tx.SendToAdmin.count_down_5s()
# time.sleep(2)
# Tx.Staking.edit_validator_owner_address(node_name=node_name,to_username=username1,fees=100)  # 修改验证者节点的归属者
# print(Tx.Query.query_staking_validator_from_node_name(node_name=node_name))
# hash_v = "ED2771E9A15F7325806E4907B7E13207E2B672DD85F0498C4800CC1F51AE2FB0"  # 查询对应的hash值
# hash_dict = Tx.Query.query_tx_hash(hash_value=hash_v)
# print(hash_dict)
# for key,value in hash_dict.items():
#     print(key,value)
# print(Tx.Query.query_tx_hash(hash_value=hash_v))

# keys_list = Tx.Keys.lists()  # 查询用户列表
# for i in keys_list:  # 查询用户列表
#     print("用户列表：",i)  # 查询用户列表
#
# piv = Tx.Keys.private_export(username=username)  # 导出用户私钥
# print("用户的私钥为",piv)

# print("KYC用戶列表如下：")
# time.sleep(1)
# kyc_list = Tx.Query.query_staking_list_kyc()      # 查询KYC列表
# print("KYC用户列表为：",[i.get('account') for i in kyc_list.get('kyc')])
# print("KYC用户地址列表：",kyc_list)
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
#
print("======" * 5, "最后结束线", "======" * 5)
