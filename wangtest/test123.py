# a = "你说："
# print(a)
# b = "你说:\"你好\""
# print(b)
dict1 = {'pagination': {'next_key': None, 'total': '0'}, 'validators': [{'commission': {
    'commission_rates': {'max_change_rate': '0.010000000000000000', 'max_rate': '0.200000000000000000',
                         'rate': '0.100000000000000000'}, 'update_time': '2023-05-19T03:41:24.747675453Z'},
                                                                 'consensus_pubkey': {
                                                                     '@type': '/cosmos.crypto.ed25519.PubKey',
                                                                     'key': 'uucMrFFhJXOmzurP6vkgHzO/MPwXyDxNMPx8XjcI+Ik='},
                                                                 'delegation_amount': '0',
                                                                 'description': {'details': '', 'identity': '',
                                                                                 'moniker': 'node8',
                                                                                 'security_contact': '', 'website': ''},
                                                                 'jailed': False, 'kyc_amount': '0',
                                                                 'min_self_stake': '1000000',
                                                                 'operator_address': 'cosmosvaloper1pw0n0w7c206mm7wrvem0hw036rgg6x540kj8y3',
                                                                 'owner_address': 'cosmos1w22wvw2lljf4kan2s5qfvg4gm70qg6w2dwrs6t',
                                                                 'staker_shares': '100000000.000000000000000000',
                                                                 'status': 'BOND_STATUS_BONDED', 'tokens': '100000000',
                                                                 'unbonding_height': '0',
                                                                 'unbonding_time': '1970-01-01T00:00:00Z'}, {
                                                                    'commission': {'commission_rates': {
                                                                        'max_change_rate': '0.010000000000000000',
                                                                        'max_rate': '0.200000000000000000',
                                                                        'rate': '0.100000000000000000'},
                                                                                   'update_time': '2023-05-19T03:42:54.837731517Z'},
                                                                    'consensus_pubkey': {
                                                                        '@type': '/cosmos.crypto.ed25519.PubKey',
                                                                        'key': 'q4KdRyc9Y+z2sQn8Z8NETA0aPhsgDefYPr9/jYmudiU='},
                                                                    'delegation_amount': '0',
                                                                    'description': {'details': '', 'identity': '',
                                                                                    'moniker': 'node14',
                                                                                    'security_contact': '',
                                                                                    'website': ''}, 'jailed': False,
                                                                    'kyc_amount': '0', 'min_self_stake': '1000000',
                                                                    'operator_address': 'cosmosvaloper1tzuwxj07qmz5ywr84v86ah62qta3sv9e794p2p',
                                                                    'owner_address': 'cosmos1w22wvw2lljf4kan2s5qfvg4gm70qg6w2dwrs6t',
                                                                    'staker_shares': '1000000000.000000000000000000',
                                                                    'status': 'BOND_STATUS_BONDED',
                                                                    'tokens': '1000000000', 'unbonding_height': '0',
                                                                    'unbonding_time': '1970-01-01T00:00:00Z'}, {
                                                                    'commission': {'commission_rates': {
                                                                        'max_change_rate': '0.010000000000000000',
                                                                        'max_rate': '0.200000000000000000',
                                                                        'rate': '0.100000000000000000'},
                                                                                   'update_time': '2023-05-19T01:36:04.541328767Z'},
                                                                    'consensus_pubkey': {
                                                                        '@type': '/cosmos.crypto.ed25519.PubKey',
                                                                        'key': 'h2UGe3Zl+jmNxPWzvtjCIBppT6PRVrgZIxRS/4cdC3o='},
                                                                    'delegation_amount': '0',
                                                                    'description': {'details': '', 'identity': '',
                                                                                    'moniker': 'node1',
                                                                                    'security_contact': '',
                                                                                    'website': ''}, 'jailed': False,
                                                                    'kyc_amount': '0', 'min_self_stake': '1000000',
                                                                    'operator_address': 'cosmosvaloper1utc9zvnp9fetdmqwsyvkjtcs9kanqaarq3zs6d',
                                                                    'owner_address': 'cosmos1w22wvw2lljf4kan2s5qfvg4gm70qg6w2dwrs6t',
                                                                    'staker_shares': '1000000000000.000000000000000000',
                                                                    'status': 'BOND_STATUS_BONDED',
                                                                    'tokens': '1000000000000', 'unbonding_height': '0',
                                                                    'unbonding_time': '1970-01-01T00:00:00Z'}]}



value1 = dict1["validators"][0]["operator_address"]
print(value1)
print(type(value1))
