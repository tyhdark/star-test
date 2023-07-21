"""
读取配置文件的连接参数用户名密码和ssh命令 (第二)
"""
from config import chain
# -*- coding: utf-8 -*-
from dataclasses import dataclass

from config.chain import config
from tools.host import Host


@dataclass
class HostCfg:
    ip: str
    port: int
    username: str
    password: str



@dataclass
class ChainCfg:
    work_dir: str
    chain_id: str
    chain_bin: str
    connect_node: str
    super_addr: str
    keyring_backend: str
    sleep_time: int
    validatortoken:int
    token_unit: dict
    role: dict
    period: dict
    delegate_term: dict
    annual_rate: dict
    fixed_type: dict
    # validatortoken: dict


@dataclass
class ComputeCfg:
    Precision: int
    DefaultRegionAS: int
    TotalAS: int
    TotalMintACCoins: int
    FirstFiveYearsACCoins: int
    BlocksPerYear: int
    InitialMintACAmount: int
    DefaultFeeRate: int
    DefaultGasLimit: int
    DefaultFees: int
    DefaultSuperToRegionAdminAC: int
    DefaultMaxDelegateAC: int
    DefaultMinDelegateAC: int


@dataclass
class HttpCfg:
    api_url: str
    base: dict
    tx: dict
    bank: dict
    staking: dict
    account: dict


class BaseClass:
    # **,下滑线表示私有，一个下划线和两个下划线
    _host = HostCfg(**config["host"])
    # 实例化对象，Host类
    ssh_client = Host(ip=_host.ip, port=_host.port, username=_host.username, password=_host.password)
    channel = ssh_client.create_invoke_shell() # 开启虚拟窗口连接

    chain = ChainCfg(**config["chain"]) # 定义chain
    compute = ComputeCfg(**config["compute"]) # 定义计算
    http = HttpCfg(**config["http"]) # 定义http

    # chain base config
    work_home = chain.work_dir # work_home就是me-chian所在目录
    chain_id = chain.chain_id # chian-id
    chain_bin = chain.chain_bin # "./me-chiand"
    connect_node = chain.connect_node # 节点
    keyring_backend = chain.keyring_backend  #
    cmd = work_home + f"{chain_bin} keys show superadmin -a {keyring_backend}"
    # a = ssh_client.ssh(cmd)
    super_addr = ssh_client.ssh(cmd)  # 超管地址

    # super_addr = chain.super_addr # 超管地址
    keyring_backend = chain.keyring_backend #
    sleep_time = chain.sleep_time # 等待时间
    coin = chain.token_unit # 币单位
    # role = chain.role # 这个用不上
    # period = chain.period # 这个用不上
    delegate_term = chain.delegate_term #定期的月数
    annual_rate = chain.annual_rate # 定期费率设置
    fixed_type = chain.fixed_type # 定期查询用的
    validatortoken = chain.validatortoken


    # compute 计算用的数据
    precision = compute.Precision
    region_as = compute.DefaultRegionAS
    total_as = compute.TotalAS
    total_ac = compute.TotalMintACCoins
    first_five_years_ac = compute.FirstFiveYearsACCoins
    block_per_year = compute.BlocksPerYear
    init_mint_ac = compute.InitialMintACAmount
    fee_rate = compute.DefaultFeeRate
    gas = compute.DefaultGasLimit
    fees = compute.DefaultFees # fees
    super_to_region_admin_amt = compute.DefaultSuperToRegionAdminAC
    max_delegate = compute.DefaultMaxDelegateAC
    min_delegate = compute.DefaultMinDelegateAC

    # http config 接口文档连接
    api_url = http.api_url
    # base module
    query_block = http.base["block"]
    query_block_latest = http.base["block_latest"]
    # tx module
    query_tx_hash = http.tx["hash"]
    # bank module
    query_bank_balances = http.bank["balances"]
    # staking module
    query_delegation = http.staking["delegation"]
    query_delegations = http.staking["delegations"]

    query_region_id = http.staking["region_id"]
    query_region_name = http.staking["region_name"]
    query_regions = http.staking["region_list"]

    query_validator = http.staking["validator"]
    query_validators = http.staking["validators"]

    query_kyc = http.staking["kyc"]
    query_kycs = http.staking["kycs"]

    query_deposit = http.staking['deposit']
    query_deposits = http.staking['deposits']

    # 查询用户
    query_address = http.account["account"]


if __name__ == '__main__':
    a = BaseClass()
    print(a.super_addr)
    # print(a.query_address)
    # print(a.chain_bin,a.chain_id,a.work_home,a.api_url,a.channel,a.coin)
    # print(a)
    print("1")
    print(a.validatortoken)
    print(a.sleep_time)
    print(a.coin['uc'])
    print(a.coin["uc"])
    # print(a.a)
    pass

    """
    # ssh_info = chain.ssh_info["config"]
    ssh_info = chain.ssh_info_meuser["config"]

    ssh_client = Host(**ssh_info)  # 实例化类，把ip地址等传参给类的属性

    ssh_home = chain.ssh_info["home"]  # home根目录
    chain_id = chain.chain_id  # 定义链id required必要
    chain_bin = chain.chain_bin  # 定义链目录,required必要
    custom_node = chain.custom_node  # 定义常用节点,required必要
    super_addr = chain.super_addr  # 定义超管
    keyring_backend = chain.keyring_backend  # 后端Key
    coin = chain.coin  # 币的键值对
    channel = ssh_client.create_invoke_shell()  # 定义虚拟链接频道
    """
