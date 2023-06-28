# -*- coding: utf-8 -*-
from config.chain import config
from tools.host import Host


class BaseClass(object):
    # host config
    host_config = config["host"]
    ssh_client = Host(**host_config)
    channel = ssh_client.create_invoke_shell()

    # chain base config
    work_home = config["chain"]["work_dir"]
    chain_id = config["chain"]["chain_id"]
    chain_bin = config["chain"]["chain_bin"]
    connect_node = config["chain"]["connect_node"]
    super_addr = config["chain"]["super_addr"]
    keyring_backend = config["chain"]["keyring_backend"]
    sleep_time = config["chain"]["sleep_time"]
    coin = config["chain"]["token_unit"]
    role = config["chain"]["role"]
    period = config["chain"]["period"]
    delegate_term = config["chain"]["delegate_term"]
    annual_rate = config["chain"]["annual_rate"]
    fixed_type = config["chain"]["fixed_type"]

    # compute
    precision = config["compute"]["Precision"]
    region_as = config["compute"]["DefaultRegionAS"]
    total_as = config["compute"]["TotalAS"]
    total_ac = config["compute"]["TotalMintACCoins"]
    first_five_years_ac = config["compute"]["FirstFiveYearsACCoins"]
    block_per_year = config["compute"]["BlocksPerYear"]
    init_mint_ac = config["compute"]["InitialMintACAmount"]
    fee_rate = config["compute"]["DefaultFeeRate"]
    gas = config["compute"]["DefaultGasLimit"]
    fees = config["compute"]["DefaultFees"]
    super_to_region_admin_amt = config["compute"]["DefaultSuperToRegionAdminAC"]
    max_delegate = config["compute"]["DefaultMaxDelegateAC"]
    min_delegate = config["compute"]["DefaultMinDelegateAC"]

    # http config
    api_url = config["http"]["api_url"]
    # base module
    query_block = config["http"]["base"]["block"]
    query_block_latest = config["http"]["base"]["block_latest"]
    # tx module
    query_tx_hash = config["http"]["tx"]["hash"]
    # bank module
    query_bank_balances = config["http"]["bank"]["balances"]
    # staking module
    query_delegation = config["http"]["staking"]["delegation"]
    query_delegations = config["http"]["staking"]["delegations"]

    query_region_id = config["http"]["staking"]["region_id"]
    query_region_name = config["http"]["staking"]["region_name"]
    query_regions = config["http"]["staking"]["region_list"]

    query_validator = config["http"]["staking"]["validator"]
    query_validators = config["http"]["staking"]["validators"]
