import math


class FixedDeposit():
    def __init__(self, balances=None):
        self.balances = balances

    def month(self, year_fixed_deposit_interest_rate=None, month=None, stake=None):
        print(f"设置的年化利率是:{year_fixed_deposit_interest_rate}元,选择的定期月是{month}个月,存入的本金是{stake}")
        rewards = year_fixed_deposit_interest_rate * month / 12 * stake
        print(f"到期后获得的利息是{rewards}")
        sum_balances = self.balances + rewards + stake
        print(f"到期后你的余额为:{sum_balances}")
        return rewards


class StakingDelegate():
    def __init__(self, balances_existing=None, start_heights=None, end_heights=None):
        '''

        :param balances_existing: 质押后剩余的余额
        '''
        self.balances_existing = balances_existing
        self.oneself_height_reward = int(math.ceil((50 * 10 ** 8) / ((365 * 24 * 60 * 60) / 5)))
        self.heights = end_heights - start_heights
        print("单块收益为:", self.oneself_height_reward, "收益类型为:", type(self.oneself_height_reward))
        print("用户质押出去后剩余的本金为:", self.balances_existing)

    def test(self):
        b = 1
        a = self.balances_existing
        print("当前的利息是:")
        return a

    def rewards_mec(self, stake=None, fees=0):
        '''
        mec单位的收益
        :param stake: 活期压出去的钱
        :param heights: 经历的块高
        :param fees: 手续费 默认是0
        :return: 产生的活期收益
        '''
        # rewards = int((793 * (stake / 20000000000) * 10 ** 6 * heights - fees))
        rewards = (self.oneself_height_reward * (stake / 20000000000) * self.heights - fees) * 10 ** 6
        # rewards = (793 * (stake / 20000000000) * heights - fees) * 10 ** 6
        print("活期质押金额为:", stake, "经历的块高为:", self.heights, "设置的手续费为:", fees)
        print("产生的利息为:", rewards, "取出质押和收益后的余额为:",
              int(rewards) + self.balances_existing + (stake * 10 ** 6))
        return rewards

    def kyc_rewards_mec(self, stake=None, fees=0):
        '''
        mec单位的收益
        :param stake: 活期压出去的钱
        :param heights: 经历的块高
        :param fees: 手续费 默认是0
        :return: 产生的活期收益
        '''
        # rewards = int((793 * (stake / 20000000000) * 10 ** 6 * heights - fees))
        rewards = (self.oneself_height_reward * ((stake + 1) / 20000000000) * self.heights - fees) * 10 ** 6
        # rewards = (793 * (stake / 20000000000) * heights - fees) * 10 ** 6
        print("活期质押金额为:", stake, "经历的块高为:", self.heights, "设置的手续费为:", fees)
        print("产生的利息为:", rewards, "取出质押和收益后的余额为:",
              int(rewards) + self.balances_existing + (stake * 10 ** 6))
        return rewards

    def rewards_umec(self, stake, heights, fees=0):
        '''
        umec单位的收益
        :param stake: 活期压出去的钱
        :param heights: 经历的块高
        :param fees: 手续费 默认是0
        :return: 产生的活期收益
        '''
        rewards = int(
            (793 * (stake / (20000000000 * 10 ** 6)) * 10 ** 6 * heights - (fees * 10 ** 6)))
        print("活期质押金额为:", stake, "经历的块高为:", heights, "设置的手续费为:", fees)
        print("产生的利息为", rewards, "取出质押和收益后的余额为:", rewards + self.balances_existing + stake)
        return rewards


if __name__ == '__main__':
    stake = 101
    start_heights = 922
    end_heights = 3270
    # heights = 263
    fees = 0
    balances_existing = 289900000973  # 扣除活期后剩余的金额
    sd = StakingDelegate(balances_existing=balances_existing, start_heights=start_heights, end_heights=end_heights)
    print("----------" * 5, "下面是mec方法的", "----------" * 5)

    sd.rewards_mec(stake=stake, fees=fees)
    # print("----------" * 5, "下面是umec方法的", "----------" * 5)
    # sd.rewards_umec(stake=stake, heights=heights, fees=fees)
    # print("----------" * 5, "下面是第二次umec方法的", "----------" * 5)
    # stake4 = 200000000
    # balances_existing2 = 40462
    # heights2 = 85
    # sd = StakingDelegate(balances_existing=balances_existing2)
    # sd.rewards_umec(stake=stake4, heights=heights2, fees=fees)

    # print("----------" * 5, "下面是定期计算的", "----------" * 5)
    # balances = 289900000973
    # year_rate = 0.013
    # month = 3
    # stake4 = 8276698171
    # fd = FixedDeposit(balances=balances)
    # a = fd.month(year_fixed_deposit_interest_rate=year_rate,month=month,stake=stake4)
    # print(a)
    '''
    print("----------" * 5, "下面是手动计算的", "----------" * 5)
    # # print(balances)
    fees2 = 0
    height2 = 10000
    balances2 = 0
    satking2 = 10000 * 10 ** 6
    interest2 = (793 * (10000 / 20000000000) * height2) - fees2
    interest3 = int(interest2 * 10 ** 6)
    print("活期利息为:", interest3)
    print("质押本金+活期利息+个人原本余额:", satking2 + interest3 + balances2)
    '''
