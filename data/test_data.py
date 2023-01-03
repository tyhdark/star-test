"""
@Author  :  Jw
@Contact :  libai7236@gmail.com
@Time    :  2023/1/3 13:57
@Version :  V1.0
@Desc    :  None
"""
import random
import string
import uuid


def create_region_id_and_name():
    _region_id = uuid.uuid1().hex
    _region_name = f"regionName-{_region_id}"

    return _region_id, _region_name


def random_username():
    username = "user-" + ''.join(random.sample(string.printable, 12))
    return username
