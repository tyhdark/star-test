import math

dicta = {'balance': {'amount': '9028000000', 'denom': 'umec'},
         'delegation': {'amount': '0', 'delegator_address': 'cosmos1fap8hp3t3xt20qw4sczlyrk6n92uffj4r4kw77',
                        'shares': '0.000000000000000000', 'startHeight': '1501', 'unKycAmount': '9028000000',
                        'unmovable': '0',
                        'validator_address': 'cosmosvaloper1vdhhxmt0wvchg7t8d4enx7rgdpenx7tkxsurwurg0qekgae5vyun26nwxa6rwmrsd56rwvrj5synkq'}}

a = int(dicta.get("delegation").get('startHeight'))
# print(a)
# print(type(a))

b = math.ceil(((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))
print(b)
c=100/(200*10**8) *(10**6)
print(c)