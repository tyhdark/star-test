# -*- coding: utf-8 -*-
import inspect
import time

from loguru import logger

from tools.name import UserInfo, RegionInfo, ValidatorInfo
from x.query import Query, HttpQuery
from x.tx import Tx


# 这个文件作为一个中间件，存放各种操作，被调用的时候，只需调用方法就行，不需要重写步骤，方便分层
class Base:
    tx = Tx()
    hq = HttpQuery()
    q = Query()


class Bank(Base):

    def test_send(self, from_addr, to_addr, amount, **kwargs):
        """用户发起转账 好"""
        tx_info = self.tx.bank.send_tx(from_addr, to_addr, amount, **kwargs)
        logger.info(f"{inspect.stack()[0][3]}: {tx_info}")
        # time.sleep(self.tx.sleep_time)
        time.sleep(10)
        resp = self.hq.tx.query_tx(tx_info['txhash'])
        assert resp['code'] == 0, f"test_send failed, resp: {resp}"
        return resp


class Keys(Base):

    def test_add(self, user_name=None):
        """ 添加用户 好 返回的是一串结果信息，不是地址"""
        if user_name is None:
            user_name = UserInfo.random_username()
        self.tx.keys.add(user_name)
        user_info = self.tx.keys.show(user_name)
        assert user_info is not None
        return user_info[0]

    def test_show(self, user_name):
        """展示用户信息，包括地址，可以提取 好"""
        user_info = self.tx.keys.show(user_name)
        assert user_info is not None
        return user_info[0]

    def test_private_export(self, user_name):
        """传入名称，导出私钥 好"""
        pk = self.tx.keys.private_export(user_name)
        assert pk is not None
        return pk

    def test_delete_key(self, addr):
        name = self.q.Key.name_of_addre(addr=addr)
        de = self.tx.Keys.delete(user_name=name)
        return de

class Kyc(Keys):

    # def test_new_kyc_user(self, region_id, region_admin_addr, addr=None, **kwargs):
    #     # 新创建区 需要等待一个块高才能认证KYC，即区金库要有余额
    #     if addr is None:
    #         user_info = self.test_add()
    #     else:
    #         user_info = dict(address=addr)
    #
    #     logger.info(f"user_info: {user_info}")
    #     tx_info = self.tx.staking.new_kyc(addr=user_info["address"], region_id=region_id,
    #                                       role=self.tx.role["user"], from_addr=region_admin_addr, **kwargs)
    #     time.sleep(self.tx.sleep_time)
    #     resp = self.hq.tx.query_tx(tx_info['txhash'])
    #     assert resp['code'] == 0, f"test_new_kyc_user failed, resp: {resp}"
    #     logger.info(f"region_id: {region_id} , new_kyc: {user_info}")
    #     return user_info

    def test_new_kyc_user(self, region_id=None, addr=None):
        """认证kyc,用户就可以，区id会自动拿线上存在的，管理员addre配置文件写了 好了"""
        if addr is None:
            user_info = self.test_add().get('address')
        else:
            user_info = addr
        if region_id is None:
            region_id_variable = RegionInfo.region_for_id_existing()
        else:
            region_id_variable = region_id
        logger.info(f"user_info:{user_info}")
        tx_info = self.tx.staking.new_kyc(user_addr=user_info,
                                          region_id=region_id_variable, from_addr=self.tx.super_addr)
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(tx_hash=tx_info["txhash"])
        assert resp['code'] == 0, f"test_new_kyc_user failed,resp: {resp}"
        logger.info(f"region_id: {region_id},new_kyc_addr:{user_info}")
        return user_info

    # def test_new_kyc_admin(self, **kwargs):
    #     region_id, region_name = RegionInfo.create_region_id_and_name()
    #     logger.info(f"new region_id: {region_id}, region_name:{region_name}")
    #     # 添加用户
    #     region_admin_info = self.test_add()
    #     logger.info(f"region_admin_info: {region_admin_info}")
    #
    #     # 超管认证区域管理员为KYC-admin
    #     tx_info = self.tx.staking.new_kyc(addr=region_admin_info["address"], region_id=region_id,
    #                                       role=self.tx.role["admin"],
    #                                       from_addr=self.tx.super_addr, **kwargs)
    #     time.sleep(self.tx.sleep_time)
    #     resp = self.hq.tx.query_tx(tx_info['txhash'])
    #     assert resp['code'] == 0, f"test_new_kyc_admin failed, resp: {resp}"
    #     logger.info(f"region_id: {region_id} , region_admin_info: {region_admin_info}")
    #     return region_admin_info, region_id, region_name


class Validator(Base):
    def test_create_validator(self, node_name=None):
        """创建验证者节点，如果没有指定node_name，node名称会自动去拿线上没有的，token金额要写到配置文件里面去"""
        if node_name is None:
            node_name_var = ValidatorInfo.validator_node_for_create()
        else:
            node_name_var = node_name
        amount = self.tx.validatortoken
        validator_info = self.tx.Staking.create_validator(node_name=node_name_var, amount=amount)
        time.sleep(self.tx.sleep_time)
        tx_resp = self.hq.tx.query_tx(validator_info['txhash'])
        assert tx_resp['code'] == 0, f"test_create_validator failed,resp:{tx_resp}"
        a = [1, 2, 3, 4, 5, 6]
        print(a[1])
        return node_name_var


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
        time.sleep(self.tx.sleep_time)
        tx_resp = self.hq.tx.query_tx(region_info['txhash'])
        assert tx_resp['code'] == 0, f"test_create_region failed, resp: {tx_resp}"
        # 等待块高 确保区域内有足够钱用于new-kyc 64ac * 1 / 200 = 0.32ac = 320000uac、 new-kyc至少需要1000000uac、4个块才能有1ac
        logger.info(f"Make sure there is enough money in the area to spend new-kyc")
        time.sleep((self.tx.sleep_time * 4) * 2)
        return region_admin_info, region_id, region_name

    # TODO 下次写取没有绑定区的节点名称出来，
    def test_create_region_wang(self, node_name=None):
        """创建区(绑定区),用链上不存在的区的名字，如果指定了节点，就用户节点，如果没有指定节点，就区链上没绑定区的节点 返回区id"""

        region_name = RegionInfo.region_name_for_create()
        region_id = region_name.lower()
        if node_name is None:
            node_name_var = ValidatorInfo.validator_node_for_noregion()
        else:
            node_name_var = node_name
        region_info = self.tx.staking.create_region(from_addr=self.tx.super_addr, region_name=region_name,
                                                    node_name=node_name_var)
        time.sleep(self.tx.sleep_time)
        tx_resp = self.hq.tx.query_tx(region_info['txhash'])
        assert tx_resp['code'] == 0, f"test_create_region failed, resp: {tx_resp}"
        return region_id

    def test_update_region(self, **kwargs):
        region_info = self.tx.staking.update_region(**kwargs)
        logger.info(f"update_region_info: {region_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(region_info['txhash'])
        assert resp['code'] == 0, f"test_update_region failed, resp: {resp}"
        return resp


class Delegate(Base):

    def test_delegate(self, **kwargs):
        """发起活期委托，KYC和非KYC都是这个命令，字典传参传用户地址和金额"""
        del_info = self.tx.staking.delegate(**kwargs)
        # logger.info(f"delegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        # time.sleep(10)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_delegate failed, resp: {resp}"
        return resp

    def test_withdraw(self, **kwargs):
        """用户提取自己的活期收益金额"""
        withdraw_info = self.tx.staking.withdraw_rewards(**kwargs)
        logger.info(f"withdraw_info: {withdraw_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(withdraw_info['txhash'])
        assert resp['code'] == 0, f"test_withdraw failed, resp: {resp}"
        return resp

    def test_undelegate_nokyc(self, **kwargs):
        """步骤：非KYC用户减少活期委托"""
        del_info = self.tx.staking.undelegate_nokyc(**kwargs)
        logger.info(f"undelegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_undelegate failed, resp: {resp}"
        return resp

    def test_undelegate_kyc(self, **kwargs):
        """步骤：KYC用户减少活期委托"""
        del_info = self.tx.staking.undelegate_kyc(**kwargs)
        logger.info(f"undelegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_undelegate failed, resp: {resp}"
        return resp

    def test_exit_delegate(self, **kwargs):
        """步骤：退出活期质押，没用"""
        del_info = self.tx.staking.exit_delegate(**kwargs)
        logger.info(f"exit_delegate_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        assert resp['code'] == 0, f"test_exit_delegate failed, resp: {resp}"
        return resp

    # def test_delegate_infinite(self, **kwargs):
    #     """步骤，创建永久活期质押，没用"""
    #     del_info = self.tx.staking.delegate_infinite(**kwargs)
    #     logger.info(f"delegate_infinite_info: {del_info}")
    #     time.sleep(self.tx.sleep_time)
    #     resp = self.hq.tx.query_tx(del_info['txhash'])
    #     assert resp['code'] == 0, f"test_delegate_infinite failed, resp: {resp}"
    #     return resp

    # def test_undelegate_infinite(self, **kwargs):
    #     """提取永久活期质押，没用"""
    #     del_info = self.tx.staking.undelegate_infinite(**kwargs)
    #     logger.info(f"undelegate_infinite_info: {del_info}")
    #     time.sleep(self.tx.sleep_time)
    #     resp = self.hq.tx.query_tx(del_info['txhash'])
    #     assert resp['code'] == 0, f"test_undelegate_infinite failed, resp: {resp}"
    #     return resp


class Fixed(Base):

    def test_delegate_fixed(self, **kwargs):
        """步骤：发起定期委托 好"""
        del_info = self.tx.staking.deposit_fixed(**kwargs)
        logger.info(f"delegate_fixed_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        logger.info(f"txhash is :{resp}")
        assert resp['code'] == 0, f"test_delegate_fixed failed, resp: {resp}"
        return resp

    def test_withdraw_fixed(self, **kwargs):
        """提取定期质押"""
        del_info = self.tx.staking.withdraw_fixed(**kwargs)
        logger.info(f"undelegate_fixed_info: {del_info}")
        time.sleep(self.tx.sleep_time)
        resp = self.hq.tx.query_tx(del_info['txhash'])
        logger.info(f"return txhash is : {resp}")
        assert resp['code'] == 0, f"test_undelegate_fixed failed, resp: {resp}"
        return resp


if __name__ == '__main__':
    r = Region()
    d = Delegate()
    b = Bank()
    f = Fixed()
    v = Validator()
    k = Kyc()
    keys = Keys()
    # u_name =
    # a.test_add(user_name="testnamekyc005")
    # time.sleep(Tx.sleep_time)
    # u_add = Query.Key.address_of_name(username="testnamekyc004")
    # s_add = Query.Key.address_of_name(username="superadmin")
    # kyc_add = Query.Key.address_of_name(username="testnamekyc005")
    # kyc_add2 = "me1krajder0hxkars23amjrrx0xev3fj6gw69g64l"
    # print(kyc_add)
    # nokyc_add = Query.Key.address_of_name(username="testname011")
    amount = 1000000
    fixed_delegation_id = 16
    # print(u_add)
    # print(s_add)
    # data_send = dict(from_addr=s_add, to_addr=kyc_add, amount=amount)
    # data_new_kyc= dict(addr=u_add,region_id="kor")
    # data_del = dict(from_addr=kyc_add, amount=amount)
    # data_u = dict(from_addr=kyc_add)
    # data_del_fixed = dict(from_addr=kyc_add, amount=amount)
    # data_del_fixed_withdraw = dict(from_addr=kyc_add, fixed_delegation_id=fixed_delegation_id)
    # undelegate_data = dict(from_addr=kyc_add2, amount=amount)
    # undelegate_resp = d.test_undelegate_kyc(**undelegate_data)

    # print(undelegate_resp)
    d_name = "userSara"
    print(Tx.Keys.delete(user_name=d_name))
    # print(b.test_send(**data_send))
    # print(keys.test_add())

    # data1 = dict(from_addr="gea12g50h9fa7jp4tu47f4mn906s3274urjamcvyrd",
    #              to_addr="gea1pv54mu2fa72vhz9wkx3dmw94f8nf6ncppae9pk",
    #              amount=10,
    #              fees=2)
    # print(b.test_send(**data_send))
    # print(d.test_delegate(**data_del))
    # print(keys.test_add())
    # print(k.test_new_kyc_user())
    # k.test_new_kyc_user(addr=kyc_add)
    # print(d.test_withdraw(**data_u))
    # d.test_undelegate_kyc(**data_del)
    # print(d.test_undelegate_nokyc(**data_del))
    # print(f.test_delegate_fixed(**data_del_fixed))
    # f.test_withdraw_fixed(**data_del_fixed_withdraw)
    # r.test_create_region_wang()
    # print(v.test_create_validator())
    pass
