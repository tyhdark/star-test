# -*- coding: utf-8 -*-
from x.query import Query


class HandleQuery(object):
    q = Query()

    @classmethod
    def get_block(cls):
        current_block = int(cls.q.block.query_block())
        return current_block

    @classmethod
    def get_balance(cls, user_addr, denom):
        balances_info = cls.q.bank.query_balances(user_addr)
        user_balance = balances_info['balances']
        return [i for i in user_balance if i['denom'] == denom][0]

    @classmethod
    def get_region(cls, region_id):
        region_info = cls.q.staking.show_region(region_id)
        return region_info

    @classmethod
    def get_delegate(cls, user_addr):
        del_info = cls.q.staking.show_delegation(user_addr)
        return del_info

    @classmethod
    def get_regin_list(cls):
        region_list = cls.q.staking.list_region()
        return region_list

    @classmethod
    def get_kyc_by_region(cls, region_id):
        kyc_info = cls.q.staking.kyc_by_region(region_id)
        return kyc_info

    @classmethod
    def get_fixed_deposit_by_addr(cls, addr, fixed_type):
        kyc_info = cls.q.staking.show_fixed_deposit_by_addr(addr, fixed_type)
        return kyc_info

    @classmethod
    def get_mint_params(cls):
        mint_info = cls.q.mint.params()
        blocks_per_year = int(mint_info['blocks_per_year'])
        blocks_per_year /= 43800
        return blocks_per_year


if __name__ == '__main__':
    q1 = HandleQuery()
    # q1.get_region("49b7bc6abeed11ed9fc31e620a42e349")
    # q1.get_delegate("sil13htu9zqv8nfzdx0939qd6g3u2x582tmneer6xw")
    # q1.get_regin_list()
    # q1.get_fixed_deposit_by_addr("sil1f85whrg3zsyhe2d52zt0utjx7mh6vepqnhgwll", chain.fixed_type[0])
    q1.get_mint_params()
