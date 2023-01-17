"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/29 18:19
@Version :  V1.0
@Desc    :  None
"""
import inspect
import time

from loguru import logger

from base.base import BaseClass
from tools import handle_resp_data, calculate, handle_console_input


class KYC(BaseClass):

    def list_kyc(self):
        cmd = self.ssh_home + "./srs-poad query srvault list-kyc --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd)
        return handle_resp_data.handle_yaml_to_dict(res)

    def show_kyc(self, addr):
        """查看地址是否为kyc用户，不是将返回错误"""
        cmd = self.ssh_home + f"./srs-poad query srvault show-kyc {addr}"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd, strip=False)
        if res.stdout:
            return handle_resp_data.handle_yaml_to_dict(res.stdout)
        else:
            return res.stderr

    def new_kyc(self, addr, region_id, role, delegate_limit, from_addr, fees, from_super=True):
        """
        创建区管理员 和 创建区内KYC用户
        :param addr: kyc address
        :param region_id: 所绑定区域ID
        :param role: 区内角色  KYC_ROLE_USER  or KYC_ROLE_ADMIN
        :param delegate_limit: 委托上限
        :param from_addr: 发起地址 区管理员 or 全局管理员
        :param from_super: 发起地址 是超级管理员 需要找到其超管私钥目录
        :param fees: Gas费用
        :return: tx Hash
        """
        delegate_limit = calculate.calculate_src(delegate_limit, reverse=True)
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srvault new-kyc {addr} {region_id} {role} {delegate_limit} " \
                              f"--from {from_addr} --chain-id=srspoa -y --fees={fees}src"

        if from_super:
            cmd += " --home node1"
        else:
            # 区管理员 不能创建 KYC_ROlE_ADMIN
            assert "KYC_ROLE_USER" == role

        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")

        handle_console_input.input_password(self.channel)
        resp_info = handle_console_input.ready_info(self.channel)

        return handle_resp_data.handle_split_esc(resp_info)

    def kyc_bonus(self, addr):
        """查询KYC用户注册所赠1src收益"""
        cmd = self.ssh_home + f"./srs-poad query srstaking kyc-bonus {addr} --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd)
        return handle_resp_data.handle_yaml_to_dict(res)

    def kyc_withdraw_bonus(self, addr, fees):
        """KYC用户提取注册所赠1src收益"""
        fees = calculate.calculate_src(fees, reverse=True)

        cmd = self.ssh_home + f"./srs-poad tx srstaking withdraw --from {addr} --fees={fees}src --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        self.channel.send(cmd + "\n")

        handle_console_input.input_password(self.channel)
        time.sleep(3)
        resp_info = handle_console_input.ready_info(self.channel)

        if "confirm" in resp_info:
            resp_info = handle_console_input.yes_or_no(self.channel)

        return handle_resp_data.handle_split_esc(resp_info)


if __name__ == '__main__':
    obj = KYC()
    # a = obj.list_kyc()
    # b = obj.show_kyc(addr="sil1mg4ls02vas8uj946kn0t9zta3nlrkwdy708d73")
    # print(a)
    # print(b)
    # from user.keys import User

    # user = User()
    #
    # res1 = user.keys_add("zhang1")
    # user_addr = res1[0][0]['address']
    # print(user_addr)
    # c = obj.new_kyc(addr=f"{user_addr}",
    #                 region_id="huabei-03",
    #                 role="KYC_ROLE_ADMIN",
    #                 delegate_limit=100,
    #                 from_addr="sil17xneh8t87qy0z0z4kfx3ukjppqrnwpazwg83dc",
    #                 fees=1)
    # print(c)

    res = obj.kyc_bonus('sil1qczwjrz7mg7h8usfvtpushuvz0xslpa6jscx6y')
    # res = obj.kyc_withdraw_bonus("sil10lkdty8nstfth9yyggaa4x0x2y7qnfr9n0duzq", 1)
    print(res)
