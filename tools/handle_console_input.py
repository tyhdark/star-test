"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 17:01
@Version :  V1.0
@Desc    :  None
"""
import time

from loguru import logger


def input_password(channel):
    """输入密码"""
    resp = ""
    listen_info = 'Enter keyring passphrase:'

    while not resp.endswith(listen_info):
        stdout = channel.recv(9999)
        resp += stdout.decode('utf-8')

    channel.send("12345678" + "\n")


def ready_info(channel):
    """
    #TODO 这是一个固定的值，若终端展示数据量过大，可能导致读取不完整
    读取数据并返回
        - channel.recv(9999)
    """
    resp2 = ""
    while True:
        if channel.recv_ready():
            stdout = channel.recv(9999)
            resp2 += stdout.decode('utf-8')
            if resp2 != "" and not resp2.isspace():
                logger.debug(f"console message: {resp2}")
                break

    return resp2


def yes_or_no(channel, boolean: bool = True):
    """
    #TODO 只对输入y的情况整理了数据，n的情况待处理
    :param channel:
    :param boolean:
    :return:
    """
    if boolean:
        channel.send("y" + "\n")
    else:
        channel.send("n" + "\n")
    resp = ""
    while True:
        time.sleep(0.5)
        if channel.recv_ready():
            stdout = channel.recv(9999)
            resp += stdout.decode('utf-8')
            resp = resp.lstrip("y")
            if resp is not None and not resp.isspace():
                logger.debug(f"console message: {resp}")
                break
    return resp
