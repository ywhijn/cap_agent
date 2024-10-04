from langchain.tools import BaseTool,tool
from typing import Optional, Type,Any,Tuple,List,Dict
# from pydantic import BaseModel, Field
from langchain_core.pydantic_v1 import BaseModel, Field
BASE_URL = "http://localhost:10086"
import requests
import json
import os
from collections import defaultdict
class Position(BaseModel):
    lng: float = Field(..., description="Longitude")
    lat: float = Field(..., description="Latitude")
@tool
def get_distance_time_between_positions(origin: tuple[float,float], destination: tuple[float,float]) -> Dict[str, float]:
    "Get the distance and travel time between two positions using corresponding (longitude, latitude) tuples"
    print("function", origin, destination)
    origin_tuple = tuple(origin)
    destination_tuple = tuple(destination)


    res_json = get_dt_w2_loc(origin_tuple, destination_tuple)
    dis, time = res_json['Distance'], res_json['Time']
    tool_res = {"Distance": dis, "Time": time}
    round_digit = 2
    distance_time = f"The distance and travel time between two points: Distance: {round(dis, round_digit)}, Time: {round(time, round_digit)}"
    return tool_res
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
