# -*- coding: utf-8 -*-
import random
import string
# from faker import Faker
from x.query import HttpQuery


class RegionInfo:
    region_name = '"\nAFG":"阿富汗","\nAGO":"安哥拉","\nAIA":"安圭拉","\nALA":"奥兰","\nALB":"阿尔巴尼亚","\nAND":"安道尔",' \
                  '"\nARE":"阿联酋","\nARG":"阿根廷","\nARM":"亚美":"南极洲","\nATF":"法属南部和南极领地",' \
                  '"\nATG":"安提瓜和巴布达","\nAUS":"澳大利亚","\nAUT":"奥地利","\nAZE":"阿塞拜疆","\nBDI":"布隆迪",' \
                  '"\nBEL":"比利时","\nBFA":"布基纳法索","\nBGD":"孟加拉国","\nBGR":"保加利亚","\nBHR":"巴林","\nBHS":"巴哈马",' \
                  '"\nBIH":"波黑","\nBLM":"圣巴泰勒米","\nBLR":"白俄罗斯","\nBLZ":"伯利兹"\nBRA":"巴西","\nBRB":"巴巴多斯",' \
                  '"\nBRN":"文莱","\nBTN":"不丹","\nBVT":"布韦岛","\nBWA":"博茨瓦纳","\nCAF":"中非","\nCAN":"加拿大",' \
                  '"\nCCK":"科科斯群岛","\nCHN":"中国","\nCIV":"科特迪瓦","\nCMR":"喀麦隆","\nCOD":"刚果民主共和国",' \
                  '"\nCOG":"刚果共和国","\nCOK":"库克群岛","\nCOL":"哥伦比亚","\nCOM":"科摩罗","\nCUB":"古巴","\nCUW":"库拉索",' \
                  '"\nCXR":"圣诞岛","\nCYM":"开曼群岛","\nCYP":"塞浦路斯","\nCZE":"捷克","\nDEU":"德国","\nDJI":"吉布提",' \
                  '"\nDMA":"多米尼克","\nDNK"":"阿尔及利亚","\nECU":"厄瓜多尔","\nEGY":"埃及","\nERI":"厄立特里亚",' \
                  '"\nESH":"西撒哈拉","\nESP":"西班牙","\nEST":"爱沙尼亚","\nETH":"埃塞俄比亚","\nFIN":","\nFRA":"法国",' \
                  '"\nFRO":"法罗群岛","\nFSM":"密克罗尼西亚联邦","\nGAB":"加蓬","\nGBR":"英国","\nGEO":"格鲁吉亚",' \
                  '"\nGGY":"根西","\nGHA":"加纳","\nGIB":"直布瓜德罗普","\nGMB":"冈比亚","\nGNB":"几内亚比绍",' \
                  '"\nGNQ":"赤道几内亚","\nGRC":"希腊","\nGRD":"格林纳达","\nGRL":"格陵兰","\nGTM":"危地马拉",' \
                  '"\nGUF":"法属圭","\nHMD":"赫德岛和麦克唐纳群岛","\nHND":"洪都拉斯","\nHRV":"克罗地亚","\nHTI":"海地",' \
                  '"\nHUN":"匈牙利","\nIDN":"印度尼西亚","\nIMN":"马恩岛","\nIND":"印度","\nIRN":"伊朗","\nIRQ":"伊拉克",' \
                  '"\nISL":"冰岛","\nISR":"以色列","\nITA":"意大利","\nJAM":"牙买加","\nJEY":"泽西","\nJOR":"约旦",' \
                  '"\nJPN":"日本","\nKAZ":"哈萨克吉尔吉斯斯坦","\nKHM":"柬埔寨","\nKIR":"基里巴斯","\nKNA":"圣基茨和尼维斯",' \
                  '"\nKOR":"韩国","\nKWT":"科威特","\nLAO":"老挝","\nLBN":"黎巴嫩","\nLBR":"利比","\nLIE":"列支敦士登",' \
                  '"\nLKA":"斯里兰卡","\nLSO":"莱索托","\nLTU":"立陶宛","\nLUX":"卢森堡","\nLVA":"拉脱维亚",' \
                  '"\nMAF":"法属圣马丁","\nMAR":"摩洛哥","\nMDG":"马达加斯加","\nMDV":"马尔代夫","\nMEX":"墨西哥",' \
                  '"\nMHL":"马绍尔群岛","\nMKD":"北马其顿","\nMLI":"马里","\nMLT":"马耳他","\nMMR":"缅甸","\nMNE":"黑山",' \
                  '"\nMOZ":"莫桑比克","\nMRT":"毛里塔尼亚","\nMSR":"蒙特塞拉特","\nMTQ":"马提尼克","\nMUS":"毛里求斯",' \
                  '"\nMWI":"马拉维","\nMYS":"马来西亚","\nMYT":"马约特","\nNER":"尼日尔","\nNFK":"诺福克岛","\nNGA":"尼日利亚",' \
                  '"\nNIC":"尼加拉瓜","\nNIU":"纽埃","\nNLD":"荷兰","\nNOR":"挪威","\nNPL":"尼泊尔","\nNRU":"瑙鲁",' \
                  '"\nPAK":"巴基斯坦","\nPAN":"巴拿马","\nPCN":"皮特凯恩群岛","\nPER":"秘鲁","\nPHL":"菲律宾","\nPLW":"帕劳",' \
                  '"\nPNG":"巴布亚新几内亚","\nPOL":"波兰","\nPRI":"波多黎各","\nPRY":"巴拉圭","\nPSE":"巴勒斯坦",' \
                  '"\nPYF":"法属波利尼西亚","\nQAT":"卡塔尔","\nREU":"留尼汪","\nROU":"罗马尼亚","\nRUS":"俄罗斯",' \
                  '"\nRWA":"卢旺达","\nSEN":"塞内加尔","\nSGP":"新加坡","\nSGS":"南乔治亚和南桑威奇群岛",' \
                  '"\nSHN":"圣赫勒拿阿森松和特里斯坦","\nSJM":"斯瓦尔巴和扬马延","\nSLB":"所罗门群岛","\nSLE:"索马里",' \
                  '"\nSPM":"圣皮埃尔和密克隆","\nSRB":"塞尔维亚","\nSSD":"南苏丹","\nSTP":"圣多美和普林西比","\nSUR":"苏里南",' \
                  '"\nSVK":"斯洛伐克","\nSVN":"斯洛文尼","\nSYC":"塞舌尔","\nSYR":"叙利亚",' \
                  '"\nTCA":"特克斯和凯科斯群岛","\nTCD":"乍得","\nTGO":"多哥","\nTHA":"泰国","\nTJK":"塔吉克斯坦",' \
                  '"\nTKL":"帝汶","\nTON":"汤加","\nTTO":"特立尼达和多巴哥","\nTUN":"突尼斯","\nTUR":"土耳其","\nTUV":"图瓦卢",' \
                  '"\nTZA":"坦桑尼亚","\nUGA":"乌干达","\nUKR":"乌克兰","\"\nUSA":"美国","\nUZB":"乌兹别克斯坦",' \
                  '"\nVAT":"梵蒂冈","\nVCT":"圣文森特和格林纳丁斯","\nVEN":"委内瑞拉","\nVGB":"英属维尔京群岛",' \
                  '"\nVIR":"美属维尔京群岛,"\nWLF":"瓦利斯和富图纳群岛","\nWSM":"萨摩亚","\nYEM":"也门","\nZAF":"南非","\nZMB":"赞比亚",' \
                  '"\nZWE":"津巴布韦","\nABW":"阿鲁巴"'
    hq = HttpQuery()


    @classmethod
    def parse_region_name(cls):
        region_name_list = cls.region_name.replace('\n', '').replace('"', '').split(',')
        region_name_item = [i.split(":") for i in region_name_list]
        region_name_dict = {item[0]: item[-1] for item in region_name_item}
        region_name_key = [j for j in region_name_dict]
        return region_name_key, region_name_dict

    @classmethod
    def _chain_region_name_list(cls):
        """获取链上已存在的region-name"""
        regin_list = cls.hq.staking.region()
        regin_name_list = [i['name'] for i in regin_list["region"]]
        return regin_name_list

    @classmethod
    def region_name_for_create(cls):
        """创建region-id和region-name(链上不存在的region—name)"""
        region_name_key, _ = cls.parse_region_name()
        while True:
            region_key = random.choice(region_name_key)
            chain_region_name_list = cls._chain_region_name_list()
            if region_key not in chain_region_name_list:
                region_id = region_key.lower()
                return region_key
                # if id_or_name == "id":
                #     return region_id
                # elif id_or_name == "name":
                #     return region_key
                # else:
                #     return region_id,region_key
                # return region_id, region_key
    @classmethod
    def region_for_id_existing(cls):
        "返回链上已经存在的区id"
        region_name_key, _ = cls.parse_region_name()
        while True:
            region_key = random.choice(region_name_key)
            chain_region_name_list = cls._chain_region_name_list()
            region_id = (random.choice(chain_region_name_list)).lower()
            return region_id

class UserInfo:
    # faker = Faker()

    @classmethod
    def random_username(cls):
        random_str = string.ascii_letters + string.digits
        username = "user" + ''.join(random.sample(random_str, 8))
        return username

    # @classmethod
    # def random_username(cls):
    #     """用faker模块写的随机名"""
    #     random_str = string.ascii_letters + string.digits
    #     username = "user" + ''.join(cls.faker.first_name())
    #     return username


class ValidatorInfo:
    node_name = ['node1','node2','node3','node4','node5','node6','node7','node8','node9','node10']
    hq = HttpQuery()

    @classmethod
    def _validator_node_list(cls):
        """返回一个链上存在的node"""
        validator = cls.hq.Staking.validator()
        radom_node = [i['description']['moniker'] for i in validator]
        return radom_node

    @classmethod
    def validator_node_for_kyc(cls,node=None):
        if node is None:
            return random.choice(cls._validator_node_list())
        else:
            return node

    @classmethod
    def validator_node_for_noregion(cls):
        """随机返回一个没有绑定区的节点 node 名称 用于绑定区的"""
        # 把所有区的节点对应的地址拿过来，
        region_addr = (cls.hq.Staking.region()).get("region")
        region_oper_list = [i.get('operator_address') for i in region_addr ]

        # 把所有节点的地址拿过来
        operators_address = cls.hq.staking.validator()

        all_oper_list = [o.get('operator_address') for o in operators_address ]

        # 判断不在区节点地址的节点地址
        no_region_oper_list = [i for i in all_oper_list if i not in region_oper_list]

        # 根据判断的节点地址去它的node名称
        # no_region_node_list = []
        # for i in operators_address:
        #     for n in no_region_oper_list:
        #         if i.get('operator_address') == n:
        #             no_region_node_list.append(i.get('description').get('moniker'))
        # 用推导式的方式写就是下面这样的：
        no_region_node_list = [i.get('description').get('moniker') for i in operators_address if
                               i.get('operator_address') in no_region_oper_list]
        return random.choice(no_region_node_list)


    @classmethod
    def validator_node_for_create(cls,node=None):
        """创建验证者节点的时候传nodename用的，链上不存在的Node"""
        ture_node = cls._validator_node_list()
        # f_node = []
        # for i in cls.node_name:
        #     if i not in ture_node:
        #         f_node.append(i)
        false_node = [i for i in cls.node_name if i not in ture_node]
        if node is None:

            return random.choice(false_node)
        else:
            return node

if __name__ == '__main__':
    # print(UserInfo.random_username())
    # print(RegionInfo.region_name_for_create())
    # print(RegionInfo.region_for_id_existing())
    # print(ValidatorInfo.validator_node_for_noregion())
    # print(ValidatorInfo._validator_node_list())
    # print(ValidatorInfo.validator_node_for_create())
    # print('a')
    print(RegionInfo.region_name_for_create())
    print(UserInfo.random_username())