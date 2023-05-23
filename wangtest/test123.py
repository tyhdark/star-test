return1 = {'pagination': {'next_key': None, 'total': '0'},
           'validators':
               [{
                   'commission': {
                            'commission_rates': {'max_change_rate': '0.010000000000000000', 'max_rate': '0.200000000000000000',
                         'rate': '0.100000000000000000'}, 'update_time': '2023-05-19T08:53:00.851211301Z'},

                    'consensus_pubkey': {
                                            '@type': '/cosmos.crypto.ed25519.PubKey',
                                            'key': 'JOT+HgxKEVmZgS0OVFVTmCbeVIoaClOQycIuXvGtmis='},
                    'delegation_amount': '2000000',
                    'description': {'details': '', 'identity': '',
                                    'moniker': 'node6',
                                    'security_contact': '',
                                    'website': ''},
                    'jailed': False, 'kyc_amount': '6000000',
                    'min_self_stake': '1000000',
                    'operator_address': 'cosmosvaloper1q6jh4rz6a8hxv5k3npverf5qq2ketnnaw5ydl3',
                    'owner_address': 'cosmos1q2vemelem20p86855v490hj4dz464vlsrp3xg9',
                    'staker_shares': '1000000000.000000000000000000',
                    'status': 'BOND_STATUS_BONDED',
                    'tokens': '1000000000',
                    'unbonding_height': '0',
                    'unbonding_time': '1970-01-01T00:00:00Z'},
                   {'commission': {'commission_rates': {
                                'max_change_rate': '0.010000000000000000',
                                'max_rate': '0.200000000000000000',
                                'rate': '0.100000000000000000'},
                                'update_time': '2023-05-22T03:38:22.457685401Z'},
                            'consensus_pubkey': {
                                '@type': '/cosmos.crypto.ed25519.PubKey',
                                'key': 'r0IyS5AsoHZyXCRnwTIcUMfaHvYNMrUXfIpbXVQNwe8='},
                            'delegation_amount': '0',
                            'description': {'details': '',
                                            'identity': '',
                                            'moniker': 'node2',
                                            'security_contact': '',
                                            'website': ''},
                            'jailed': False, 'kyc_amount': '0',
                            'min_self_stake': '1000000',
                            'operator_address': 'cosmosvaloper18v7mx03atm3pdqzua63pqylcd8duydk8enp045',
                            'owner_address': 'cosmos1q2vemelem20p86855v490hj4dz464vlsrp3xg9',
                            'staker_shares': '100000000.000000000000000000',
                            'status': 'BOND_STATUS_BONDED',
                            'tokens': '100000000',
                            'unbonding_height': '0',
                            'unbonding_time': '1970-01-01T00:00:00Z'},
                   {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-05-19T08:43:07.131138868Z'},
    'consensus_pubkey': {
        '@type': '/cosmos.crypto.ed25519.PubKey',
        'key': 'sA2Ly9Gzg/tptezSqhx3wGMWdPsN1HVDXUOfpRp1dS0='},
    'delegation_amount': '0',
    'description': {'details': '',
                    'identity': '',
                    'moniker': 'node1',
                    'security_contact': '',
                    'website': ''},
    'jailed': False, 'kyc_amount': '0',
    'min_self_stake': '1000000',
    'operator_address': 'cosmosvaloper1devfaq59f5av2g5czm2d2yg4exshfns6j78cuc',
    'owner_address': 'cosmos1q2vemelem20p86855v490hj4dz464vlsrp3xg9',
    'staker_shares': '1000001000000.000000000000000000',
    'status': 'BOND_STATUS_BONDED',
    'tokens': '1000001000000',
    'unbonding_height': '0',
    'unbonding_time': '1970-01-01T00:00:00Z'}]}

moniker_to_find = 'node2'
operator_address = None
for validator in return1['validators']:
    if validator['description']['moniker'] == moniker_to_find:
        operator_address = validator['operator_address']
        break

print(operator_address)

# value1 = dict1["validators"][0]["operator_address"]

# python中根据员工姓名为laowang7取出其对应的地址的值
# my_dic2t = {"a1": {'kk1': {'kkkk1': 'vvvvv2'}, '地址': '江西省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang2'}},
#             "a2": {'kk1': {'kkkk1': 'vvvvv6'}, '地址': '广西省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang6'}},
#             "a3": {'kk1': {'kkkk1': 'vvvvv7'}, '地址': '广东省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang7'}},
#             "a4": {'kk1': {'kkkk1': 'vvvvv3'}, '地址': '湖北省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang3'}},
#             "a5": {'kk1': {'kkkk1': 'vvvvv5'}, '地址': '四川省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang5'}},
#             "a6": {'k1': {'kkk1': 'vvv2'}, '地址': '湖南省', 'k3': {'k4': 'v4', '员工姓名': 'laowang2'}},
#             "a7": {'kk1': {'kkkk1': 'vvvvv2'}, '地址': '青海省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang1'}}}

# value_to_find = "laowang7"
#
# matching_keys = [k for k, v in my_dict.items() if v.get('laowang7') == value_to_find]
#
# print(matching_keys)  # 输出 ['key1', 'key3']

a = "这个dict2是某一个查询用户信息的接口的返回值，" \
    "为了方便取值，我已经将这个接口的返回值转化成dict了，" \
    "可是每一次查询接口的时候，这个接口的返回值的都会变化，因为不可能永远只有这个7个员工是把？，肯定会有增有减的，，" \
    "可是不管员工怎么变化，我每次都想拿到员工姓名为langwang7的地址，" \
    "因为我每次都要那这个laowang7的地址出来作为下一个函数的入参"


# my_dict2 = {
#     'key1': {
#         'name': 'Alice',
#         'age': 25
#     },
#     'key2': {
#         'name': 'Bob',
#         'age': 30
#     },
#     'key3': {
#         'name': 'Charlie',
#         'age': 25
#     }
# }

# value_to_find = 25

# matching_keys = [k for k, v in my_dict2.items() if v.get('age') == value_to_find]

# print(matching_keys)  # 输出 ['key1', 'key3']
def find_top_key(d, value_to_find):
    for k, v in d.items():
        if isinstance(v, dict):
            result = find_top_key(v, value_to_find)
            if result:
                return result
        elif v == value_to_find:
            return k


def find_key(d, value_find):
    for key, values in d.items():
        if isinstance(values, dict):
            r = find_key(values, value_find)
            if r:
                return r
        elif values == value_find:
            return key


my_dict = {
    'key1': {
        'name': 'Alice',
        'age': 25,
        'details': {
            'address': '123 Main St',
            'phone': '555-1234'
        }
    },
    'key2': {
        'name': 'Bob',
        'age': 30,
        'details': {
            'address': '456 Oak St',
            'phone': '555-5678'
        }
    },
    'key3': {
        'name': 'Charlie',
        'age': 25,
        'details': {
            'address': '789 Elm St',
            'phone': '555-9012'
        }
    }
}
my_dict.get("")
value_to_find = '555-1234'

top_key = find_key(my_dict, value_to_find)
# print(top_key)

# if __name__ == '__main__':
#     my_dict = {
#         'key1': {
#             'name': 'Alice',
#             'age': 25,
#             'details': {
#                 'address': '123 Main St',
#                 'phone': '555-1234'
#             }
#         },
#         'key2': {
#             'name': 'Bob',
#             'age': 30,
#             'details': {
#                 'address': '456 Oak St',
#                 'phone': '555-5678'
#             }
#         },
#         'key3': {
#             'name': 'Charlie',
#             'age': 25,
#             'details': {
#                 'address': '789 Elm St',
#                 'phone': '555-9012'
#             }
#         }
#     }
#     my_dic2 = {"a1": {'kk1': {'kkkk1': 'vvvvv2'}, '地址': '江西省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang2'}},
#                 "a2": {'kk1': {'kkkk1': 'vvvvv6'}, '地址': '广西省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang6'}},
#                 "a3": {'kk1': {'kkkk1': 'vvvvv7'}, '地址': '广东省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang7'}},
#                 "a4": {'kk1': {'kkkk1': 'vvvvv3'}, '地址': '湖北省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang3'}},
#                 "a5": {'kk1': {'kkkk1': 'vvvvv5'}, '地址': '四川省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang5'}},
#                 "a6": {'k1': {'kkk1': 'vvv2'}, '地址': '湖南省', 'k3': {'k4': 'v4', '员工姓名': 'laowang2'}},
#                 "a7": {'kk1': {'kkkk1': 'vvvvv2'}, '地址': '青海省', 'kk3': {'kk4': 'vv4', '员工姓名': 'laowang1'}}}
#     value_to_find = 'laowang7'
#     matching_keys = find_keys(my_dic2, value_to_find)
#
#     print(matching_keys)  # 输出 ['key1']
