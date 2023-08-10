# -*- coding: utf-8 -*-
from decimal import Decimal

# from numpy import matrix

# new_list = [i for i in range(5) if i>1]
# print(new_list)
# new_list2 = [(x+1,y+1) for x in range(3) for y in range(4)]
# print(new_list2)
# flattened = []
# for row in :
#     for n in row:
#         flattened.append(n)

# flattened = [n for row in matrix for n in row]
# print(flattened)
# b = 0.0000001*1000000
# print(b)
# a = Decimal('0.0000001') * Decimal('1000000')
# print(type(a))
a="%0.001f"%(0.0000001*1000000)
print(a)
# print(float(a))