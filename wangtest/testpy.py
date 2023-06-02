import math


class FixedDeposit():
    def __init__(self, balances=None):
        self.balances = balances

    def month(self, year_fixed_deposit_interest_rate=None, month=None, stake=None):
        print(
            f"设置的年化利率是:{year_fixed_deposit_interest_rate}百分比,选择的定期月是{month}个月,存入的本金是{stake}")
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
        # self.oneself_height_reward_2_year = int(
        #     math.ceil((50 * 10 ** 8) / 200))  # 测试环境下一年200个块
        self.heights = end_heights - start_heights
        print("单块收益为:", self.oneself_height_reward)
        # print("用户质押出去后剩余的本金为:", self.balances_existing)

    def test(self):
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

        rewards_one_blok = (self.oneself_height_reward * (stake / (20000000000 * 10 ** 6))) * (10 ** 6)
        rewards = (self.oneself_height_reward * (stake / (20000000000 * 10 ** 6)) * self.heights) * (10 ** 6)

        earnings = int(rewards) - fees
        delegation_end = self.balances_existing - stake - fees

        print(
            f"本来的金额为：{self.balances_existing}umec,减去委托本金和手续费后的余额为：{delegation_end}")
        print(f"单块个人收益为:{rewards_one_blok}")
        # print(f"单块国库收益为：{(self.oneself_height_reward_2_year * (10 ** 6)) - rewards_one_blok}")
        print(f"活期质押金额为:{stake}umec,经历的块高为:{self.heights}设置的手续费为:{fees}umec")
        print(
            f"经历块高产生的利息为:{rewards}，扣除手续费到账收益金额为：{earnings}，")
        print(f"提取收益且扣除手续费后的余额为：{delegation_end + stake + earnings}")
        return rewards

    def kyc_rewards_mec(self, stake=None, fees=0):
        '''
        mec单位的收益
        :param stake: 活期压出去的钱
        :param heights: 经历的块高
        :param fees: 手续费 默认是0
        :return: 产生的活期收益
        '''
        kyc = 1 * 10 ** 6
        rewards = (self.oneself_height_reward * ((stake + kyc) / (20000000000 * 10 ** 6)) * self.heights) * 10 ** 6
        earnings = int(rewards) - fees
        delegation_end = self.balances_existing - stake - fees

        print(
            f"本来的金额为：{self.balances_existing}umec,减去委托本金和手续费后的余额为：{delegation_end}")
        print(f"活期质押金额为:{stake}umec,经历的块高为:{self.heights}设置的手续费为:{fees}umec")
        print(
            f"经历块高产生的利息为:{rewards}，扣除手续费到账收益金额为：{earnings}，")
        print(f"提取收益且扣除手续费后的余额为：{delegation_end + stake + earnings}")
        return earnings


if __name__ == '__main__':
    start_balances = 100000 * 10 ** 6
    stake = 100000 * 10 ** 6
    start_heights = 7535
    end_heights = 7539
    fees = 0

    sd = StakingDelegate(balances_existing=start_balances, start_heights=start_heights, end_heights=end_heights)
    print("----------" * 5, "下面是mec方法的", "----------" * 5)

    now_rewards = sd.rewards_mec(stake=stake, fees=fees)
    b = 6987487031250000
    a = 6974987037500000
    # print(f"单块国库收益为：{b - a}")
    no_1 = 0  # 1187500000
    no_2 = 0  # 1250000000
    no_3 = 0  # 625000000
    no_4 = 0  # 312500000
    no_5 = 0  # 156250000
    no_6 = 0  # 78125000
    no_7 = 0  # 39062500
    no_8 = 0  # 19531299.999999996
    no_9 = 0  # 9765699.999999998
    no_10 = 0  # 4882899.999999999
    no_11 = 0  # 2441500.0
    no_12 = 0  # 1220800.0
    no_13 = 0  # 610400.0
    no_14 = 0  # 305200.0
    no_15 = 0  # 152600.0
    no_16 = 0
    no_17 = 0
    no_18 = 0
    no_19 = 0
    no_20 = 0

    print(f"第一年出块个人总收益为：{now_rewards}")
    now = now_rewards+ no_1 + no_2 + no_3 + no_4 + no_5 + no_6 + no_8 + no_9 + no_10 + no_11 + no_12 + no_13 + no_14 + no_15 + no_16 + no_17 + no_18 + no_19 + no_20
    print(f"现在应该显示的的收益为：{now}")

    # print("----------" * 5, "下面是KYC的方法的", "----------" * 5)
    # sd.kyc_rewards_mec(stake=stake, fees=fees)

    # print("----------" * 5, "下面是umec方法的", "----------" * 5)
    # sd.rewards_umec(stake=stake, heights=heights, fees=fees)
    # print("----------" * 5, "下面是第二次umec方法的", "----------" * 5)
    # stake4 = 200000000
    # balances_existing2 = 40462
    # heights2 = 85
    # sd = StakingDelegate(balances_existing=balances_existing2)
    # sd.rewards_umec(stake=stake4, heights=heights2, fees=fees)

    # print("----------" * 5, "下面是定期计算的", "----------" * 5)
    # balances = 70022997
    # year_rate = 0.233
    # month = 1
    # stake4 = 10000000
    # fd = FixedDeposit(balances=balances)
    # a = fd.month(year_fixed_deposit_interest_rate=year_rate,month=month,stake=stake4)
    # print("收益为：",a)
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
