"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 10:38
@Version :  V1.0
@Desc    :  None
"""
from base.base import BaseClass
from tools import handle_data


class Tx(BaseClass):

    def query_tx(self, tx_hash):
        """查询 tx_hash """
        cmd = self.ssh_home + f"./srs-poad query tx {tx_hash}"
        res = self.ssh_client.ssh(cmd)
        return handle_data.handle_yaml_to_dict(res)


if __name__ == '__main__':
    obj = Tx()
    a = obj.query_tx("63E04D681AD4ECA1F8034450B1562294167528669F8FF1A6BD1345E1CF31C547")
    print(a)
