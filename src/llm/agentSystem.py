'''
@Author: WANG Maonan
@Date: 2023-12-01 22:59:52
@Description: 结合 RL+LLM 的方式来进行决策, 调用工具
运行 script 3way_agent.log 可以开始记录日志, 将所有输出的终端上面的内容都保存下来
运行 exit 可以推出日志的记录

@3way
-> python llm_rl.py --env_name '3way' --phase_num 3 --edge_block 'E1' --detector_break 'E0--s'

@4way
-> python llm_rl.py --env_name '4way' --phase_num 4 --edge_block 'E1' --detector_break 'E2--s'
@LastEditTime: 2024-01-06 20:45:24
'''
import argparse
import langchain
import numpy as np

from langchain.chat_models import ChatOpenAI

# from tshub.utils.get_abs_path import get_abs_path
# from tshub.utils.init_log import set_logger
from .Agent import TaxiAgent
from .output_parse import OutputParse
from .LLM_options import LLMOptions
from .custom_tools import dict_to_str
from .custom_tools import (
    GetDistancTime
    # GetAvailableActions,
    # GetCurrentOccupancy,
    # GetPreviousOccupancy,
    #
    # GetIntersectionLayout,
    # GetSignalPhaseStructure,
    # GetTraditionalDecision,
    # GetJunctionSituation
)
from ..utils.readConfig import read_config

langchain.debug = False  # 开启详细的显示


class AgentSystem:
    def __init__(self,cfg, env):

        self.tsc_scenario = env
        self.cfg = cfg

        self.tools = [
            GetDistancTime(env=env),
        ]

        self.chat = LLMOptions.getClinetByName("deepseek",temperature=0.5)
        self.o_parse = OutputParse(env=None, llm=self.chat)
        self.agent = None
    def initialize(self):
        self.agent = TaxiAgent(env=self.tsc_scenario, llm=self.chat, tools=self.tools, verbose=True)

    # req_dict={requests[i].id: {"origin":requests[i].pickup_position,"destination":requests[i].dropoff_position}}         previous_occupancy = self.tsc_scenario.getUV_loc()
    def getUV_loc_Prompt(self,requests,vehicles,num_vehicles=20):
        requests_dict = {}
        for i in range(len(requests)):
            requests_dict[int(requests[i].id)] = {"origin":requests[i].pickup_position,"destination":requests[i].dropoff_position}
        vehicles_dict = {}
        for i in range(len(vehicles[:num_vehicles])):
            vehicles_dict[int(vehicles[i].id)]=vehicles[i].current_position
            if i > num_vehicles:
                break
        UV_loc_string = f"""Now you get the two position dicts for passenger requests and taxi vehicles, respectively. Every position is represented as [longitude, latitude].\nThe passenger requests are as follows:
{dict_to_str(requests_dict)}\t,where `key` is the `request id`, and `value` represents its ideal pickup position and drop-off position dict.\nThe taxi vehicles are as follows:
{dict_to_str(vehicles_dict)}\t,where `key` is the `taxi id`, and `value` represents the current position of the vehicle.
Please use the appropriate tools to assign each request to a single taxi reasonably.\n"""
        return UV_loc_string
    def parse_output(self,output):
        return self.o_parse.parser_output(output)










