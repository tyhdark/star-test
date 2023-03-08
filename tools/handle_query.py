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
        pass




if __name__ == '__main__':
    q1 = HandleQuery()
    q1.get_region("2357c5d4bd9311ed84f61e620a42e349")
