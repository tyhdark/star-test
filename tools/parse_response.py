# -*- coding: utf-8 -*-
from tools.middleware import retry_decorator
from x.query import Query, HttpQuery


class HttpResponse:
    q = Query()
    hq = HttpQuery()

    @classmethod
    def get_current_block(cls) -> int:
        current_block = cls.hq.block.query_block()
        return int(current_block["header"]["height"])

    @classmethod
    def get_balance_unit(cls, user_addr, denom) -> dict:
        balance_list = cls.hq.bank.query_balances(user_addr)
        return [i for i in balance_list if i['denom'] == denom][0]

    @classmethod
    def get_region(cls, region_id):
        region_info = cls.hq.staking.region(region_id=region_id)
        return region_info

    @classmethod
    def get_regin_list(cls):
        region_list = cls.hq.staking.region()
        return region_list

    @classmethod
    def get_validator_list(cls):
        validator_list = cls.hq.staking.validator()
        return validator_list

    @classmethod
    @retry_decorator
    def get_delegate(cls, user_addr):
        del_info = cls.q.staking.show_delegation(user_addr)
        return del_info

    @classmethod
    def show_fixed_delegation(cls, addr):
        del_info = cls.q.staking.show_fixed_delegation(addr)
        return del_info

    @classmethod
    def get_kyc_by_region(cls, region_id):
        kyc_info = cls.q.staking.kyc_by_region(region_id)
        return kyc_info

    @classmethod
    def get_fixed_deposit_by_addr(cls, addr, fixed_type):
        fixed_info = cls.q.staking.show_fixed_deposit_by_addr(addr, fixed_type)
        return fixed_info

    @classmethod
    def get_fixed_deposit_by_region(cls, region_id, fixed_type):
        fixed_info = cls.q.staking.show_fixed_deposit_by_region(region_id, fixed_type)
        return fixed_info

    @classmethod
    def get_fixed_deposit_by_id(cls, addr, deposit_id):
        fixed_info = cls.q.staking.show_fixed_deposit_by_id(addr, deposit_id)
        return fixed_info


if __name__ == '__main__':
    pass
