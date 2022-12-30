"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2022/12/30 16:18
@Version :  V1.0
@Desc    :  None
"""
import inspect

from loguru import logger

from base.base import BaseClass
from tools import handle_data


class Vault(BaseClass):

    def list_region_vault(self):
        cmd = self.ssh_home + "./srs-poad query srvault list-region-vault --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd)
        return handle_data.handle_yaml_to_dict(res)

    def show_region_vault(self, region_id):
        cmd = self.ssh_home + f"./srs-poad query srvault show-region-vault {region_id} --chain-id srspoa"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        return handle_data.handle_yaml_to_dict(self.ssh_client.ssh(cmd))


if __name__ == '__main__':
    v = Vault()
    # s = v.list_region_vault()
    # print(s)
    # b = v.show_region_vault("ca2ba4fa881611edb29b1e620a42e34a")
    # print(b)


