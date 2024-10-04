from typing import List

import numpy as np
import requests
import json
BASE_URL = "http://localhost:10086"

def dict_to_str(my_dict) -> str:

        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()  # 将ndarray转换为列表
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        json_str = json.dumps(my_dict, indent=2, default=convert_to_serializable)
        return json_str
def present_UV_prompt(Uinfo, Vinfo,V_space, max_num_vehicles=10):

        # shorten the length of the vehicle list
        Vinfo = {k: Vinfo[str(k)] for k in V_space}
        basic_uv_prompt = f"""Now you get the basic information for passenger requests and taxi vehicles, respectively. Their positions are represented as [longitude, latitude].\nThe passenger requests are as follows:
    {dict_to_str(Uinfo)}\t,where the key is the `request id`, and its value represents its ideal pickup position and drop-off position.\nThe taxi vehicles are as follows:
    {dict_to_str(Vinfo)}\t,where the key is the `taxi id`, and its value represents the taxi's current position and any already assigned passenger on it.
    Please refer these information to make a accurate decision.\n"""

        # print(basic_uv_prompt)
        return basic_uv_prompt, Vinfo

def present_decision_space_prompt( step,U2MultiV,V2MultiU, max_num_vehicles=6):
        v_in_space = []
        # avaliable_vehicles = list(Vinfo.keys())
        for u in U2MultiV:
            max_len = len(U2MultiV[u])
            keep_len = min(max_len, max_num_vehicles)
            U2MultiV[u] = [int(v) for v in U2MultiV[u][:keep_len]]
            v_in_space.extend(U2MultiV[u])
        decision_space_prompt = \
            f"""Now you get the decision space for the current step. The decision space is represented as a dictionary, where the key is the `request id` and the value is a list of `taxi id` that can be assigned to the request.
The decision space for passenger requests is as follows:
{dict_to_str(U2MultiV)}"""
        if len(V2MultiU) < 2:
            decision_space_prompt += f"""
The decision space for taxi vehicles is as follows:
{dict_to_str(V2MultiU)}
Please use the appropriate tools to assign each passenger request to a single taxi reasonably.\n"""

        # print(decision_space_prompt)
        return decision_space_prompt, list(set(v_in_space))
def getDemandNeed():
    response = requests.get(f"{BASE_URL}/getDemandNeed")
    uv_json =   response.json()
    step, Uinfo, Vinfo, U2MultiV, V2MultiU =uv_json["step"], uv_json["Passengers"], uv_json["Taxis"], uv_json["U2MultiV"], uv_json["V2MultiU"]


    decision_space_prompt, V_space = present_decision_space_prompt(step, U2MultiV,V2MultiU, max_num_vehicles=6)
    basic_uv_prompt, Vinfo = present_UV_prompt(Uinfo, Vinfo, V_space,max_num_vehicles=3)
    return basic_uv_prompt, decision_space_prompt
# print(getDemandNeed())
def implement_action(decision: List[tuple[int,int]]):
    action = {"decisions": decision}
    response = requests.post(f"{BASE_URL}/implementDecision", json=action)
    return response.json()