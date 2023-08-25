# -*- coding: utf-8 -*-
import time

import pytest
from loguru import logger

from cases import unitcases
from tools.compute import Compute
from x.query import HttpQuery, Query
from x.tx import Tx


# logger.add("logs/case_{time}.log", rotation="500MB")


@pytest.mark.P0
class TestRegionInfo(object):
    test_region = unitcases.Region()
    test_del = unitcases.Delegate()
    test_kyc = unitcases.Kyc()
    test_bank = unitcases.Bank()
    test_fixed = unitcases.Fixed()
    test_validator = unitcases.Validator()
    tx = Tx()
    hq = HttpQuery()
    q = Query()
    base_cfg = test_bank.tx
    # DefaultTotalStakeAllow 100000 * 400 = 40000000
    default_stake_allow_ac = Compute.as_to_ac(base_cfg.region_as)
    tx_charge = int(float(default_stake_allow_ac) * 0.0001)
    gas_limit = 200000 * (tx_charge + 10)
    fees = tx_charge + 10  # 本次tx多给10个代币,防止fees不足

    def test_update_region(self, setup_update_region_data):
        """测试修改区域信息"""
        logger.info("TestRegionInfo/test_update_region")

        for data in setup_update_region_data:
            logger.info(f"update_region_data: {data}")
            self.test_region.test_update_region(**data)

    # 水位异常场景测试
    # 1.水位和regionAS一致
    def test_stake_allow_eq_region_as(self, setup_create_region_and_kyc_user):
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user
        kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**kyc_data)
        user_addr2 = user_info['address']

        # update region
        data = dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=self.default_stake_allow_ac)
        self.test_region.test_update_region(**data)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
                         amount=self.default_stake_allow_ac + self.base_cfg.fees, gas=self.gas_limit, fees=self.fees)
        send_data2 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2,
                          amount=self.default_stake_allow_ac + self.base_cfg.fees, gas=self.gas_limit, fees=self.fees)
        self.test_bank.test_send(**send_data)
        self.test_bank.test_send(**send_data2)

        del_data = dict(from_addr=user_addr, amount=self.default_stake_allow_ac - 1)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_delegate(**del_data)
        assert "'code': 2018" in str(ex.value)  # ErrRegionTotalStakeAllow parameter error

    # 2.水位是regionAS 80%
    def test_stake_allow_eq_region_as_80(self, setup_create_region_and_kyc_user):
        region_admin_addr, region_id, region_name, user_addr = setup_create_region_and_kyc_user

        data = dict(region_id=region_id, from_addr=region_admin_addr, userMaxDelegateAC=self.default_stake_allow_ac)
        self.test_region.test_update_region(**data)

        send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr,
                         amount=self.default_stake_allow_ac, gas=self.gas_limit, fees=self.fees)
        self.test_bank.test_send(**send_data)

        del_data = dict(from_addr=user_addr, amount=int(self.default_stake_allow_ac * 0.5))
        self.test_del.test_delegate(**del_data)

        # update stake_allow = region_as * 80%
        data = dict(region_id=region_id, from_addr=region_admin_addr,
                    totalStakeAllow=int(self.base_cfg.region_as * 0.8))
        self.test_region.test_update_region(**data)

        kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        user_info = self.test_kyc.test_new_kyc_user(**kyc_data)
        user_addr2 = user_info['address']

        send_data2 = dict(from_addr=self.base_cfg.super_addr, to_addr=user_addr2,
                          amount=self.default_stake_allow_ac, gas=self.gas_limit, fees=self.fees)
        self.test_bank.test_send(**send_data2)

        del_data = dict(from_addr=user_addr2, amount=int(self.default_stake_allow_ac * 0.3))
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_delegate(**del_data)
        assert "'code': 2018" in str(ex.value)

        # 0.3+0.5-2(2个kyc) = 0.8
        del_data = dict(from_addr=user_addr2, amount=int(self.default_stake_allow_ac * 0.3) - 2)
        self.test_del.test_delegate(**del_data)

        # 达到水位之后 可以继续kyc 但是不能继续委托
        kyc_data = dict(region_id=region_id, region_admin_addr=region_admin_addr)
        _ = self.test_kyc.test_new_kyc_user(**kyc_data)

        del_data = dict(from_addr=user_addr2, amount=1)
        with pytest.raises(AssertionError) as ex:
            self.test_del.test_delegate(**del_data)
        assert "'code': 2018" in str(ex.value)

    def test_find_validator(self):
        # {
        #     'commission': {
        #         'commission_rates': {
        #             'max_change_rate': '0.010000000000000000',
        #             'max_rate': '0.200000000000000000',
        #             'rate': '0.100000000000000000'
        #         },
        #         'update_time': '2023-08-23T11:34:57.542134293Z'
        #     },
        #     'consensus_pubkey': {
        #         '@type': '/cosmos.crypto.ed25519.PubKey',
        #         'key': 'qeSrHKdZcrWNGmEfb9U86hq3RGq/0qU8gZ9M8fiKb3g='
        #     },
        #     'delegation_amount': '9000000',
        #     'description': {
        #         'details': '',
        #         'identity': '',
        #         'moniker': 'node5',
        #         'security_contact': '',
        #         'website': ''
        #     },
        #     'jailed': False,
        #     'kyc_amount': '20000000',
        #     'min_self_stake': '1000000',
        #     'operator_address': 'mevaloper1u2swta5eynlnyf0rjpx2d97l50psrqjnd9gwmx',
        #     'owner_address': 'me16lxhdm5p3ma2s4nh8f2rphfla4tzd35vu36q95',
        #     'staker_shares': '999999000000.000000000000000000',
        #     'status': 'BOND_STATUS_BONDED',
        #     'tokens': '999999000000',
        #     'unbonding_height': '0',
        #     'unbonding_ids': [],
        #     'unbonding_on_hold_ref_count': '0',
        #     'unbonding_time': '1970-01-01T00:00:00Z'
        # }

        # - creator: me13t38gy4kp0vcq06sp2ek0na60wd2k50gqpu0ea
        # name: MLT
        # nft_class_id: MLT - NFT - CLASS - ID -
        # operator_address: mevaloper1u2swta5eynlnyf0rjpx2d97l50psrqjnd9gwmx
        # regionId: mlt

        # - address: me1kpc32s5svs8hd5rpvgukd2jas7k8tzmyty6w08
        # name: tyh_test02
        # pubkey: '{"@type":"/cosmos.crypto.secp256k1.PubKey","key":"A6m3NnZASnNJdBVDlnbhkELzh4amTkVJ68WRhWx4hpKE"}'
        # type: local
        addr = 'me1kpc32s5svs8hd5rpvgukd2jas7k8tzmyty6w08'
        # send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=addr, amount=100)
        # resp = self.test_bank.test_send(**send_data)
        # self.hq.tx.query_tx(resp['txhash'])
        # time.sleep(6)
        validator = self.test_validator.find_validator_by_node_name('node5')
        logger.info(f"validator===={validator}")
        logger.info(f"validator delegation_amount 活期委托金额===={validator['delegation_amount']}")
        logger.info(f"validator kyc_amount kyc占用的金额===={validator['kyc_amount']}")
        logger.info(f"validator staker_shares 总占用股份===={validator['staker_shares']}")
        logger.info(f"validator 可用金额===="
                    f"{int(validator['tokens']) - int(validator['kyc_amount']) - int(validator['delegation_amount'])}")
        logger.info(f"可用金额2=={self.test_validator.get_validator_available_pledge_amount_by_kyc_adr(addr)}")
        delegate_data = dict(from_addr=addr, amount=20)
        resp = self.tx.staking.delegate(**delegate_data)
        txhash = self.hq.tx.query_tx(resp['txhash'])
        code = txhash['code']
        assert code == 52
        # code=52 failed to execute message; message index: 0: Node delegation limit exceeded.
        # 超过验证者节点最大可质押数

    def test_my_cmd(self):
        addr = "me10esf6004mf8tcv4hk8wuegtunwx3fcllgqdmfd"

        # 认证kyc
        kyc_data = dict(user_addr=addr, region_id='chn')
        resp = self.tx.staking.new_kyc(**kyc_data)
        code = self.hq.tx.query_tx(resp['txhash'])['code']
        assert code == 0

        # 从超管转钱给用户
        # send_data = dict(from_addr=self.base_cfg.super_addr, to_addr=addr, amount=100)
        # resp = self.test_bank.test_send(**send_data)
        # code = self.hq.tx.query_tx(resp['txhash'])['code']
        # assert code == 0

        # 用户进行活期委托
        delegate_data = dict(from_addr=addr, amount=20)
        resp = self.tx.staking.delegate(**delegate_data)
        txhash = self.hq.tx.query_tx(resp['txhash'])
        code = txhash['code']
        assert code == 0
