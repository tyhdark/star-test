# -*- coding:utf-8 -*-
list1 = []
print(len(list1))
list2 = [{"a":1},{"b":2}]
print(len(list2))
list3= [{'id': '4', 'account': 'me139gejytfffu40lqmds75743fuzktp0uy9d39h4', 'principal': {'denom': 'umec', 'amount': '80000000'}, 'interest': {'denom': 'umec', 'amount': '6000000'}, 'start_time': '2023-07-24T03:40:54.512062743Z', 'end_time': '2023-07-24T03:46:54.512062743Z', 'term': 'TERM_6_MONTHS', 'rate': '0.150000000000000000'}, {'id': '5', 'account': 'me139gejytfffu40lqmds75743fuzktp0uy9d39h4', 'principal': {'denom': 'umec', 'amount': '1000000'}, 'interest': {'denom': 'umec', 'amount': '75000'}, 'start_time': '2023-07-24T03:53:49.740413304Z', 'end_time': '2023-07-24T03:59:49.740413304Z', 'term': 'TERM_6_MONTHS', 'rate': '0.150000000000000000'}]
print(len(list3))
list4 = [{'account': 'me139gejytfffu40lqmds75743fuzktp0uy9d39h4', 'end_time': '2023-07-24T03:46:54.512062743Z', 'id': '4', 'interest': {'amount': '6000000', 'denom': 'umec'}, 'principal': {'amount': '80000000', 'denom': 'umec'}, 'rate': '0.150000000000000000', 'start_time': '2023-07-24T03:40:54.512062743Z', 'term': 'TERM_6_MONTHS'}, {'account': 'me139gejytfffu40lqmds75743fuzktp0uy9d39h4', 'end_time': '2023-07-24T03:59:49.740413304Z', 'id': '5', 'interest': {'amount': '75000', 'denom': 'umec'}, 'principal': {'amount': '1000000', 'denom': 'umec'}, 'rate': '0.150000000000000000', 'start_time': '2023-07-24T03:53:49.740413304Z', 'term': 'TERM_6_MONTHS'}]
print(len(list4))
for i in list4:
    print(i['account'])
b = [i['account'] for i in list4]
print(b)