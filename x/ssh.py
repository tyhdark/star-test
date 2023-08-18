# -*- coding: utf-8 -*-
import time

import yaml
from fabric import Connection, Config
from paramiko.channel import Channel


class Client:

    def __init__(self, ip: str, username: str, port: int = 22, password: str = None, certificate: str = None, ):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.certificate = certificate
        self._connection = None
        self.channel = self.create_invoke_shell()

    def __eq__(self, other):
        return True if self.ip == other.ip and self.username == other.username else False

    def __hash__(self):
        return hash(id(self))

    @property
    def connection(self):
        if self._connection and self._connection.is_connected:
            return self._connection
        # TODO: 证书登录
        config = None if self.certificate else Config(overrides={'sudo': {'password': self.password}})
        self._connection = Connection(self.ip, self.username, self.port, config=config,
                                      connect_kwargs={'password': self.password})
        return self._connection

    def exec_cmd(self, command, sudo=False, warn=True, hide='both', strip=True):
        """
        执行shell命令
        :param command: 需要执行的shell命令行
        :param sudo: 是否sudo的方式执行
        :param warn: 当命令执行失败的时候,以警告的方式打印错误,而不是抛出异常
        :param hide: 打印错误信息,设置需要隐藏的输出内容,包含: out、err、both
        :param strip: 是否直接返回命令行执行结果，False返回fabric-result对象
        """
        if sudo:
            result = self.connection.sudo(command, warn=warn, hide=hide)
        else:
            result = self.connection.run(command, warn=warn, hide=hide)
        if strip:
            return result.stdout.strip()
        return result

    def _create_session(self) -> Channel:
        return self.connection.create_session()

    def create_invoke_shell(self) -> Channel:
        """开启一个虚拟窗口"""
        channel = self._create_session()
        channel.get_pty()
        channel.invoke_shell()
        return channel

    class Interactive:
        read_size = 1024 * 5

        @classmethod
        def input_password(cls, channel, resp: str, password: str):
            """输入密码"""
            listen_info = 'Enter keyring passphrase:'
            if resp.endswith(listen_info):
                channel.send(f"{password}" + "\n")
            else:
                raise Exception("not found listen info")

        @classmethod
        def read_channel_data(cls, channel, size=read_size) -> str:
            """
            循环读取channel数据直到接收完整的数据或达到终止条件
            :param channel: SSH通道对象
            :param size: 每次读取的数据大小
            :return: 完整的数据字符串
            """
            resp = ""
            while True:
                time.sleep(0.5)
                if channel.recv_ready():
                    stdout = channel.recv(size)
                    resp += stdout.decode('utf-8')
                    if not resp.isspace():
                        break
            return resp

        @classmethod
        def input_yes_or_no(cls, channel, boolean: bool = True):
            channel.send("y" + "\n") if boolean else channel.send("n" + "\n")
            resp = cls.read_channel_data(channel)
            resp = resp.lstrip("y")
            return resp


class Result:

    @classmethod
    def split_esc(cls, data: str):
        """按esc切割数据"""
        data_info = data.split("")
        return yaml.load(data_info[0], Loader=yaml.FullLoader)

    @classmethod
    def yaml_to_dict(cls, yaml_path: str, is_file=False) -> dict:
        """yaml数据/文件转dict"""
        if yaml_path.isspace():
            return {}
        if is_file:
            with open(yaml_path) as file:
                dict_value = yaml.load(file.read(), Loader=yaml.FullLoader)
        else:
            dict_value = yaml.load(yaml_path, Loader=yaml.FullLoader)
        return dict_value


if __name__ == '__main__':
    pass
