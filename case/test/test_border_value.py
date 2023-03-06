# -*- coding: utf-8 -*-
"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/1/15 18:14
@Version :  V1.0
@Desc    :  None
"""
from case.test.test_create_region_and_delegate import super_admin_tx_user, test_add_region_kyc, tx
from case.test.test_fixed_deposit import delegate
from tools.calculate import border_value, border_value2

region_admin_addr = 'sil1l5sewkftwcgacr66sty0j3v0xh857xlj09h9a6'
region_id = '99ea0316949811ed88651e620a42e349'  # MDV


def test_01():
    """边界值进行活期委托"""
    region_user_addr = test_add_region_kyc(region_id, region_admin_addr)
    super_admin_tx_user(region_user_addr)
    border_value()
    del_info = delegate.create_delegate(region_user_addr, 10, region_id, 1)
    resp = tx.query_tx(del_info['txhash'])
    assert resp['code'] == 0


def test_02():
    """边界值进行活期委托"""
    region_user_addr = test_add_region_kyc(region_id, region_admin_addr)
    super_admin_tx_user(region_user_addr)
    border_value2()
    del_info = delegate.create_delegate(region_user_addr, 10, region_id, 1)
    resp = tx.query_tx(del_info['txhash'])
    assert resp['code'] == 0


if __name__ == '__main__':
    test_01()
