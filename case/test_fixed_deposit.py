"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/1/4 14:40
@Version :  V1.0
@Desc    :  None
"""
#  区管理员地址: sil1c0t54fz5m5yc3jqrr7xvy6yeec70tgk6crs2pj, 区ID: 73685ac68b4c11ed99e21e620a42e34a
#  - name: user-sLyiQT5UKS4G         address: sil18vj3druvnwfmy03mxk0l7s9cuk0shscsx7qyaa
from srstaking.delegate import Delegate
from srvault.fixed_deposit import Deposit

deposit = Deposit()
delegate = Delegate()


def test_do_fixed_deposit(region_user_addr):
    # 区内kyc 发起定期存款
    res = deposit.do_fixed_deposit(amount=10, period="PERIOD_3_MONTHS", from_addr=region_user_addr, fees=1)
    print(res)


def test_delegate(region_user_addr, region_id):
    del_info_res = delegate.create_delegate(region_user_addr, 10, region_id, 1)
    print(del_info_res)


def test_add_delegate(region_user_addr, ):
    del_info_res = delegate.add_delegate(region_user_addr, 11, 1)
    print(del_info_res)


if __name__ == '__main__':
    # kyc_user = "sil18vj3druvnwfmy03mxk0l7s9cuk0shscsx7qyaa"
    # test_do_fixed_deposit("sil18vj3druvnwfmy03mxk0l7s9cuk0shscsx7qyaa")
    # test_delegate("sil1qczwjrz7mg7h8usfvtpushuvz0xslpa6jscx6y", "2cfb26828d6c11ed8f731e620a42e34a")
    test_add_delegate("sil1qczwjrz7mg7h8usfvtpushuvz0xslpa6jscx6y")
    pass
