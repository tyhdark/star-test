# -*- coding:utf-8 -*-

import time
region_name=["CHN","USA","JPN","NZL","TWN","HKG","ZAF","ARG","RUS","CAN","ATA","WSM","ISL"]
# for r in region_name:
#     print(r)
# print(len(region_name))
# node_name = [region_name(1,14)]
# def node():
#     node_name=""
#
#     for i in range(1,11):
#         a = 0
#         if i<12:
#             node_name = f"node{i}"
#             a +=1
#     # print(f"node{i}")
#     # print(node_name)
#     return node_name
node = [i for i in range(1,14)]
# print(region_name)
# print(node)
region_node = dict(zip(region_name,node))
# print(region_node)
for k,v in region_node.items():
    print(k,v)
    time.sleep(2)
class Tes:
    # def __init__(self,node):
    #     self.name ="a"
    #     self.node = node
    @staticmethod
    def tes():
        a = 0
        for a in node:
            print(f"node{a}")
            time.sleep(1)
            a +=1
        # print(f"名字是：{node}")
        # pass
# print(dict(zip(region_name(),)))
# Tes.tes()