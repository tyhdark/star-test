"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 16:35
@Version :  V1.0
@Desc    :  None
"""
import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_console_input, handle_resp_data


class User(BaseClass):

    def keys_add(self, username):
        """
        添加用户 重名也会新增,地址不一样
        :param username:
        :return:
        """
        cmd = self.ssh_home + f"./srs-poad keys add {username}"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_console_input.input_password(self.channel)
        time.sleep(1)
        resp_info = handle_console_input.ready_info(self.channel)

        if "existing" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        if "**Important**" in resp_info:
            return handle_resp_data.handle_add_user(resp_info)

    def keys_list(self):
        """查询用户列表 需要密码"""
        cmd = self.ssh_home + "./srs-poad keys list"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_console_input.input_password(self.channel)

        resp_info = handle_console_input.ready_info(self.channel)

        return handle_resp_data.handle_yaml_to_dict(resp_info)

    def keys_show(self, username):
        """
        查询用户信息
        :param username:
        :return:
        """
        cmd = self.ssh_home + f"./srs-poad keys show {username}"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        handle_console_input.input_password(self.channel)
        resp_info = handle_console_input.ready_info(self.channel)
        return handle_resp_data.handle_split_esc(resp_info)

    def keys_private_export(self, username):
        """
        导出私钥
        :param username:
        :return:
        """
        cmd = self.ssh_home + f"./srs-poad keys export {username} --unsafe --unarmored-hex"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")
        time.sleep(3)
        resp_info = handle_console_input.ready_info(self.channel)
        if "private key will be exported" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        if "Enter keyring passphrase:" in resp_info:
            self.channel.send("12345678" + "\n")
        time.sleep(3)
        resp_info = handle_console_input.ready_info(self.channel)
        return handle_resp_data.handle_split_esc(resp_info)


if __name__ == '__main__':
    obj = User()
    # a = obj.keys_list()
    # b = obj.keys_add("libai2")
    # c = obj.keys_list()

    # d = obj.keys_private_export("user-uW56anJTEAGU")
    # print(d, type(d))
    # c5e67586a52f46eac844a4735ddd94a06904ad35f52750da3964f4aba7ffd8d8

    # e = obj.keys_private_export("user-2urR4zHid937")
    # print(e, type(e))
    # 703589232e27018ab9197c8b9fc4868a7f66da7953756612532c9bf1924ca52a

    # e = obj.keys_private_export("user-fiA4kToyQa2c")
    # print(e, type(e))
    # 0708790dcd0705ace7557a03e02fa2147f79e569d1bfaf047ac7025388b0ec0e

    # jw2 = obj.keys_private_export("user-phjn64b8ldCq")
    # print(jw2, type(jw2))  # 58eadbee198035d0987ce3ab19257bfb140f8ab7d85861591cd56b0579c3336b

    # jw3 = obj.keys_private_export("user-jYN8IAEXrJMt")
    # print(jw3, type(jw3))  # 58eadbee198035d0987ce3ab19257bfb140f8ab7d85861591cd56b0579c3336b
    # jw4 = obj.keys_private_export("user-cU3gQsMf2Wu1")
    # print(jw4, type(jw4))  # 8ea39a0edab37fd29906132803580a3513ff83e1bedd30dfe9a0bc44f4af1963

    # jw5 = obj.keys_private_export("user-KBxDC8A9kO2J")
    # print(jw5, type(jw5))  # 726845c54d8514a4f01a29caac032909efd0eb58f6808067d1cca454d426e9a0
    #
    # jw6 = obj.keys_private_export("user-dp2Utkf6XbYC")
    # print(jw6, type(jw6))  # fd6bff1bac1e564f32ad524c3a90f62614b07caa331ebb919cc6241332dfc252

    jw7 = obj.keys_private_export("user-wRBYJqWVPyC6")
    print(jw7, type(jw7))  # 536422bc34732fabfb771ea18d1fef2ccdbcc7baee95d0d256a5164452113bc0

    # jw8 = obj.keys_private_export("user-GAONCW3iJ6Xo")
    # print(jw8, type(jw8))  # 8346df95ad19e0816ab6a81a3cb7116df982039859bf312ff5a0dc92661a1cd2

    # jw9 = obj.keys_private_export("user-6xlNWfzIPVa2")
    # print(jw9, type(jw9))  # 6e938cd746fe511fd25b7a1640bd59f7e7b9b764995454858eae22f4eb0fd0ca
