
# read csv has lowest .5 decimal but csv has 7 decimal
import json

import numpy as np
# def dict_to_str(my_dict) -> str:
#     """将字典转换为格式化的JSON字符串
#     """
#     def convert_to_serializable(obj):
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()  # 将ndarray转换为列表
#         raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
#
#     json_str = json.dumps(my_dict, indent=2, default=convert_to_serializable)
#     return json_str
def merge_dicts(dict1, dict2):
    return {**dict1, **dict2}
def exact_pos_resolution(requests_raw):
    pass
# class CompactDictEncoder(json.JSONEncoder):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.indent = 2
#         self.current_indent = 0
#
#     def encode(self, obj):
#         if isinstance(obj, dict):
#             if not obj:
#                 return '{}'
#             self.current_indent += self.indent
#             lines = []
#             for key, value in obj.items():
#                 key_str = json.dumps(key)
#                 value_str = self.encode(value)
#                 lines.append(f"{self.current_indent * ' '}{key_str}: {value_str}")
#             result = '{\n' + ',\n'.join(lines) + '\n'
#             self.current_indent -= self.indent
#             result += self.current_indent * ' ' + '}'
#             return result
#         elif isinstance(obj, (list, tuple)):
#             if len(obj) == 0:
#                 return '[]'
#             elif  all(isinstance(x, (int, float)) for x in obj):
#                 # 对于短的数值列表，保持在一行
#                 return '[' + ', '.join(map(str, obj)) + ']'
#             else:
#                 self.current_indent += self.indent
#                 lines = [self.current_indent * ' ' + self.encode(item) for item in obj]
#                 result = '[\n' + ',\n'.join(lines) + '\n'
#                 self.current_indent -= self.indent
#                 result += self.current_indent * ' ' + ']'
#                 return result
#         elif isinstance(obj, np.ndarray):
#             return self.encode(obj.tolist())
#         return json.dumps(obj)
class CompactDictEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 2
        self.current_indent = 0

    def encode(self, obj):
        if isinstance(obj, dict):
            if not obj:
                return '{}'
            self.current_indent += self.indent
            lines = []
            # 定义键的顺序
            key_order = ['origin', 'destination', 'expected_travel_distance', 'expected_travel_time', 'state', 'distance_to_taxis']
            # 对键进行排序，先排序指定的键，然后是其他键
            sorted_keys = sorted(obj.keys(), key=lambda x: (key_order.index(x) if x in key_order else len(key_order), x))
            for key in sorted_keys:
                value = obj[key]
                key_str = json.dumps(key)
                value_str = self.encode(value)
                lines.append(f"{self.current_indent * ' '}{key_str}: {value_str}")
            result = '{\n' + ',\n'.join(lines) + '\n'
            self.current_indent -= self.indent
            result += self.current_indent * ' ' + '}'
            return result
        elif isinstance(obj, (list, tuple)):
            if len(obj) == 0:
                return '[]'
            elif all(isinstance(x, (int, float)) for x in obj):
                # 对于短的数值列表，保持在一行
                return '[' + ', '.join(map(str, obj)) + ']'
            else:
                self.current_indent += self.indent
                lines = [self.current_indent * ' ' + self.encode(item) for item in obj]
                result = '[\n' + ',\n'.join(lines) + '\n'
                self.current_indent -= self.indent
                result += self.current_indent * ' ' + ']'
                return result
        elif isinstance(obj, np.ndarray):
            return self.encode(obj.tolist())
        elif isinstance(obj, str):
            return json.dumps(obj)
        else:
            return str(obj)
def dict_to_str(my_dict) -> str:
    """将字典转换为格式化的JSON字符串"""
    return json.dumps(my_dict, cls=CompactDictEncoder)
def map_npTuple( original_tuple):
    return tuple(map(float, original_tuple))
def strList2intList( original_list):
    return [ (int(sub[0]),int(sub[1])) for sub in original_list]
# 删除重复的订单 ID
def remove_duplicate_orders(requests_raw):
    duplicates = requests_raw[requests_raw.duplicated(subset='order_id', keep=False)]
    max_order_id = requests_raw['order_id'].max()
    # 遍历重复的订单 ID
    for order_id in duplicates['order_id'].unique():
        same_id_orders = requests_raw[requests_raw['order_id'] == order_id]
    
        # 检查 OD 经纬度 是否相同
        unique_orders = same_id_orders.drop_duplicates(subset=['origin_lat', 'origin_lng', 'dest_lat', 'dest_lng'])
    
        if len(unique_orders) == 1:
            # 如果经纬度相同，保留一条记录，删除其他记录
            requests_raw = requests_raw.drop(same_id_orders.index[1:])
        else:
            # 如果经纬度不同，为重复订单分配新的 order_id
            for i, index in enumerate(same_id_orders.index[1:], start=1):
                max_order_id += 1
                requests_raw.loc[index, 'order_id'] = max_order_id
    # print(len(requests_raw['order_id'].unique()) == len(requests_raw) )
    return requests_raw
