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
    keyring_backend: str
    sleep_time: int
    token_unit: dict
    role: dict
    period: dict
    delegate_term: dict
    annual_rate: dict
    fixed_type: dict


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


class BaseClass:
    _host = HostCfg(**config["host"])
    ssh_client = Host(ip=_host.ip, port=_host.port, username=_host.username, password=_host.password)
    channel = ssh_client.create_invoke_shell()

    chain = ChainCfg(**config["chain"])
    compute = ComputeCfg(**config["compute"])
    http = HttpCfg(**config["http"])

    # chain base config
    work_home = chain.work_dir
    chain_id = chain.chain_id
    chain_bin = chain.chain_bin
    connect_node = chain.connect_node
    keyring_backend = chain.keyring_backend
    get_superadmin = f"{work_home} {chain_bin} keys show superadmin -a {keyring_backend}"
    super_addr = ssh_client.ssh(command=get_superadmin)
    sleep_time = chain.sleep_time
    coin = chain.token_unit
    role = chain.role
    period = chain.period
    delegate_term = chain.delegate_term
    annual_rate = chain.annual_rate
    fixed_type = chain.fixed_type

    # compute
    precision = compute.Precision
    region_as = compute.DefaultRegionAS
    total_as = compute.TotalAS
    total_ac = compute.TotalMintACCoins
    first_five_years_ac = compute.FirstFiveYearsACCoins
    block_per_year = compute.BlocksPerYear
    init_mint_ac = compute.InitialMintACAmount
    fee_rate = compute.DefaultFeeRate
    gas = compute.DefaultGasLimit
    fees = compute.DefaultFees
    super_to_region_admin_amt = compute.DefaultSuperToRegionAdminAC
    max_delegate = compute.DefaultMaxDelegateAC
    min_delegate = compute.DefaultMinDelegateAC

    # http config
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


if __name__ == '__main__':
    a = BaseClass()
    pass
