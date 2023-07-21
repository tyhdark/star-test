# -*- coding: utf-8 -*-
# 这个文件用来手动计算收益的
import math
from loguru import logger

class Reward(object):
    # def __init__(self):
    one_block = int(math.ceil((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))

    @classmethod
    def reward_nokyc(cls, stake, end_height=None, start_height=None):
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
        uamount = amount * (10 ** 6)
        logger.info(
            f"设置的年化利率是:{rate}百分比,选择的定期月是{month}个月,存入的本金是{uamount}umec")
        rewards = int(rate * month / 12 * uamount)
        logger.info(f"到期后获得的利息是{rewards}")

        return rewards


if __name__ == '__main__':
    r = Reward()
    # r.nokyc_reward(10000,1000,996)
    # r.kyc_reward(10000,10000,0)
    print(Reward.fixed_reward(rate=0.05, month=1, amount=100000000))
    # print(r.fixed_reward(rate=0.05, month=1, amount=100000000))
