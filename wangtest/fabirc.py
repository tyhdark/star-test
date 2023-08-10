from fabric import Connection

# 建议将ssh连接所需参数变量化
# user = 'wangzhibiao'
# host = '172.17.195.4'
# password = '123456'
# port = 2222
user = 'meuser'
host = '192.168.0.207'
password = '12345678'
port = 22

# 利用fabric.Connection快捷创建连接
# c = Connection(host=f'{user}@{host}',
#                connect_kwargs=dict(
#                    password = password
#                ))
conn = Connection(host=host, user=user, connect_kwargs={'password': password},port=port)
# 利用run方法直接执行传入的命令
conn.run('pwd')
