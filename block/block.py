"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/1/3 16:59
@Version :  V1.0
@Desc    :  None
"""

import inspect

from loguru import logger

from base.base import BaseClass
from tools import handle_resp_data


class Block(BaseClass):

    def query_block(self, height=""):
        cmd = self.ssh_home + f"./srs-poad query block {height}"
        logger.info(f"{inspect.stack()[0][3]}: {cmd}")
        res = self.ssh_client.ssh(cmd)
        if height:
            return handle_resp_data.handle_yaml_to_dict(res)
        else:
            resp = handle_resp_data.handle_yaml_to_dict(res)
            block_height = resp['block']['header']['height']
            return block_height


if __name__ == '__main__':
    block = Block()
    r = block.query_block()
    print(r)
