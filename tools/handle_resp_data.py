import yaml


def handle_split_esc(data: str):
    """切割控制台esc数据"""
    data_info = data.split("")
    _value = data_info[0]
    return yaml.load(_value, Loader=yaml.FullLoader)


def handle_split_esc_re_code(data: str):
    """切割控制台esc数据 并按code 匹配"""
    data_info = data.split("")
    _value = data_info[1]
    value = 'code:' + _value.split('\rcode:')[-1]
    return yaml.load(value, Loader=yaml.FullLoader)


def handle_input_y_split_esc_re_code(data: str):
    """input_y 后切割控制台esc数据 并按code 匹配"""
    data_info = data.split("")
    # 使用 'code:' 作为分割符查找数据源
    _value_list = ['code:' + i.split('\r\ncode:')[-1] for i in data_info if 'code:' in i]
    if len(_value_list) == 1:
        return yaml.load(_value_list[0], Loader=yaml.FullLoader)
    else:
        return _value_list


def handle_yaml_to_dict(yaml_path: str, is_file=False):
    """处理dict 格式数据"""
    if is_file:
        with open(yaml_path) as file:
            dict_value = yaml.load(file.read(), Loader=yaml.FullLoader)
    else:
        dict_value = yaml.load(yaml_path, Loader=yaml.FullLoader)
    return dict_value


class HandleRespErrorInfo:
    rpc_error = "Error: rpc error"

    @classmethod
    def handle_rpc_error(cls, message):
        if cls.rpc_error in message:
            error_info = message.split('Usage')[0]
            return error_info
        else:
            return message
