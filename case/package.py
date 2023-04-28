# -*- coding: utf-8 -*-
import time

from loguru import logger

from config import chain
from tools import handle_name
from x.query import Query
from x.tx import Tx


class BaseClass(object):
    tx = Tx()
    q = Query()


class BankPackage(BaseClass):

    def test_send(self, data):
        """默认使用超管在发送"""
        if data.get("gas"):
            tx_info = self.tx.bank.send_tx(data["from_addr"], data["to_addr"], data["amount"], data["fees"],
                                           data["gas"])
        else:
            tx_info = self.tx.bank.send_tx(data["from_addr"], data["to_addr"], data["amount"], data["fees"])

        logger.info(f"Sent transaction:{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"


class KeysPackage(BaseClass):

    def test_add(self):
        user_name = handle_name.create_username()
        user_info = self.tx.keys.add(user_name)
        user_addr = user_info[0]['address']
        time.sleep(1)
        res = self.q.bank.query_balances(user_addr)
        assert res.get('balances') == list()
        return user_addr

    def test_show(self, data):
        res1 = self.tx.keys.show(f"{data['superadmin']}", True)
        assert type(res1[0]) == dict
        res2 = self.tx.keys.show(f"{data['username']}", False)
        assert type(res2[0]) == dict

    def test_private_export(self, data):
        res1 = self.tx.keys.private_export(f"{data['superadmin']}", True)
        assert type(res1) == str
        res2 = self.tx.keys.private_export(f"{data['username']}", False)
        assert type(res2) == str


class DelegatePackage(BaseClass):

    def test_delegate(self, data):
        del_info = self.tx.staking.delegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"
        return resp

    def test_withdraw(self, data):
        withdraw_info = self.tx.staking.withdraw(data["user_addr"], data["fees"], data['gas'])
        logger.info(f"withdraw_info :{withdraw_info}")
        resp = self.q.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"
        return resp

    def test_undelegate(self, data):
        del_info = self.tx.staking.undelegate(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"

    def test_exit_delegate(self, data):
        del_info = self.tx.staking.exit_delegate(data["from_addr"], data["delegator_address"], data["fees"])
        logger.info(f"undelegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"

    def test_delegate_fixed(self, data):
        del_info = self.tx.staking.delegate_fixed(data["region_user_addr"], data["amount"], data["term"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"
        return resp

    def test_delegate_infinite(self, data):
        del_info = self.tx.staking.delegate_infinite(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"
        return resp

    def test_undelegate_fixed(self, data):
        """提取定期内周期质押"""
        if data.get("gas"):
            del_info = self.tx.staking.undelegate_fixed(data["from_addr"], data["fixed_delegation_id"],
                                                        data["fees"], data["gas"])
        else:
            del_info = self.tx.staking.undelegate_fixed(data["from_addr"], data["fixed_delegation_id"], data["fees"])

        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"

    def test_undelegate_infinite(self, data):
        del_info = self.tx.staking.undelegate_infinite(data["region_user_addr"], data["amount"], data["fees"])
        logger.info(f"delegate tx_info :{del_info}")
        resp = self.q.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"


class FixedPackage(BaseClass):

    def test_create_fixed_deposit(self, data):
        tx_info = self.tx.staking.create_fixed_deposit(data["amount"], data["period"], data["from_addr"], data["fees"],
                                                       data["gas"])
        logger.info(f"do_fixed_deposit tx_info :{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"

    def test_withdraw_fixed_deposit(self, data):
        tx_info = self.tx.staking.withdraw_fixed_deposit(data["deposit_id"], data["from_addr"], data["fees"],
                                                         data["gas"])
        logger.info(f"do_fixed_withdraw tx_info :{tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"


class KycPackage(BaseClass):
    test_keys = KeysPackage()

    def test_new_kyc_user(self, data):
        # 新创建区 需要等待一个块高才能认证KYC，即区金库要有余额
        region_id, region_admin_addr = data['region_id'], data['region_admin_addr']
        user_addr = self.test_keys.test_add()
        logger.info(f"user_addr : {user_addr}")
        tx_info = self.tx.staking.new_kyc(addr=user_addr, region_id=region_id, role=chain.role[1],
                                          from_addr=region_admin_addr, fees=5, gas=1000000)
        logger.info(f"region_id: {region_id} , new_kyc: {tx_info}")
        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"
        return user_addr

    def test_new_kyc_admin(self):
        region_id, region_name = handle_name.create_region_id_and_name()
        logger.info(f"new region_id: {region_id}, region_name:{region_name}")
        # 添加用户
        region_admin_addr = self.test_keys.test_add()
        logger.info(f"region_admin_addr: {region_admin_addr}")

        # 超管认证区域管理员为KYC-admin
        tx_info = self.tx.staking.new_kyc(addr=region_admin_addr, region_id=region_id, role=chain.role[0],
                                          from_addr=self.tx.super_addr, fees=5, gas=1000000)
        logger.info(f"region_admin_addr kyc info: {tx_info}")

        resp = self.q.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"error_code: {resp['code']} != 0"
        return region_admin_addr, region_id, region_name


class RegionPackage(BaseClass):
    test_kyc = KycPackage()

    def test_create_region(self):
        region_admin_addr, region_id, region_name = self.test_kyc.test_new_kyc_admin()

        # 使用SuperAdmin给区管理转账
        send_tx_info = self.tx.bank.send_tx(from_addr=chain.super_addr, to_addr=region_admin_addr, amount=100, fees=1)
        logger.info(f"send_tx_info: {send_tx_info}")

        # 创建区域
        time.sleep(5)
        # as总量:200 00000
        region_info = self.tx.staking.create_region(region_name=region_name, region_id=region_id,
                                                    total_as=chain.REGION_AS, delegators_limit=200,
                                                    fee_rate=0.5, from_addr=region_admin_addr,
                                                    totalStakeAllow=chain.REGION_AS, userMaxDelegateAC=100000,
                                                    userMinDelegateAC=1, fees=2, gas=400000)
        logger.info(f"create_region_info: {region_info}")
        tx_resp = self.q.tx.query_tx(region_info['txhash'])
        assert tx_resp['code'] == 0, f"error_code: {tx_resp['code']} != 0"
        # 等待块高 确保区域内有足够钱用于new-kyc 64ac * 1 / 200 = 0.32ac = 320000usrc、 newkyc至少需要1000000usrc、三个块才能有1AC
        logger.info(f"Make sure there is enough money in the area to spend new-kyc")
        time.sleep((5 * 3) * 2)
        region_info = dict(region_admin_addr=region_admin_addr, region_id=region_id, region_name=region_name)
        logger.info(f"{region_info}")
        return region_admin_addr, region_id, region_name

    def test_update_region(self, data):
        tx_resp = self.tx.staking.update_region(**data)
        time.sleep(5)
        assert tx_resp.get("code") == 0, f"error_code: {tx_resp['code']} != 0"
        logger.info(f"Updated region tx_resp:{tx_resp}")
