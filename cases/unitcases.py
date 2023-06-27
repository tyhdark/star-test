# -*- coding: utf-8 -*-
import inspect
import time

from loguru import logger

from tools.name import UserInfo, RegionInfo
from x.query import Query, HttpQuery
from x.tx import Tx


class Base(object):
    tx = Tx()
    hq = HttpQuery()
    q = Query()


class Bank(Base):

    def test_send(self, from_addr, to_addr, amount, **kwargs):
        tx_info = self.tx.bank.send_tx(from_addr, to_addr, amount, **kwargs)
        logger.info(f"{inspect.stack()[0][3]}: {tx_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"test_send failed, resp: {resp}"


class Keys(Base):

    def test_add(self, user_name=None):
        if user_name is None:
            user_name = UserInfo.random_username()
        self.tx.keys.add(user_name)
        user_info = self.tx.keys.show(user_name)
        assert user_info is not None
        return user_info[0]

    def test_show(self, user_name):
        user_info = self.tx.keys.show(user_name)
        assert user_info is not None
        return user_info[0]

    def test_private_export(self, user_name):
        pk = self.tx.keys.private_export(user_name)
        assert pk is not None
        return pk


class Kyc(Keys):

    def test_new_kyc_user(self, region_id, region_admin_addr, addr=None, **kwargs):
        # 新创建区 需要等待一个块高才能认证KYC，即区金库要有余额
        if addr is None:
            user_info = self.test_add()
        else:
            user_info = dict(address=addr)

        logger.info(f"user_info: {user_info}")
        tx_info = self.tx.staking.new_kyc(addr=user_info["address"], region_id=region_id,
                                          role=self.tx.role["user"], from_addr=region_admin_addr, **kwargs)
        logger.info(f"region_id: {region_id} , new_kyc: {tx_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"test_new_kyc_user failed, resp: {resp}"
        return user_info

    def test_new_kyc_admin(self, **kwargs):
        region_id, region_name = RegionInfo.create_region_id_and_name()
        logger.info(f"new region_id: {region_id}, region_name:{region_name}")
        # 添加用户
        region_admin_info = self.test_add()
        logger.info(f"region_admin_info: {region_admin_info}")

        # 超管认证区域管理员为KYC-admin
        tx_info = self.tx.staking.new_kyc(addr=region_admin_info["address"], region_id=region_id,
                                          role=self.tx.role["admin"],
                                          from_addr=self.tx.super_addr, **kwargs)
        logger.info(f"new_region_admin_kyc: {tx_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"test_new_kyc_admin failed, resp: {resp}"
        return region_admin_info, region_id, region_name


class Region(Kyc, Bank):

    def test_create_region(self, **kwargs):
        region_admin_info, region_id, region_name = self.test_new_kyc_admin(**kwargs)

        # 使用SuperAdmin给区管理转账
        self.test_send(from_addr=self.tx.super_addr, to_addr=region_admin_info["address"],
                       amount=self.tx.super_to_region_admin_amt, **kwargs)

        time.sleep(self.tx.sleep_time)

        region_info = self.tx.staking.create_region(region_name=region_name, region_id=region_id,
                                                    total_as=self.tx.region_as, fee_rate=self.tx.fee_rate,
                                                    from_addr=region_admin_info["address"],
                                                    totalStakeAllow=self.tx.region_as,
                                                    userMaxDelegateAC=self.tx.max_delegate,
                                                    userMinDelegateAC=self.tx.min_delegate, **kwargs)
        logger.info(f"create_region_info: {region_info}")
        time.sleep(self.tx.sleep_time)
        tx_resp = self.hq.tx.query_tx(region_info['txhash'])
        assert tx_resp['code'] == 0, f"test_create_region failed, resp: {tx_resp}"
        # 等待块高 确保区域内有足够钱用于new-kyc 64ac * 1 / 200 = 0.32ac = 320000uac、 new-kyc至少需要1000000uac、4个块才能有1ac
        logger.info(f"Make sure there is enough money in the area to spend new-kyc")
        time.sleep((self.tx.sleep_time * 4) * 2)
        return region_admin_info, region_id, region_name

    def test_update_region(self, **kwargs):
        region_info = self.tx.staking.update_region(**kwargs)
        logger.info(f"update_region_info: {region_info}")
        time.sleep(self.tx.sleep_time)
        tx_resp = self.hq.tx.query_tx(region_info['txhash'])
        assert tx_resp['code'] == 0, f"test_update_region failed, resp: {tx_resp}"


class Delegate(Base):

    def test_delegate(self, **kwargs):
        del_info = self.tx.staking.delegate(**kwargs)
        logger.info(f"delegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_delegate failed, resp: {resp}"

    def test_withdraw(self, **kwargs):
        withdraw_info = self.tx.staking.withdraw(**kwargs)
        logger.info(f"withdraw_info: {withdraw_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0, f"test_withdraw failed, resp: {resp}"

    def test_undelegate(self, **kwargs):
        del_info = self.tx.staking.undelegate(**kwargs)
        logger.info(f"undelegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_undelegate failed, resp: {resp}"

    def test_exit_delegate(self, **kwargs):
        del_info = self.tx.staking.exit_delegate(**kwargs)
        logger.info(f"exit_delegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_exit_delegate failed, resp: {resp}"

    def test_delegate_fixed(self, **kwargs):
        del_info = self.tx.staking.delegate_fixed(**kwargs)
        logger.info(f"delegate_fixed_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_delegate_fixed failed, resp: {resp}"

    def test_delegate_infinite(self, **kwargs):
        del_info = self.tx.staking.delegate_infinite(**kwargs)
        logger.info(f"delegate_infinite_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_delegate_infinite failed, resp: {resp}"

    def test_undelegate_fixed(self, **kwargs):
        """提取定期内周期质押"""
        del_info = self.tx.staking.undelegate_fixed(**kwargs)
        logger.info(f"undelegate_fixed_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_undelegate_fixed failed, resp: {resp}"

    def test_undelegate_infinite(self, **kwargs):
        del_info = self.tx.staking.undelegate_infinite(**kwargs)
        logger.info(f"undelegate_infinite_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_undelegate_infinite failed, resp: {resp}"


class Fixed(Base):

    def test_create_fixed_deposit(self, **kwargs):
        tx_info = self.tx.staking.create_fixed_deposit(**kwargs)
        logger.info(f"do_fixed_deposit_info: {tx_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"test_create_fixed_deposit failed, resp: {resp}"

    def test_withdraw_fixed_deposit(self, **kwargs):
        tx_info = self.tx.staking.withdraw_fixed_deposit(**kwargs)
        logger.info(f"do_fixed_withdraw_info :{tx_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"test_withdraw_fixed_deposit failed, resp: {resp}"


if __name__ == '__main__':
    a = Region()
    # data1 = dict(from_addr="gea12g50h9fa7jp4tu47f4mn906s3274urjamcvyrd",
    #              to_addr="gea1pv54mu2fa72vhz9wkx3dmw94f8nf6ncppae9pk",
    #              amount=10,
    #              fees=2)
    # a.test_send(**data1)
    pass
