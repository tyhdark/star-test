# -*- coding: utf-8 -*-
from x.tx import Tx
import time
# ttx = Tx()

vaildators_list = {'pagination': {'next_key': None, 'total': '0'}, 'validators': [{'commission': {
    'commission_rates': {'max_change_rate': '0.010000000000000000', 'max_rate': '0.200000000000000000',
                         'rate': '0.100000000000000000'}, 'update_time': '2023-06-08T08:29:55.088841032Z'},
    'consensus_pubkey': {
        '@type': '/cosmos.crypto.ed25519.PubKey',
        'key': '8G/kXX0Xy9nTRIaY6RPFeKQNeg+uyZM3f7isXu7kRrE='},
    'delegation_amount': '80000000',
    'description': {'details': '',
                    'identity': '',
                    'moniker': 'node1',
                    'security_contact': '',
                    'website': ''},
    'jailed': False,
    'kyc_amount': '1000000',
    'min_self_stake': '1000000',
    'operator_address': 'mevaloper1z820hara5yqa82zs8kuxjgysze3gkk6mkqe7gd',
    'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
    'staker_shares': '50000000000000.000000000000000000',
    'status': 'BOND_STATUS_BONDED',
    'tokens': '50000000000000',
    'unbonding_height': '0',
    'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-09T02:01:02.107509952Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': 'cno9qY6PwcTecLbbsScMmNgDg7MPbn8bg8Kg0onlKi4='},
        'delegation_amount': '0',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node5',
                        'security_contact': '',
                        'website': ''},
        'jailed': False, 'kyc_amount': '0',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper1rsyss639d4aqjuuf9unjear0j6p06rjz4kgler',
        'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
        'staker_shares': '40000000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '40000000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-20T03:01:00.367551718Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': 'y7TJ9BQphDgSbgyTQGOD/BQIzZ1Vl+vUTj4H5eQGptE='},
        'delegation_amount': '0',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node8',
                        'security_contact': '',
                        'website': ''},
        'jailed': False,
        'kyc_amount': '1000000',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper1fd8fn2d56m3d6dwf5s7j7zgtert0rssng5u3e4',
        'owner_address': 'me1ncrfmwd5tunaxdn9ktq75ruw9hwz04s9jyaehl',
        'staker_shares': '40000000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '40000000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-09T01:54:46.725259154Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': '6j6RSPmJFwv2Uhgkt+1DcC2m3vVOT+JZnS+2st7Fzog='},
        'delegation_amount': '0',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node4',
                        'security_contact': '',
                        'website': ''},
        'jailed': False, 'kyc_amount': '0',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper1tn7vup0a6ma6x7tggkkalw6pc6x3ets9eg4ejv',
        'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
        'staker_shares': '40000000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '40000000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-09T02:02:19.231816761Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': 'u9TGxWN11JMo0vA3yQb3SNrGDEQgEdcqH3W2pAACJBY='},
        'delegation_amount': '0',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node6',
                        'security_contact': '',
                        'website': ''},
        'jailed': False, 'kyc_amount': '0',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper10g230d2vux9je4080eggk80spn44wkg9m73nlv',
        'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
        'staker_shares': '30000000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '30000000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-09T01:51:23.637880740Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': 'ztipTDS9sLEsMj5z5InavTssM/BKhMErFKvrBlUKusM='},
        'delegation_amount': '262165467',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node3',
                        'security_contact': '',
                        'website': ''},
        'jailed': False,
        'kyc_amount': '2000000',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper10ugvk0vp8evnrtn9suaugvte8z4lcvgmgvlf62',
        'owner_address': 'me137w03a2k3z7e9yrxjpgqlygyyx27ep8t2drwqc',
        'staker_shares': '59800000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '59800000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-13T07:54:19.542400681Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': 'V3wlPErR7NL82yd/qmDZmEy7pheBGTUC22+R1bMktfw='},
        'delegation_amount': '1870005221',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node7',
                        'security_contact': '',
                        'website': ''},
        'jailed': False,
        'kyc_amount': '5000000',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper1seq5nwcscr9ugwpfyvfgc35ryk9wjpey04nkrk',
        'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
        'staker_shares': '40000000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '40000000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-20T07:08:48.524312213Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': 'DVc7AA17Vy+ed50JHLn0x9coVrCFZZiNCreDMqni0dY='},
        'delegation_amount': '0',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node9',
                        'security_contact': '',
                        'website': ''},
        'jailed': False, 'kyc_amount': '0',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper1kwtll6uzugd48aku78607rul5jkvvtsjaqjmcl',
        'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
        'staker_shares': '40000000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '40000000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'},
    {'commission': {'commission_rates': {
        'max_change_rate': '0.010000000000000000',
        'max_rate': '0.200000000000000000',
        'rate': '0.100000000000000000'},
        'update_time': '2023-06-08T08:36:18.707310130Z'},
        'consensus_pubkey': {
            '@type': '/cosmos.crypto.ed25519.PubKey',
            'key': '0sZDTf3yHD1eMvj+cqe3jssr+EvCjedu3SLgI+Lr97I='},
        'delegation_amount': '0',
        'description': {'details': '',
                        'identity': '',
                        'moniker': 'node2',
                        'security_contact': '',
                        'website': ''},
        'jailed': False,
        'kyc_amount': '2000000',
        'min_self_stake': '1000000',
        'operator_address': 'mevaloper1kl7ya94cqyzt0ppj5qtk6gxl8rqv3qctgftyfc',
        'owner_address': 'me12s4ddtmz406qrfxax27kpvk7hxu94agk8yqq4e',
        'staker_shares': '50010000000000.000000000000000000',
        'status': 'BOND_STATUS_BONDED',
        'tokens': '50010000000000',
        'unbonding_height': '0',
        'unbonding_time': '1970-01-01T00:00:00Z'}]}

regin_list = {'pagination': {'next_key': None, 'total': '0'}, 'region': [
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'CHN', 'nft_class_id': 'CHN-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1z820hara5yqa82zs8kuxjgysze3gkk6mkqe7gd', 'regionId': 'CHNid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'FLK', 'nft_class_id': 'FLK-NFT-CLASS-ID-',
     'operator_address': 'mevaloper10g230d2vux9je4080eggk80spn44wkg9m73nlv', 'regionId': 'FLKid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'HKG', 'nft_class_id': 'HKG-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1kwtll6uzugd48aku78607rul5jkvvtsjaqjmcl', 'regionId': 'HKGid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'ISL', 'nft_class_id': 'ISL-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1tn7vup0a6ma6x7tggkkalw6pc6x3ets9eg4ejv', 'regionId': 'ISLid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'LBY', 'nft_class_id': 'LBY-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1seq5nwcscr9ugwpfyvfgc35ryk9wjpey04nkrk', 'regionId': 'LBYid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'NFK', 'nft_class_id': 'NFK-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1rsyss639d4aqjuuf9unjear0j6p06rjz4kgler', 'regionId': 'NFKid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'NZL', 'nft_class_id': 'NZL-NFT-CLASS-ID-',
     'operator_address': 'mevaloper10ugvk0vp8evnrtn9suaugvte8z4lcvgmgvlf62', 'regionId': 'NZLid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'TWN', 'nft_class_id': 'TWN-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1fd8fn2d56m3d6dwf5s7j7zgtert0rssng5u3e4', 'regionId': 'TWNid'},
    {'creator': 'me1lc53tgwulx9dgd8zsgv0zu8zdwkyk7gg3mtdmz', 'name': 'USA', 'nft_class_id': 'USA-NFT-CLASS-ID-',
     'operator_address': 'mevaloper1kl7ya94cqyzt0ppj5qtk6gxl8rqv3qctgftyfc', 'regionId': 'USAid'}]}

regin_node_name = {'mevaloper1z820hara5yqa82zs8kuxjgysze3gkk6mkqe7gd': 'node1',
                   'mevaloper1rsyss639d4aqjuuf9unjear0j6p06rjz4kgler': 'node5',
                   'mevaloper1fd8fn2d56m3d6dwf5s7j7zgtert0rssng5u3e4': 'node8',
                   'mevaloper1tn7vup0a6ma6x7tggkkalw6pc6x3ets9eg4ejv': 'node4',
                   'mevaloper10g230d2vux9je4080eggk80spn44wkg9m73nlv': 'node6',
                   'mevaloper10ugvk0vp8evnrtn9suaugvte8z4lcvgmgvlf62': 'node3',
                   'mevaloper1seq5nwcscr9ugwpfyvfgc35ryk9wjpey04nkrk': 'node7',
                   'mevaloper1kwtll6uzugd48aku78607rul5jkvvtsjaqjmcl': 'node9',
                   'mevaloper1kl7ya94cqyzt0ppj5qtk6gxl8rqv3qctgftyfc': 'node2'}

regin_list_name = {'mevaloper1z820hara5yqa82zs8kuxjgysze3gkk6mkqe7gd': 'CHN',
                   'mevaloper10g230d2vux9je4080eggk80spn44wkg9m73nlv': 'FLK',
                   'mevaloper1kwtll6uzugd48aku78607rul5jkvvtsjaqjmcl': 'HKG',
                   'mevaloper1tn7vup0a6ma6x7tggkkalw6pc6x3ets9eg4ejv': 'ISL',
                   'mevaloper1seq5nwcscr9ugwpfyvfgc35ryk9wjpey04nkrk': 'LBY',
                   'mevaloper1rsyss639d4aqjuuf9unjear0j6p06rjz4kgler': 'NFK',
                   'mevaloper10ugvk0vp8evnrtn9suaugvte8z4lcvgmgvlf62': 'NZL',
                   'mevaloper1fd8fn2d56m3d6dwf5s7j7zgtert0rssng5u3e4': 'TWN',
                   'mevaloper1kl7ya94cqyzt0ppj5qtk6gxl8rqv3qctgftyfc': 'USA'}


# new = {"node1": "CHN", "node2": "USA", "node3": "NZL", "node4": "ISL", "node5": "NFK", "node6": "FLK", "node7": "LBY",
#        "node8": "TWN", "node9": "HKG"}

# new = dict(zip(regin_node_name.values(), regin_list_name.values()))
# print(new)
# dict1 = {"A":"aaa","B":"bbb","C":"ccc"}

# print("查询节点列表推导式结果为：",[ i.get('description').get('moniker') for i in (vaildators_list.get('validators')) ] )# 推导式方式写)
# print("查询区列表推导式结果为",[i.get('name') for i in (regin_list.get('region'))])
# oa = "mevaloper1fd8fn2d56m3d6dwf5s7j7zgtert0rssng5u3e4"
# for i in regin_list.get("region"):
#     dict_none = {}
#     dict_none[i.get("operator_address")]=i.get("name")
#     print(dict_none)

# print(i.get("operator_address"))
# print(i.get("name"))

# if i.get("operator_address")==oa:
#      print(i.get("name"))

r_l = Tx.Query.query_staking_list_region()
print("区列表：",r_l)
v_l = Tx.Query.query_staking_validator()
print("节点列表：",v_l)
def vail():
    v_dict = {}
    for v in vaildators_list.get('validators'):
        # v_dict = {}
        a = 0
        if a <= len(vaildators_list.get('validators')):
            v_dict[v.get('operator_address')] = v.get('description').get('moniker')
            a += 1
        # else:
        #     print("结束了")
        # print(v_dict)
    return v_dict

def region():
    r_dict = {}
    for r in regin_list.get('region'):
        b = 0
        if b <= len(regin_list.get('region')):
            r_dict[r.get('operator_address')] = r.get('name')
            b += 1

    return r_dict

v_dict = {v.get('operator_address'):v.get('description').get('moniker') for v in vaildators_list.get('validators')}
r_dict = {r.get('operator_address'): r.get('name') for r in regin_list.get('region')}
new2 = dict(zip(v_dict.values(), r_dict.values()))
print(new2)

# r_dict = {r.get('operator_address'): r.get('name') for r in r_l.get('region')}
# v_dict = {v.get('operator_address'):v.get('description').get('moniker') for v in v_l.get('validators')}
# v_dict = {r.get('operator_address'): r.get('description').get('moniker') for r in vaildators_list.get('description').get('moniker')}
# print("区列表用推导式写：",r_dict)
# print("验证者列表用推导式写：",v_dict)

# new2 = dict(zip(v_dict.values(), r_dict.values()))
# print(new2)

# def
# print(vail())
# print(region())
# new_dict = {}

# if __name__ == '__main__':
# print(vail())

# print(v.get('operator_address'))
# print(v.get('description').get('moniker'))
# print(v.get())
# if v.get('operator_address') ==oa:
# print(v.get('description').get('moniker'))


# listA = ["A","B","C","D"]
# listB = ["a","b","c","d"]
# 把这两个列表转化成字典
# dictionary = dict(zip(listA, listB))
# print(dictionary)
