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
        self.dev = cfg.dev
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
        if self.dev:
            Vinfo = {k: Vinfo[str(k)] for k in V_space}
        basic_uv_prompt = f"""At step {step}, Now you get the basic information for passenger requests and taxi vehicles, respectively. Their positions are represented as [longitude, latitude].\nThe passenger requests are as follows:
{dict_to_str(Uinfo)}\t, where `key` is the `passenger ID`, and `distance_to_taxis` field with 'taxi ID: distance' dict represents the estimated distance to the taxi vehicles in the decision space.\nThe taxi vehicles are as follows:
{dict_to_str(Vinfo)}\t,where the key is the `taxi ID`, and its value represents the taxi's current position and any already assigned passenger on it."""
# Please refer these information to make a accurate decision.\n"""
        # print(basic_uv_prompt)
        return basic_uv_prompt,Vinfo
    def present_decision_space_prompt(self,step,max_num_vehicles=6):
        step_uv =  self.step_states[step]
        v_in_space = []
        # avaliable_vehicles = list(Vinfo.keys())
        U2MultiV = step_uv["U2MultiV"]
        if self.dev:
            for u in U2MultiV:
                max_len = len(U2MultiV[u])
                keep_len = min(max_len,max_num_vehicles)
                U2MultiV[u] = [int(v) for v in U2MultiV[u][:keep_len] ]
                v_in_space.extend(U2MultiV[u])
        V2MultiU = step_uv["V2MultiU"]
        decision_space_prompt = \
f"""For the current step, you get the decision space for taxis, where the key is the `taxi ID` and the value is possibly a list of `passenger ID` scanned by the taxi.
{dict_to_str(V2MultiU)}"""
# Please use the appropriate tools to assign each passenger passenger to a single taxi reasonably.\n"""

        # print(decision_space_prompt)
        return decision_space_prompt, list(set(v_in_space))
    def format_UV_prompt(self, requests, vehicles, num_vehicles=20):
            requests_dict = {}
            for i in range(len(requests)):
                requests_dict[int(requests[i].id)] = {"origin": requests[i].pickup_position,
                                                      "destination": requests[i].dropoff_position}
            vehicles_dict = {}
            if self.dev:
                for i in range(len(vehicles[:num_vehicles])):
                    vehicles_dict[int(vehicles[i].id)] = vehicles[i].current_position
                    if i > num_vehicles:
                        break
            UV_loc_string = f"""Now you get the positions for passenger requests and taxi vehicles, respectively. Every position is represented as [longitude, latitude].\nThe passenger requests are as follows:
        {dict_to_str(requests_dict)}\t,where `key` is the `passenger ID`, and `value` represents its ideal pickup position and drop-off position.\nThe taxi vehicles are as follows:
        {dict_to_str(vehicles_dict)}\t,where `key` is the `taxi ID`, and `value` represents the current position and assigned requests on this vehicles.
    Please use the appropriate tools to assign each passenger to a single taxi reasonably.\n"""
            return UV_loc_string

    def present_helper_prompt(self,helper,help_note=None):
        UV_loc_string = f"""To help you make a decision, the distance information for mentioned locations are as follows:
            {dict_to_str(helper)}\t,where `key` is the `Passenger ID`, and `value` represents its ideal pickup position and drop-off position.\nThe taxi vehicles are as follows:
            {dict_to_str}\t,where `key` is the `taxi ID`, and `value` represents the current position and assigned requests on this vehicles.
        Please use the appropriate tools to assign each passenger to a single taxi reasonably.\n"""
        if help_note is None:
            help_note = f"""The helper function is as follows:"""
        



