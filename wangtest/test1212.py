dict1 = {'balances': [{'amount': '10999999900', 'denom': 'umec'}], 'pagination': {'next_key': None, 'total': '0'}}
dict2 = {'balances': [], 'pagination': {'next_key': None, 'total': '0'}}
list2 = dict1.get('balances')[0]
amount= list2.get('amount')
int1 = int(amount)
print(int1)
print(type(int1))
a = int(dict1.get('balances')[0].get('amount'))

print(a)
print(type(a))
# a = int(dict2.get('balances')[0].get('amount'))
#
# print(a)
# print(type(a))
if dict2.get('balances')==None:
    print("kong")
else:
    print("2")
    int(dict_resp_info.get('balances')[0].get('amount'))