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
    d = obj.keys_private_export("user-sLyiQT5UKS4G")
    # print(a)
    # print(b)
    # print(c)
    print(d, type(d))
