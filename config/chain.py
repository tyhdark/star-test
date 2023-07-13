# -*- coding: utf-8 -*-
import yaml
from nacos import NacosClient

ip = '192.168.0.206'
namespace = '83827568-a530-44f6-ace5-b05b5cc1ed71'
data_id = "chain-test.yml"
group = "alpha"  # ["alpha", "beta", "dev"]


def read_config(ip=ip, namespace=namespace, data_id=data_id, group=group):
    client = NacosClient(ip, namespace=namespace)
    cfg = client.get_config(data_id, group)
    return yaml.safe_load(cfg)


config = read_config()

GasLimit = config["compute"]["DefaultGasLimit"]
Fees = config["compute"]["DefaultFees"]
if __name__ == '__main__':
    pass
