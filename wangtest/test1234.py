r = {'k1': {'kk1': 1, 'kk2': '0'}, 'validators': [
    {'commission': {'commission_rates': '1'}, 'description': {'details': '', 'identity': '',
                                                              'moniker': 'node6',
                                                              'security_contact': '',
                                                              'website': ''},
     'address': "cosmosvaloper1q6jh4rz6a8hxv5k3npverf5qq2ketnnaw5ydl3"},
    {'commission': {'commission_rates': '1'}, 'description': {'details': '', 'identity': '',
                                                              'moniker': 'node2',
                                                              'security_contact': '',
                                                              'website': ''},
     'address': "cosmosvaloper18v7mx03atm3pdqzua63pqylcd8duydk8enp045"},
    {'commission': {'commission_rates': '1'}, 'description': {'details': '', 'identity': '',
                                                              'moniker': 'node1',
                                                              'security_contact': '',
                                                              'website': ''},
     'address': "cosmosvaloper1devfaq59f5av2g5czm2d2yg4exshfns6j78cuc"}]}

moniker_to_find = 'node6'
address = None

for validator in r['validators']:
    if validator['description']['moniker'] == moniker_to_find:
        address = validator['address']
        break

print(address)  # 输出 "cosmosvaloper1q6jh4rz6a8hxv5k3npverf5qq2ketnnaw5ydl3"
