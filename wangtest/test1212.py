# -*- coding:utf-8 -*-
import threading
import time


def music(data):
    print("bengin listen music: {}".format(time.ctime()))
    # time.sleep(1)
    print(str(data))
    print("music end: {}".format(time.ctime()))


def movie(data):
    print("bengin look movie: {}".format(time.ctime()))
    # time.sleep(3)
    print(str(data))
    print("movie end: {}".format(time.ctime()))

def fun1():

    print("1")
    time.sleep(1)
    print(time.ctime())

def fun2():

    print("2")
    time.sleep(1)
    print(time.ctime())

f1 = threading.Thread(target=fun1)
f2 = threading.Thread(target=fun2)
f1.start()
f2.start()
# th1 = threading.Thread(target=music, args=("love.mp3",))  ##创建线程
# th1.start()  ##启动线程
# th2 = threading.Thread(target=movie, args=("Anit.avi",))
# th2.start()

