from langchain.tools import BaseTool,tool
from typing import Optional, Type,Any,Tuple,List,Dict
# from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
import json
#
# class GetDistanceTimeInput(BaseModel):
#     origin: tuple = Field(..., description="Origin coordinates as a tuple (x, y)")
#     destination: tuple = Field(..., description="Destination coordinates as a tuple (x, y)")
#     type: # str = Field(default="Linear", description="Type of distance calculation")
#     congestion_factor: float = Field(default=1.0, description="Congestion factor")
#
# class GetDistanceTimeTool(BaseTool):
#     name = "get_distance_time"
#     description = "Get the distance and travel time between two points"
#     args_schema: Type[BaseModel] = GetDistanceTimeInput
#
#     def __init__(self, env):
#         super().__init__()
#         self.env = env
#
#     def _run(self, origin: tuple, destination: tuple, type: str = "Linear", congestion_factor: float = 1.0):
#         dis, time = self.env.GetDistanceandTime(origin, destination, type)
#         return f"Distance: {dis}, Time: {time}"
#
#     def _arun(self, origin: tuple, destination: tuple, type: str = "Linear", congestion_factor: float = 1.0):
#         raise NotImplementedError("This tool does not support async")
#
# # Usage example
# class Environment:
#     def GetDistanceandTime(self, origin, destination, type):
#         # Simulated implementation
#         return 10, 20
#
# env = Environment()
# get_distance_time_tool = GetDistanceTimeTool(env)
#
# # Now you can use this tool with LangChain
# from langchain.llms import OpenAI
# from langchain.agents import initialize_agent, AgentType
#
# llm = OpenAI(temperature=0)
# tools = [get_distance_time_tool]
#
# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True
# )
#
# # Example usage
# result = agent.run("What's the distance and time between (0,0) and (3,4)?")
# print(result)
BASE_URL = "http://localhost:10086"
import requests
import json
import os
from collections import defaultdict
def get_dt_w2_loc(origin: tuple[float,float], destination: tuple[float,float]) -> Dict[str, float]:
    BASE_URL = "http://localhost:10086"
    data = {
        "origin": origin,
        "destination": destination
    }
    response = requests.post(f"{BASE_URL}/get_dt_w2_loc", json=data)
    return response.json()


def extract_poi_info(result_pois):
    # 解析 JSON 字符串（如果输入是字符串的话）
    if isinstance(result_pois, str):
        data = json.loads(result_pois)
        result_pois = data['result']['pois']

    # 提取 pois 列表
    pois = result_pois

    # 按距离排序
    sorted_pois = sorted(pois, key=lambda x: int(x['distance']))
    poi_len = 6 if  len(sorted_pois) > 6 else len(sorted_pois)
    # 选择前5个POI
    selected_pois = sorted_pois[:poi_len]

    # 检查是否包含房地产POI
    has_real_estate = any(poi['poiType'] == '房地产' for poi in selected_pois)

    # 如果前5个中没有房地产POI，添加最近的一个
    if not has_real_estate:
        real_estate_poi = next((poi for poi in sorted_pois[poi_len-1:] if poi['poiType'] == '房地产'), None)
        if real_estate_poi:
            selected_pois.append(real_estate_poi)
    # 使用 defaultdict 来组织数据
    poi_info = defaultdict(lambda: {"num": 0, "names": [], "distance": []})

    for poi in selected_pois:
        poi_type = poi['poiType']
        poi_info[poi_type]["num"] += 1
        # poi_info[poi_type]["names"].append(poi['name'])
        poi_info[poi_type]["distance"].append(int(poi['distance']))
    result = [
        {
            "type": poi_type,
            "num": info["num"],
            "distance": info["distance"]
        }
        for poi_type, info in poi_info.items()
    ]
    return json.dumps(result, ensure_ascii=False, indent=2)
# 缓存文件路径
class Position(BaseModel):
    lng: float = Field(..., description="Longitude")
    lat: float = Field(..., description="Latitude")

class POIbyLocation(BaseTool):
    name: str = "get_pois_by_location"
    description: str = "Get the POIs and semantic description of a location based on latitude and longitude."
    env: Any = None
    cfg: Any = None
    def __init__(self, env: Any, cfg: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.env= env
        self.cfg = cfg
        self.init_cache(cfg)
    def _run(self, lng: float, lat: float) -> str:
        """
        Get the POIs and semantic description of a location

        Args:
            lng (float): Longitude
            lat (float): Latitude

        Returns:
            str: JSON string containing POIs
        """
        cache,origin_cache = self.load_cache()
        key = f"{lat},{lng}"

        if key in cache:
            print("Using cached data")
            print(cache[key])
            return json.dumps(cache[key],ensure_ascii=False)

        print("Fetching new data from API")
        params = {
            "ak": self.cfg.baidu_ak,
            "output": "json",
            "coordtype": "wgs84ll",
            "extensions_poi": "1",
            "location": key
        }
        # extensions_poi = 0，不召回pois数据。
#       # extensions_poi = 1，返回pois数据（默认显示周边1000米内的poi），并返回sematic_description语义化数据。
        response = requests.get(url=self.cfg.baidu_url, params=params)
        res = response.json()

        if 'result' in res and 'pois' in res['result'] and 'sematic_description' in res['result']:
            cache_data = {
                'pois': res['result']['pois'],
                'sematic_description': res['result']['sematic_description']
            }
            fined_poi = extract_poi_info(res['result']['pois'])
            cache[key] = fined_poi
            origin_cache[key] = cache_data
            self.save_cache(cache,origin_cache)

            return json.dumps(cache_data,ensure_ascii=False)
        else:
            return json.dumps(res,ensure_ascii=False)  # 返回原始响应，以防API返回错误或意外格式
    def init_cache(self,cfg):
        self.cfg.PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的目录
        self.cfg.DATA_DIR = os.path.join(self.cfg.PROJECT_DIR, '../data/poi')  # 定义数据目录
        self.cfg.CACHE_FILE = os.path.join(self.cfg.DATA_DIR, cfg.poi_cache_file)  # 定义缓存文件路径
        self.cfg.ORIGIN_CACHE_FILE = os.path.join(self.cfg.DATA_DIR, cfg.origin_poi_file)  # 定义原始缓存文件路径

        # 确保数据目录存在
        if not os.path.exists(self.cfg.DATA_DIR):
            os.makedirs(self.cfg.DATA_DIR)  # 创建数据目录
    async def _arun(self, lng: float, lat: float) -> str:
        """Asynchronous version of _run"""
        # 如果需要异步操作，可以在这里实现
        # 目前，我们只是调用同步版本
        return self._run(lng, lat)

    def load_cache(self):
        origin_cache = {}
        cache = {}
        if os.path.exists(self.cfg.CACHE_FILE):
            with open(self.cfg.CACHE_FILE, 'r') as f:
                cache = json.load(f)
        if os.path.exists(self.cfg.ORIGIN_CACHE_FILE):
            with open(self.cfg.ORIGIN_CACHE_FILE, 'r') as f:
                origin_cache = json.load(f)
        return cache,origin_cache

    def save_cache(self, cache,origin_cache):
        with open(self.cfg.CACHE_FILE, 'w') as f:
            json.dump(cache, f,ensure_ascii=False,separators=(',', ':'))
        with open(self.cfg.ORIGIN_CACHE_FILE, 'w') as f:
            json.dump(origin_cache, f,ensure_ascii=False,separators=(',', ':'))

    def test_usage(self):
        return self._run(104.0581489, 30.6792291)


class UV_ID_pair(BaseModel):
    request_id: int = Field(..., description="The ID of the request")
    driver_id: int = Field(..., description="The ID of the driver")

# class GetDistanceTimeByID(BaseTool):
#     name = "get_distance_time_by_id"
#     description = "Get the distance and travel time between a request's position and a driver's position using their IDs"
#     args_schema: Type[BaseModel] = UV_ID_pair
#
#     env: Any
#     request_dict: Dict[int, list] = {78942: [104.0412682, 30.6669185], 81088: [104.0562247, 30.6223237]}
#     driver_dict: Dict[int, list] = {17: [104.0581489, 30.6792291], 12: [104.0566995, 30.6722262],
#                                     33: [104.0485007, 30.6620189]}
#
#     def __init__(self, env: Any, **kwargs: Any) -> None:
#         super().__init__(**kwargs)
#         self.env = env
#     def get_dt_w2_loc(self,origin, destination):
#         data = {
#             "origin": origin,
#             "destination": destination
#         }
#         response = requests.post(f"{BASE_URL}/get_dt_w2_loc", json=data)
#         return response.json()
#
#     def _run(self, request_id: int, driver_id: int) -> str:
#         """
#         Get the distance and travel time between a request's position and a driver's position.
#
#         Args:
#             request_id (int): The ID of the request
#             driver_id (int): The ID of the driver
#
#         Returns:
#             str: A string describing the distance and travel time
#         """
#         try:
#             request_id = int(request_id)
#             driver_id = int(driver_id)
#         except ValueError:
#             return "Invalid input. Both request_id and driver_id must be integers."
#
#         if request_id not in self.request_dict or driver_id not in self.driver_dict:
#             print("The request ID or driver ID is not valid.")
#             request_id = 78942
#             driver_id = 17
#
#         origin = tuple(self.request_dict[request_id])
#         destination = tuple(self.driver_dict[driver_id])
#         if self.env==None:
#             res_json = self.get_dt_w2_loc(origin, destination)
#             dis = res_json['Distance']
#             time = res_json['Time']
#         else:
#             dis, time = self.env.GetDistanceandTime(origin, destination, type='Linear')
#         round_digit = 2
#         distance_time = f"The distance and travel time between two points: Distance: {round(dis, round_digit)}, Time: {round(time, round_digit)}"
#         return distance_time
#
#     def __call__(self, request_id: int, driver_id: int) -> str:
#         """
#         This method allows the tool to be called with keyword arguments.
#         """
#         return self._run(request_id, driver_id)
#     def test_usage(self):
#         return self._run(78942, 17)
#
# class Position(BaseModel):
#     lng: float = Field(..., description="Longitude")
#     lat: float = Field(..., description="Latitude")
# class PositionPair(BaseModel):
#     origin: Position = Field(..., description="Origin position")
#     destination: Position = Field(..., description="Destination position")
# class GetDistanceTimeByPos(BaseTool):
#     name = "get_distance_time_between_positions"
#     description = "Get the distance and travel time between two positions using their (longitude, latitude) pairs"
#     args_schema: Type[BaseModel] = PositionPair
#     env: Any
#     def __init__(self, env: Any = None, **kwargs: Any) -> None:
#         super().__init__(**kwargs)
#         self.env = env
#
#     def __call__(self,tool_input: Dict[str, Any], **kwargs: Any) -> str:
#         """
#         This method allows the tool to be called with a dictionary input.
#         """
#         print(tool_input)
#         position_pair = PositionPair(**tool_input)
#         return self._run(position_pair.origin, position_pair.destination)
#
#     def get_dt_w2_loc(self, origin: tuple, destination: tuple) -> Dict[str, float]:
#         data = {
#             "origin": origin,
#             "destination": destination
#         }
#         response = requests.post(f"{BASE_URL}/get_dt_w2_loc", json=data)
#         return response.json()
#
#     def _run(self, origin: Position, destination: Position) -> str:
#         """
#         Get the distance and travel time between any two positions represented by (longitude, latitude) with decimal 7.
#
#         Args:
#             origin (Position): Origin position (lng, lat)
#             destination (Position): Destination position (lng, lat)
#
#         Returns:
#             str: A string describing the distance and travel time
#         """
#         print(origin, destination)
#         origin_tuple = (float(origin.lng), float(origin.lat))
#         destination_tuple = (float(destination.lng), float(destination.lat))
#
#         if self.env is None:
#             res_json = self.get_dt_w2_loc(origin_tuple, destination_tuple)
#             dis = res_json['Distance']
#             time = res_json['Time']
#         else:
#             dis, time = self.env.GetDistanceandTime(origin_tuple, destination_tuple, type='Linear')
#
#         round_digit = 2
#         distance_time = f"The distance and travel time between two points: Distance: {round(dis, round_digit)}, Time: {round(time, round_digit)}"
#         return distance_time
#
#     def _arun(self, origin: Position, destination: Position) -> str:
#         """Asynchronous version of _run"""
#         # 如果需要异步操作，可以在这里实现
#         raise NotImplementedError("Asynchronous operation not supported")
# class GetDistanceTimeByPos_Debug(BaseTool):
#     name = "get_distance_time_between_positions"
#     description = "Get the distance and travel time between two positions using their (longitude, latitude) pairs"
#     args_schema: Type[BaseModel] = PositionPair
#     env: Any
#     def __init__(self, env: Any = None, **kwargs: Any) -> None:
#         super().__init__(**kwargs)
#         self.env = env
#
#     # def __call__(self,tool_input: Dict[str, Any], **kwargs: Any) -> str:
#     #     """
#     #     This method allows the tool to be called with a dictionary input.
#     #     """
#     #     print("__call__", tool_input)
#     #     position_pair = PositionPair(**tool_input)
#     #     return self._run(position_pair.origin, position_pair.destination)
#     def _run(self, origin: Position, destination: Position) -> str: # go here
#         """
#         Get the distance and travel time between any two positions represented by (longitude, latitude) with decimal 7.
#
#         Args:
#             origin (Position): Origin position (lng, lat)
#             destination (Position): Destination position (lng, lat)
#
#         Returns:
#             str: A string describing the distance and travel time
#         """
#         print("_run",origin, destination)
#         origin_tuple = (float(origin.lng), float(origin.lat))
#         destination_tuple = (float(destination.lng), float(destination.lat))
#
#         if self.env is None:
#             res_json = get_dt_w2_loc(origin_tuple, destination_tuple)
#             dis = res_json['Distance']
#             time = res_json['Time']
#         else:
#             dis, time = self.env.GetDistanceandTime(origin_tuple, destination_tuple, type='Linear')
#
#         round_digit = 2
#         distance_time = f"The distance and travel time between two points: Distance: {round(dis, round_digit)}, Time: {round(time, round_digit)}"
#         return distance_time
#         # return f"Distance: 100km, Time: 2 hours"
