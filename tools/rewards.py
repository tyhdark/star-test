# -*- coding: utf-8 -*-
# 这个文件用来手动计算收益的
import math
from loguru import logger


class Reward(object):
    # def __init__(self):
    one_block = int(math.ceil((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))

    @classmethod
    def reward_nokyc(cls, stake, end_height=None, start_height=None):
        """
        计算非KYC的收益
        :param stake: 委托金额
        :param end_height: 结束块高
        :param start_height: 开始块高
        :return 返回经历这些块高后的收益
        """
        stakes = stake * (10 ** 6)

        logger.info(f"单块出块奖励：{cls.one_block} mec")
        one_reward = (cls.one_block * (stakes / (20000000000 * 10 ** 6))) * 10 ** 6

        heights = end_height - start_height
        logger.info(f"单块委托收益：{one_reward}umec")
        all_height_reward = int(one_reward * heights)
        logger.info(f"所有块高收益：{all_height_reward}umec")
        return all_height_reward

    @classmethod
    def reward_kyc(cls, stake=None, end_height=None, start_height=None):
        """
        计算KYC的收益
        :param stake: 委托金额
        :param end_height: 结束块高
        :param start_height: 开始块高
        :return 返回经历这些块高后的收益
        """
        stakes = (stake + 1) * (10 ** 6)
        logger.info(f"单块出块奖励：{cls.one_block} mec")
        one_reward = (cls.one_block * (stakes / (20000000000 * 10 ** 6))) * 10 ** 6
        logger.info(f"单块委托收益：{one_reward}umec")
        heights = end_height - start_height
        all_height_reward = int(one_reward * heights)
        logger.info(f"KYC所有块高收益：{all_height_reward}umec")
        return all_height_reward

    @classmethod
    def fixed_reward(cls, rate=None, month=None, amount=None):
        """
        计算定期委托的收益
        :param rate: 费率
        :param month: 月数的枚举值
        :param amount: 金额
        :return 预估收益
        """
        u_amount = amount * (10 ** 6)
        logger.info(
            f"设置的年化利率是:{rate}百分比,选择的定期月是{month}个月,存入的本金是{u_amount}umec")
        rewards = int(rate * month / 12 * u_amount)
        logger.info(f"到期后获得的利息是{rewards}")

        return rewards


if __name__ == '__main__':
    # r.nokyc_reward(10000,1000,996)
    # r.kyc_reward(10000,10000,0)
    # print(Reward.fixed_reward(rate=c, month=6, amount=1000000000))
    # print(r.fixed_reward(rate=0.05, month=1, amount=100000000))
    print(Reward.reward_nokyc(stake=1469, end_height=100, start_height=99))
    reward = Reward.reward_nokyc(stake=1, end_height=101, start_height=100)
    # Reward.fixed_reward(rate=)
