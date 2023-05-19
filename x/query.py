
import inspect
import time

from loguru import logger

from tools import handle_resp_data
from x.base import BaseClass
"""查询用的,查询各种信息,  (第四)
查询区块
转账交易
库
质押权益
铸造厂
"""

class Query(BaseClass):
    """
    查询类
    """

    def __init__(self):
        self.block = self.Block()
        self.tx = self.Tx()
        self.bank = self.Bank()
        self.staking = self.Staking()
        self.mint = self.Mint()

    class Block(object):  # 区块

        @staticmethod  # 静态方法装饰器
        def query_block(self, height=""):  # 查询区块
            """
            返回当前块高
            """
            cmd = Query.ssh_home + f"{Query.chain_bin} q block {height} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            if height:
                return handle_resp_data.handle_yaml_to_dict(res)  # 直接返回
            else:
                resp = handle_resp_data.handle_yaml_to_dict(res)
                block_height = resp['block']['header']['height']  # 返回块的高度
                return block_height

    class Tx(object):  # 转账

        @staticmethod
        def query_tx(tx_hash):
            """查询 tx_hash"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q tx {tx_hash} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            time.sleep(5)
            res = Query.ssh_client.ssh(cmd)
            time.sleep(2)
            return handle_resp_data.handle_yaml_to_dict(res)  # 返回对应的cmd

    class Bank(object):  # 库

        @staticmethod
        def query_balances(addr):
            """查询 addr 余额"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q bank balance {addr} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

    class Staking(object):  # 权益质押

        @staticmethod
        def show_delegation(addr):  # 展示对应用户的货期委托本金
            """查询货期质押"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-delegation {addr} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            time.sleep(5)
            return handle_resp_data.handle_yaml_to_dict(cmd)
        def delegation(addr):  # 展示对应用户的货期委托本金
            """查询货期质押"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-delegation {addr} {Query.chain_id}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            time.sleep(5)
            return handle_resp_data.handle_yaml_to_dict(cmd)

        @staticmethod
        def list_delegation():  # 委托列表
            """查询所有活期质押信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-delegation {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def list_fixed_delegation():  # 固定委托列表,展示所有活期内周期质押信息
            """所有活期内周期质押信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-fixed-delegation {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_delegation(addr):  # 展示 固定质押 在活期内 传地址
            """活期内周期质押信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-fixed-delegation {addr} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def kyc_by_region(region_id):  # KYC 用户表示, 用户归属区
            """查询区域KYC列表"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking kyc-by-region {region_id} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def show_kyc(addr):  # 查询KYC 通过地址
            """查看地址是否为KYC用户,不是就返回错误"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-kyc {addr} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd, strip=False)
            if res.stdout:
                return handle_resp_data.handle_yaml_to_dict(res.stdout)
            else:
                return res.stderr

        @staticmethod
        def list_kyc():  # KYC列表
            """查询kyc列表,"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-kyc {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def list_fixed_deposit():  # 固定质押列表
            """查询固定质押的列表"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-fixed-deposit {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_id(addr, deposit_id):  # 通过id查询固定质押
            """传入地址,和id  查询固定质押"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-fixed-deposit {addr} {deposit_id} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_addr(addr, query_type):  # 通过地址和类型,查询固定质押
            """ 传入地址,和查询类型,查询固定质押"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-fixed-deposit-by-acct {addr} {query_type} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_fixed_deposit_by_region(region_id, query_type):  # 通过地区id,类型查询固定质押
            """ 传入地区id,查询类型,查询固定质押"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-fixed-deposit-by-region {region_id} {query_type} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_region():  # 地区列表
            """查询区域列表"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-region {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            res = Query.ssh_client.ssh(cmd)
            return handle_resp_data.handle_yaml_to_dict(res)

        @staticmethod
        def show_region(region_id):  # 区金库信息.
            """区金库信息"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-region {region_id} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def show_region_by_name(region_name):  # 通过地区名字查询.
            """传入地区名,查询"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-region-by-name {region_name} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def list_validator():  # 验证列表
            """ 查询验证列表,"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking list-validator {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        # validate 参数是 operator_address
        @staticmethod
        def show_validator(validator):  # 展示验证信息,
            """ 传入验证信息,展示"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking show-validator {validator} {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

        @staticmethod
        def params():  # 参数,
            """ 查询参数"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q staking params {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))

    class Mint(object):  # 造币厂,铸造厂

        @staticmethod
        def params():
            """查询铸造参数,Query the current minting parameters"""
            cmd = Query.ssh_home + f"{Query.chain_bin} q mint params {Query.chain_id} {Query.custom_node}"
            logger.info(f"{inspect.stack()[0][3]}: {cmd}")
            return handle_resp_data.handle_yaml_to_dict(Query.ssh_client.ssh(cmd))


if __name__ == '__main__':
    q = Query()
    k = q.staking.list_validator()
    print(k)

    # r = q.staking.show_region("bfdf8d44bc9211ed83a91e620a42e349")
    # r1 = q.staking.show_region_by_name("CZE")
    # # from deepdiff import DeepDiff
    # #
    # # res = DeepDiff(r, r1)
    # r2 = q.staking.params()
    # r3 = q.mint.params()
    # print(r3)
    # res = q.Block.query_block()
    # pass
