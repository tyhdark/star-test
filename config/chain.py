# -*- coding: utf-8 -*-
import yaml
from nacos import NacosClient

ip = '192.168.0.206'
namespace = '280ca1b7-f010-4f11-9240-9c4e58223f42'
data_id = "chain-test.yml"
group = "dev"  # ["alpha", "beta", "dev"]


def read_config(ip=ip, namespace=namespace, data_id=data_id, group=group):
    client = NacosClient(ip, namespace=namespace)
    cfg = client.get_config(data_id, group)
    return yaml.safe_load(cfg)


config = read_config()

GasLimit = config["compute"]["DefaultGasLimit"]
Fees = config["compute"]["DefaultFees"]
if __name__ == '__main__':
    pass
