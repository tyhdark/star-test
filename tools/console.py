# -*- coding: utf-8 -*-
import time

import yaml
from loguru import logger


class Interaction:

    @staticmethod
    def input_password(channel):
        """输入密码"""
        resp = ""
        listen_info = 'Enter keyring passphrase:'

        while not resp.endswith(listen_info):
            stdout = channel.recv(1024 * 5)
            resp += stdout.decode('utf-8')

        channel.send("12345678" + "\n")

    @staticmethod
    def ready(channel):
        """
        读取数据并返回
            - channel.recv(1024*5)
        """
        resp2 = ""
        while True:
            time.sleep(1)
            if channel.recv_ready():
                stdout = channel.recv(1024 * 5)
                resp2 += stdout.decode('utf-8')
                if resp2 != "" and not resp2.isspace():
                    logger.debug(f"read console message: {resp2}")
                    break

        return resp2

    @staticmethod
    def yes_or_no(channel, boolean: bool = True):
        """
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
                stdout = channel.recv(1024 * 5)
                resp += stdout.decode('utf-8')
                resp = resp.lstrip("y")
                if resp is not None and not resp.isspace():
                    break
        return resp


class Result:

    @classmethod
    def split_esc(cls, data: str):
        """按esc切割数据"""
        data_info = data.split("")
        _value = data_info[0]
        return yaml.load(_value, Loader=yaml.FullLoader)

    @classmethod
    def yaml_to_dict(cls, yaml_path: str, is_file=False):
        """yaml数据/文件转dict"""
        if is_file:
            with open(yaml_path) as file:
                dict_value = yaml.load(file.read(), Loader=yaml.FullLoader)
        else:
            dict_value = yaml.load(yaml_path, Loader=yaml.FullLoader)
        return dict_value
