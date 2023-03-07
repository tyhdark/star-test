# -*- coding: utf-8 -*-
import time

from tools import handle_name
from x.query import Query
from x.tx import Tx


class TestKeys:
    tx = Tx()
    q = Query()

    def test_add(self):
        user_name = handle_name.create_username()
        user_info = self.tx.keys.add(user_name)
        user_addr = user_info[0][0]['address']
        time.sleep(1)
        res = self.q.bank.query_balances(user_addr)
        assert res.get('balances') == list()
        return user_addr

    def test_list(self):
        kyc_list = self.tx.keys.list()
        time.sleep(1)
        assert type(kyc_list) == list

    def test_show(self):
        res1 = self.tx.keys.show("wang", True)
        assert type(res1[0]) == dict
        res2 = self.tx.keys.show("user-ry2kCtxpJmY9", False)
        assert type(res2[0]) == dict

    def test_private_export(self):
        res1 = self.tx.keys.private_export("wang", True)
        assert type(res1) == str
        res2 = self.tx.keys.private_export("user-ry2kCtxpJmY9", False)
        assert type(res2) == str
