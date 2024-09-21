# u3621353
#Ywh=12171119

# step=6
# step_requests_id = [1,2,3,4,5,6,6,3,12,13,14,15,16]
# duplicated_req_id = []
# for req in step_requests_id:
#     if step_requests_id.count(req) > 1:
#         duplicated_req_id.append(req)
#
# print(f'the duplicated request ids are {duplicated_req_id}')
# #
# LANGCHAIN_TRACING_V2=True
# LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
# LANGCHAIN_API_KEY="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"
# LANGCHAIN_PROJECT="traffic"

import json
from collections import defaultdict
# import torch
#
# # 设置参数
# sequence = 12
# batch = 2
# channel = 3
# ds = 3
#
# # 创建一个示例张量
# x = torch.arange(sequence * batch * channel).reshape(sequence, batch, channel)
#
# # 进行 reshape 操作
# x_reshaped = x.reshape(sequence // ds, ds, batch, channel)
#
# print("Original shape:", x.shape)
# print("Reshaped shape:", x_reshaped.shape)
#
# # 打印原始张量和重塑后的张量
# print("\nOriginal tensor:")
# print(x)
# print("\nReshaped tensor:")
# print(x_reshaped)

import os
import json

class YourClass:
    def __init__(self):
        # 定义项目目录和缓存文件路径
        self.PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的目录
        self.DATA_DIR = os.path.join(self.PROJECT_DIR, '../data/poi')  # 定义数据目录
        self.CACHE_FILE = os.path.join(self.DATA_DIR, 'cache.json')  # 定义缓存文件路径

        # 确保数据目录存在
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)  # 创建数据目录

    def load_cache(self):
        # 检查缓存文件是否存在
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, 'r') as f:
                return json.load(f)
        return {}  # 如果文件不存在，返回空字典

    def save_cache(self, data):
        # 保存数据到缓存文件
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(data, f)

# 使用示例
if __name__ == '__main__':
    your_class_instance = YourClass()
    data = {"key": "valudde"}
    your_class_instance.save_cache(data)

# def extract_poi_info(data):
#     # 解析 JSON 字符串（如果输入是字符串的话）
#     if isinstance(data, str):
#         data = json.loads(data)
#
#     # 提取 pois 列表
#     pois = data['result']['pois']
#
#     # 使用 defaultdict 来组织数据
#     poi_info = defaultdict(lambda: {"num": 0, "names": [], "distance": []})
#
#     # 遍历所有 POI
#     for poi in pois:
#         poi_type = poi['poiType']
#         poi_info[poi_type]["num"] += 1
#         poi_info[poi_type]["names"].append(poi['name'])
#         poi_info[poi_type]["distance"].append(int(poi['distance']))
#
#     # 转换为所需的输出格式
#     result = [
#         {
#             "type": poi_type,
#             "num": info["num"],
#             "names": info["names"],
#             "distance": info["distance"]
#         }
#         for poi_type, info in poi_info.items()
#     ]
#
#     return json.dumps(result, ensure_ascii=False, indent=2)
#
# # 假设您的数据存储在一个名为 'data' 的变量中
# data = {'status': 0, 'result': {'location': {'lng': 104.06708862352096, 'lat': 30.682951440730765}, 'formatted_address': '四川省成都市青羊区北较场西路3号-附1', 'edz': {'name': ''}, 'business': '西体路,新华西路,通锦桥', 'addressComponent': {'country': '中国', 'country_code': 0, 'country_code_iso': 'CHN', 'country_code_iso2': 'CN', 'province': '四川省', 'city': '成都市', 'city_level': 2, 'district': '青羊区', 'town': '草市街街道', 'town_code': '510105002', 'distance': '16', 'direction': '附近', 'adcode': '510105', 'street': '北较场西路', 'street_number': '3号-附1'}, 'pois': [{'addr': '四川省成都市青羊区北较场西路3号', 'cp': ' ', 'direction': '附近', 'distance': '21', 'name': '成都市公安局青羊分局草市街派出所', 'poiType': '政府机构', 'point': {'x': 104.06706737815304, 'y': 30.68311830042448}, 'tag': '政府机构;公检法机构', 'tel': '', 'uid': 'f19372299c3fc020fea778be', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}, {'addr': '通锦桥路65号', 'cp': ' ', 'direction': '东', 'distance': '101', 'name': '锦欣苑', 'poiType': '房地产', 'point': {'x': 104.06623195402877, 'y': 30.683219237431455}, 'tag': '房地产;住宅区', 'tel': '', 'uid': '0971dff9a4898128e6073802', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}, {'addr': '四川省成都市青羊区新华大道通锦桥路65号附1号', 'cp': ' ', 'direction': '东', 'distance': '85', 'name': '白玉兰酒店(通锦桥店)', 'poiType': '酒店', 'point': {'x': 104.06634873374506, 'y': 30.682761137851788}, 'tag': '酒店;其他', 'tel': '', 'uid': 'a00cce0a0848b5da83a00ccb', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}, {'addr': '成都市青羊区北较场西路1号', 'cp': ' ', 'direction': '附近', 'distance': '38', 'name': '青羊区人民政府信访局', 'poiType': '政府机构', 'point': {'x': 104.06674398816945, 'y': 30.68293971930492}, 'tag': '政府机构;行政单位', 'tel': '', 'uid': '083a55fa81c2fd07246e98d6', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}, {'addr': '四川省成都市青羊区北较场西路9号院', 'cp': ' ', 'direction': '南', 'distance': '117', 'name': '北较场西路9号院', 'poiType': '房地产', 'point': {'x': 104.06704042898774, 'y': 30.683863678886855}, 'tag': '房地产;住宅区', 'tel': '', 'uid': '1d2e7352eb6a9096774ff1cf', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}, {'addr': '四川省成都市树德巷1号附1号', 'cp': ' ', 'direction': '东北', 'distance': '134', 'name': '树德园', 'poiType': '房地产', 'point': {'x': 104.06629483541447, 'y': 30.68216327577665}, 'tag': '房地产;住宅区', 'tel': '', 'uid': '606ab0d0b3dc47570f3ddaad', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}, {'addr': '万和路99号丽阳天下商务大厦', 'cp': ' ', 'direction': '北', 'distance': '209', 'name': '7天酒店(成都宽窄巷子文殊院地铁站店)', 'poiType': '酒店', 'point': {'x': 104.06641161513076, 'y': 30.681433413110575}, 'tag': '酒店;快捷酒店', 'tel': '', 'uid': '127bdfab0936ae3bd2f49e62', 'zip': '', 'parent_poi': {'name': '', 'tag': '', 'addr': '', 'point': {'x': 0.0, 'y': 0.0}, 'direction': '', 'distance': '', 'uid': ''}}]}}
#
# # 调用函数并打印结果
# result = extract_poi_info(data)
# print(result)
