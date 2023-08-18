# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, fields

import yaml
from nacos import NacosClient

ip = '192.168.0.206'
namespace = '280ca1b7-f010-4f11-9240-9c4e58223f42'
data_id = "chain-test.yml"
group = "beta"  # ["alpha", "beta", "dev"]


class NacosConfig:

    def __init__(self, ip, namespace):
        self.ip = ip
        self.namespace = namespace
        self.client = NacosClient(self.ip, namespace=self.namespace)

    def get_config(self, data_id, group):
        return yaml.safe_load(self.client.get_config(data_id, group))


@dataclass
class IterMixin:
    def __iter__(self):
        for fld in fields(self):
            field_name, field_type = fld.name, fld.type
            field_value = getattr(self, field_name)
            yield field_name, field_type, field_value


@dataclass
class Host(IterMixin):
    ip: str
    port: int
    username: str
    password: str
    chain_work_path: str


@dataclass
class Mint(IterMixin):
    convert_unit: int
    total_coin: int
    base_denom: str
    denom: str


@dataclass
class Staking(IterMixin):
    period: dict
    annual_rate: dict
    fixed_type: dict


@dataclass
class GlobalFlags(IterMixin):
    chain_id: str = field(default="--chain-id=me-chain")  # The network chain ID (default "mechain")
    home: str = field(default="--home=/home/user1/.me-chain")  # directory for config and data
    log_format: str = field(default="--log_format=plain")  # The logging format (json|plain)
    log_level: str = field(default="--log_level=info")  # The logging level (trace|debug|info|warn|error|fatal|panic)
    trace: any = field(default="--trace")  # print out full stack trace on errors


@dataclass
class Flags(IterMixin):
    account_number: str = field(default="--account-number=")  # account number of signing account (offline mode only)
    aux: any = field(default="--aux")  # Generate aux signer data instead of sending a tx
    broadcast_mode: str = field(default="-b=sync")  # Transaction broadcasting mode (sync|async|block)  (default "sync")
    # ignore the --gas flag and perform a simulation of a transaction,
    # but don't broadcast it (when enabled, the local Keybase is not accessible)
    dry_run: any = field(default="--dry_run")
    fee_granter: str = field(default="--fee-granter=")  # Fee granter grants fees for the transaction
    # Fee payer pays fees for the transaction instead of deducting from the signer
    fee_payer: str = field(default="--fee-payer=")
    fees: str = field(default="--fees=")  # Fees to pay along with transaction; eg: 10uatom
    from_: str = field(default="--from=")  # Name or address of private key with which to sign
    # gas limit to set per-transaction; set to "auto" to calculate required gas automatically (default 200000)
    gas: str = field(default="--gas=")
    # Adjustment factor to be multiplied against the estimate returned by the tx simulation;
    # if the gas limit is set manually this flag is ignored (default 1.0)
    gas_adjustment: float = field(default="--gas_adjustment=1.0")
    gas_prices: str = field(default="--gas-prices=")  # Gas prices to determine the transaction fee (e.g. 10uatom)
    # Build an unsigned transaction and write it to STDOUT (when enabled, the local Keybase is not accessible)
    generate_only: any = field(default="--generate-only")
    # Select keyring's backend (os|file|kwallet|pass|test|memory)  (default "test")
    keyring_backend: str = field(default="--keyring-backend=test")
    # The client Keyring directory; if omitted, the default 'home' directory will be used
    keyring_dir: str = field(default="--keyring-dir=")
    ledger: any = field(default="--ledger")  # Use a connected Ledger device
    # <host>:<port> to tendermint rpc interface for this chain (default "tcp://localhost:26657")
    node: str = field(default="--node=tcp://localhost:26657")
    note: str = field(default="--note=")  # A note to be included in the transaction;
    offline: any = field(default="--offline")  # Offline mode (does not allow any online functionality)
    output: str = field(default="--output=json")  # Output format (text|json)
    sequence: int = field(default="-s=")  # The sequence number of the signing account (offline mode only)
    # The transaction sign mode (direct|amino-json|amino-std) this is an advanced feature
    sign_mode: str = field(default="--sign-mode=direct")
    # Set a block timeout height to prevent the tx from being committed past a certain height
    timeout_height: int = field(default="--timeout-height=")
    # Tip is the amount that is going to be transferred to the fee payer on the target chain.
    # This flag is only valid when used with --aux, and is ignored if the target chain didn't enable the TipDecorator
    tip: any = field(default="--tip")
    yes: str = field(default="-y")  # Skip tx broadcasting prompt confirmation


@dataclass
class ApplicationChain(IterMixin):
    Host: Host
    GlobalFlags: GlobalFlags
    Flags: Flags
    Mint: Mint
    Staking: Staking


class Config(NacosConfig):

    def __init__(self, ip, namespace, data_id, group):
        super().__init__(ip, namespace)
        self.config_data = self.get_config(data_id, group)

    def __deserialize(self, key):
        class_obj = globals().get(key)
        if class_obj is None:
            raise ValueError(f"Invalid config key: {key}")
        _value = class_obj(**self.config_data[key])
        return _value

    def deserialize_application_chain(self):
        _host = self.__deserialize("Host")
        _mint = self.__deserialize("Mint")
        _compute = self.__deserialize("Compute")
        _coin = self.__deserialize("Coin")
        _stake = self.__deserialize("Stake")
        app = ApplicationChain(Host=_host, Mint=_mint, Compute=_compute, Coin=_coin, Stake=_stake,
                               GlobalFlags=GlobalFlags(), Flags=Flags())
        return app


cfg = Config(ip, namespace, data_id, group)
app_chain = cfg.deserialize_application_chain()
