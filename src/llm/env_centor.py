"""
store the data from the backend, build and cache the information
"""
import json

import numpy as np

import os
from collections import defaultdict
from src.utils.data_process import dict_to_str

class EnvCentor:
    def __init__(self,cfg,logger) -> None:
        self.cfg = cfg
        self.step_states = defaultdict(defaultdict)
        self.graph_data = []
        self.steps_UV_info = defaultdict()
        self.logger = logger
        self.STEP_STATE_JSON_FILE = os.path.join(cfg.STEP_STATE_DIR, cfg.STEP_STATE_JSON_FILE)
        if not os.path.exists(self.cfg.STEP_STATE_DIR):
            os.makedirs(self.cfg.STEP_STATE_DIR)  # 创建数据目录
    def load_cache(self):
        cache = {}
        if os.path.exists(self.STEP_STATE_JSON_FILE):
            with open(self.STEP_STATE_JSON_FILE, 'r') as f:
                cache = json.load(f)
        if not self.step_states:  # 检查是否为空
            for key, value in cache.items():
                self.step_states[int(key)] = value  # 将 cache 中的内容加载到 step_states 中

        return cache

    def save_cache(self, cache):
        with open(self.STEP_STATE_JSON_FILE, 'w') as f:
            json.dump(cache, f,ensure_ascii=False,separators=(',', ':'))

    def store_UV(self,step,Uinfo, Vinfo, U2MultiV, V2MultiU):
        self.step_states[step]["Uinfo"]=Uinfo
        self.step_states[step]["Vinfo"]=Vinfo
        self.step_states[step]["U2MultiV"]=U2MultiV
        self.step_states[step]["V2MultiU"]=V2MultiU
        self.save_cache(self.step_states)
    def store_step_decision(self,step,decision):
        self.step_states[step] = decision
    def present_UV_prompt(self,step,V_space,max_num_vehicles=10):
        step_uv =  self.step_states[step]
        Uinfo = step_uv["Uinfo"]
        Vinfo = step_uv["Vinfo"]
        # shorten the length of the vehicle list
        Vinfo = {k: Vinfo[str(k)] for k in V_space}
        basic_uv_prompt = f"""Now you get the basic information for passenger requests and taxi vehicles, respectively. Their positions are represented as [longitude, latitude].\nThe passenger requests are as follows:
{dict_to_str(Uinfo)}\t,where the key is the `request id`, and its value represents its ideal pickup position and drop-off position.\nThe taxi vehicles are as follows:
{dict_to_str(Vinfo)}\t,where the key is the `taxi id`, and its value represents the taxi's current position and any already assigned passenger on it.
Please refer these information to make a accurate decision.\n"""

        # print(basic_uv_prompt)
        return basic_uv_prompt,Vinfo
    def present_decision_space_prompt(self,step,max_num_vehicles=6):
        step_uv =  self.step_states[step]
        v_in_space = []
        # avaliable_vehicles = list(Vinfo.keys())
        U2MultiV = step_uv["U2MultiV"]
        for u in U2MultiV:
            max_len = len(U2MultiV[u])
            keep_len = min(max_len,max_num_vehicles)
            U2MultiV[u] = [int(v) for v in U2MultiV[u][:keep_len] ]
            v_in_space.extend(U2MultiV[u])
        V2MultiU = step_uv["V2MultiU"]
        decision_space_prompt = \
f"""Now you get the decision space for the current step. The decision space is represented as a dictionary, where the key is the `request id` and the value is a list of `taxi id` that can be assigned to the request.
The decision space for passenger requests is as follows:
{dict_to_str(U2MultiV)}"""
        if len(V2MultiU)<2:
            decision_space_prompt += f"""
The decision space for taxi vehicles is as follows:
{dict_to_str(V2MultiU)}
Please use the appropriate tools to assign each passenger request to a single taxi reasonably.\n"""

        # print(decision_space_prompt)
        return decision_space_prompt, list(set(v_in_space))
    def format_UV_prompt(self, requests, vehicles, num_vehicles=20):
            requests_dict = {}
            for i in range(len(requests)):
                requests_dict[int(requests[i].id)] = {"origin": requests[i].pickup_position,
                                                      "destination": requests[i].dropoff_position}
            vehicles_dict = {}
            for i in range(len(vehicles[:num_vehicles])):
                vehicles_dict[int(vehicles[i].id)] = vehicles[i].current_position
                if i > num_vehicles:
                    break
            UV_loc_string = f"""Now you get the positions for passenger requests and taxi vehicles, respectively. Every position is represented as [longitude, latitude].\nThe passenger requests are as follows:
        {dict_to_str(requests_dict)}\t,where `key` is the `request id`, and `value` represents its ideal pickup position and drop-off position.\nThe taxi vehicles are as follows:
        {dict_to_str(vehicles_dict)}\t,where `key` is the `taxi id`, and `value` represents the current position and assigned requests on this vehicles.
    Please use the appropriate tools to assign each request to a single taxi reasonably.\n"""
            return UV_loc_string


