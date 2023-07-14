# -*- coding: utf-8 -*-
'''
遇到问题没人解答？小编创建了一个Python学习交流QQ群：778463939
寻找有志同道合的小伙伴，互帮互助,群里还有不错的视频学习教程和PDF电子书！
'''
class TestYield:
    def gen_iterator(self):
        for j in range(3):
            print(f"do_something-{j}")
            # yield在for循环内部
            yield j

    def call_gen_iterator(self):
        # yield并不是直接返回[0,1,2]，执行下边这句后result_list什么值都没有
        result_list = self.gen_iterator()
        # i每请求一个数据，才会触发gen_iterator生成一个数据
        for i in result_list:
            print(f"call_gen_iterator-{i}")
name = "CHNHIASHKS"

if __name__ == "__main__":
    obj = TestYield()
    obj.call_gen_iterator()
    print(name.lower())