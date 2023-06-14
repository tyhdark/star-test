list1 = [1,2,3]
list2 = [1,2,3,4]
# print(type(len(list1)))
# for list2 in list1:
#     if list2 not in list1:
#         print(list2)
list3 = set(list2) -set(list1)
print(list(list3))
