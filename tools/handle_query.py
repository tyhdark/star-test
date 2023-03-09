# -*- coding: utf-8 -*-
from x.query import Query


class HandleQuery(object):
    q = Query()

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


if __name__ == '__main__':
    q1 = HandleQuery()
    # q1.get_region("b99bd980be6b11eda4291e620a42e349")
    q1.get_delegate("sil13htu9zqv8nfzdx0939qd6g3u2x582tmneer6xw")
    # q1.get_regin_list()
