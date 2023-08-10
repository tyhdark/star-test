# -*- coding: utf-8 -*-
import os
import random
import time

from fabric import Connection, Config
from paramiko.channel import Channel


class Host:

    def __init__(self,
                 ip: str,
                 username: str,
                 certificate: str = None,
                 password: str = None,
                 port: int = 22,
                 ):
        """
        初始化远程主机对象并尝试连接，支持免密/密码/证书方式。

        Args:
            ip: IP地址
            username: 用户名
            certificate: 证书
            password: 密码/证书密码
            port: ssh端口
        """
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
        """ 单例模式连接到服务器,支持免密/密码/证书方式
        """
        if self._connection and self._connection.is_connected:
            return self._connection

        if self.certificate:
            # todo: 证书方式连接
            config = None
        else:
            config = Config(overrides={'sudo': {'password': self.password}})

        self._connection = Connection(self.ip, self.username, self.port, config=config,
                                      connect_kwargs={'password': self.password})
        return self._connection

    def pid(self, name):
        """ 通过进程名字，获取远程主机的进程号
        """
        return self.ssh(f'ps -ef | grep {name} | grep -v grep | ' + "awk {'print $2'}")

    def ssh(self, command, sudo=False, warn=True, hide='both', strip=True):
        """ 在远程主机上执行ssh命令

        Args:
            command: 需要执行的shell命令行
            sudo: 是否用sudo的方式执行
            warn: 当命令执行失败的时候，以警告的方式打印错误，而不是抛出异常
            hide: 打印错误信息时，需要隐藏的输出内容，包含：out、err、both
            strip: 是否直接返回命令行执行结果，False返回fabric-result对象
        """
        if sudo:
            result = self.connection.sudo(command, warn=warn, hide=hide)
        else:
            result = self.connection.run(command, warn=warn, hide=hide)
        if strip:
            return result.stdout.strip()
        return result

    def file_exist(self, path):
        """ 判断目录或文件是否已存在于远程主机
        """
        time.sleep(random.randint(1, 3))
        return self.ssh(f'test -e {path}', strip=False).ok

    def write_file(self, content: str, file):
        """ 将文本内容写入远程主机的文件，目前仅支持写入新的文件
        # todo： 支持写入已存在的文件，包括覆盖、追加等方式
        """
        path, _ = os.path.split(file)
        if path:
            self.ssh(f'mkdir -p {path}')

        content = str(content).replace('"', r'\"')
        self.ssh(rf'echo "{content}" > {file}')

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



