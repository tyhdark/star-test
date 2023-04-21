# -*- coding: utf-8 -*-
import time

import pytest

from tools import handle_name
from x.query import Query
from x.tx import Tx


@pytest.mark.P1
class TestKeys:
    tx = Tx()
    q = Query()

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
