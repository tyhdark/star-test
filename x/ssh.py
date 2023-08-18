# -*- coding: utf-8 -*-

from fabric import Connection, Config
from paramiko.channel import Channel


class Client:

    def __init__(self, ip: str, username: str, port: int = 22, password: str = None, certificate: str = None, ):
        self.ip = ip
        self.port = port
        self.username = username
        self.certificate = certificate
        self.password = password
        self._connection = None

    def __eq__(self, other):
        if self.ip == other.ip and self.username == other.username:
            return True
        return False

    def __hash__(self):
        return hash(id(self))

    @property
    def connection(self):
        if self._connection and self._connection.is_connected:
            return self._connection

        if self.certificate:
            config = None
        else:
            config = Config(overrides={'sudo': {'password': self.password}})

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

    def create_session(self) -> Channel:
        """创建一个会话"""
        channel = self.connection.create_session()
        return channel

    def create_invoke_shell(self) -> Channel:
        """开启一个虚拟窗口"""
        channel = self.create_session()
        channel.get_pty()
        channel.invoke_shell()
        return channel


if __name__ == '__main__':
    pass
