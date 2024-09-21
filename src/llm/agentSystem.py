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
from src.test_env_api import getDemandNeed,implement_action,reset_env
from langchain.chat_models import ChatOpenAI

# from tshub.utils.get_abs_path import get_abs_path
# from tshub.utils.init_log import set_logger
from src.llm.Agent import TaxiAgent,CompilerAgent
from src.llm.output_parse import OutputParse
from src.llm.LLM_options import LLMOptions
from src.llm.custom_tools import dict_to_str
from src.llm.env_centor import EnvCentor
from src.llm.graph_construct import construct_simpleTool
from langchain_core.messages import AIMessage,ToolMessage
from src.llm.tools.tools import GetDistanceTimeByID,POIbyLocation,GetDistanceTimeByPos,GetDistanceTimeByPos_Debug
from src.llm.tools.tools import get_distance_time_between_positions
from src import test_env_api
from langgraph.prebuilt import ToolNode
import os
langchain.debug = False  # 开启详细的显示
from src.llm.test_case.data import *
# from langsmith.wrappers import wrap_openai
import logging
from langchain_core.tools import tool
from datetime import datetime
class AgentSystem:
    def __init__(self,cfg, env):

        self.env = env
        self.cfg = cfg
        os.environ["LANGCHAIN_TRACING_V2"] = cfg.LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_PROJECT"] = cfg.project_name
        os.environ["LANGCHAIN_API_KEY"] = cfg.langchain_key
        self.tools = [
            GetDistanceTimeByID(env=env),
            POIbyLocation(env=env,cfg=cfg)
        ]

        self.complex_tools = [
            GetDistanceTimeByPos(env=env),
            POIbyLocation(env=env,cfg=cfg)
        ]

        self.chat = LLMOptions.getClinetByName("deepseek",temperature=0.5)
        # self.chat=wrap_openai(self.chat)
        self.o_parse = OutputParse(env=None, llm=self.chat)
        self.agent = None

        self.logger = None # self.initilize_logging(self.cfg)
        self.env = EnvCentor(cfg=cfg, logger=self.logger)

    def initilize_logging(self, cfg):
        logger = logging.getLogger('')
        if not os.path.exists(cfg.OutputDir):
            os.makedirs(cfg.OutputDir)
        file_name_time = f"{cfg.output_file}_{datetime.now().strftime('%m-%d-%H-%M')}.log"
        filehandler = logging.FileHandler(os.path.join(cfg.OutputDir, file_name_time))
        streamhandler = logging.StreamHandler()
        logger.setLevel(logging.WARNING)
        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)
    def initialize_agent(self,name="taxi"):
        if name=="taxi":
            self.agent = TaxiAgent(env=self.env, llm=self.chat, tools=self.complex_tools, cfg=self.cfg, verbose=True)
        elif name=="compiler":
            self.agent = CompilerAgent(env=self.env, llm=self.chat, tools=self.tools, verbose=True)
        return self.agent
    # req_dict={requests[i].id: {"origin":requests[i].pickup_position,"destination":requests[i].dropoff_position}}         previous_occupancy = self.env.getUV_loc()
    def getUV_loc_prompt(self,requests,vehicles,num_vehicles=20):
        requests_dict = {}
        for i in range(len(requests)):
            requests_dict[int(requests[i].id)] = {"origin":requests[i].pickup_position,"destination":requests[i].dropoff_position}
        vehicles_dict = {}
        for i in range(len(vehicles[:num_vehicles])):
            vehicles_dict[int(vehicles[i].id)]=vehicles[i].current_position
            if i > num_vehicles:
                break
        UV_loc_string = f"""Now you get the positions for passenger requests and taxi vehicles, respectively. Every position is represented as [longitude, latitude].\nThe passenger requests are as follows:
{dict_to_str(requests_dict)}\t,where `key` is the `request id`, and `value` represents its ideal pickup position and drop-off position.\nThe taxi vehicles are as follows:
{dict_to_str(vehicles_dict)}\t,where `key` is the `taxi id`, and `value` represents the current position of the vehicle.
Please use the appropriate tools to assign each request to a single taxi reasonably.\n"""
        return UV_loc_string
    def parse_output(self,output):
        return self.o_parse.parser_output(output)

    def test_agent(self):
        from langchain_core.messages import HumanMessage
        app = construct_simpleTool(self.env,self.chat)
        test_masg = "The location of passenger 1 is [104.0412682, 30.6669185]. Given place 3 [104.0562247, 30.6223237] and place 4 [104.0566995, 30.6722262],  please select the closest place to the passenger 1."
        inputs = {"messages": [HumanMessage(content=test_masg)]}
        # final_state = app.invoke(inputs)
        for output in app.stream(inputs, stream_mode="values"):
            last_msg = output["messages"][-1]

            last_msg.pretty_print()
            print("\n---\n")
        # print(f'final state, {final_state}')
        # agent_response=self.agent.agent_run(UV_loc_string)
        # agent_response = self.agent.agent_executor.invoke({"input":UV_loc_string})
        # print(f'agent response Output, {agent_response}')

        # agent_action = self.agent.parse_output(agent_response)
        # print(f'parsed response Output, {agent_action}')
        # return agent_action

    def trytools(self):

        self.env.load_cache()
        step = 1
        present_decision_space_prompt, V_space = self.env.present_decision_space_prompt(step, max_num_vehicles=3)
        basic_uv_prompt, Vinfo = self.env.present_UV_prompt(step, V_space, max_num_vehicles=1)
        get_distance_time_tool = GetDistanceTimeByPos_Debug()
        custom_message = agent.input_format(basic_uv_prompt, present_decision_space_prompt)
        tools=[get_distance_time_tool]
        tools = [get_distance_time_between_positions]
        tool_node = ToolNode(tools)
        BASE_URL = "http://localhost:10086"
        test_masg = "The location of passenger 1 is [104.0412682, 30.6669185], and I want to how long can he arrive at place 3 [104.0562247, 30.6223237], place 4 [104.0566995, 30.6722262]? Please select the closest one to the passenger 1."
        model_with_tools = self.chat.bind_tools(tools)

        # gene_took_ars=model_with_tools.invoke(test_masg).tool_calls
        func_took_args=[{'name': 'get_distance_time_between_positions', 'args': {'origin': [104.0412682, 30.6669185], 'destination': [104.0562247, 30.6223237]}, 'id': 'call_0_ae66067f-91e7-4a82-a6cd-75d69babbb94', 'type': 'tool_call'},
                        {'name': 'get_distance_time_between_positions', 'args': {'origin': [104.0412682, 30.6669185], 'destination': [104.0566995, 30.6722262]}, 'id': 'call_1_9c1c3e36-3bae-4690-8606-8184d20a26b7', 'type': 'tool_call'}]
        cls_took_ars=[{'name': 'get_distance_time_between_positions', 'args': {'origin': {'lng': 104.0412682, 'lat': 30.6669185}, 'destination': {'lng': 104.0562247, 'lat': 30.6223237}}, 'id': 'call_0_30cf2e36-207d-458f-aabf-b1ac44c8429f', 'type': 'tool_call'},
                  {'name': 'get_distance_time_between_positions', 'args': {'origin': {'lng': 104.0412682, 'lat': 30.6669185}, 'destination': {'lng': 104.0566995, 'lat': 30.6722262}}, 'id': 'call_1_25ec7533-0839-40e9-899a-cdd3400c3eb8', 'type': 'tool_call'}]
        tool_calls = AIMessage(
            content="",
            tool_calls=func_took_args
        )
        # pres = tool_node.invoke({"messages": [model_with_tools.invoke(test_masg)]})
        pres = tool_node.invoke({"messages":[tool_calls]})

        fun_tool_out={'messages': [ToolMessage(content='{"Distance": 5160.1, "Time": 344.01}', name='get_distance_time_between_positions', tool_call_id='call_0_ae66067f-91e7-4a82-a6cd-75d69babbb94'),
                                   ToolMessage(content='{"Distance": 1589.92, "Time": 105.99}', name='get_distance_time_between_positions', tool_call_id='call_1_9c1c3e36-3bae-4690-8606-8184d20a26b7')]}
        cls_tool_out={'messages': [ToolMessage(content='The distance and travel time between two points: Distance: 5160.1, Time: 344.01', name='get_distance_time_between_positions', tool_call_id='call_0_30cf2e36-207d-458f-aabf-b1ac44c8429f'),
                             ToolMessage(content='The distance and travel time between two points: Distance: 1589.92, Time: 105.99', name='get_distance_time_between_positions', tool_call_id='call_1_25ec7533-0839-40e9-899a-cdd3400c3eb8')]}

    def parallel_test(self):

        @tool
        def get_weather(location: str):
            """Call to get the current weather."""
            if location.lower() in ["sf", "san francisco"]:
                return "It's 60 degrees and foggy."
            else:
                return "It's 90 degrees and sunny."

        @tool
        def get_coolest_cities():
            """Get a list of coolest cities"""
            return "nyc, sf"

        tools = [get_weather, get_coolest_cities]
        tool_node = ToolNode(tools)

        message_with_single_tool_call = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "get_weather",
                    "args": {"location": "sf"},
                    "id": "tool_call_id",
                    "type": "tool_call",
                }
            ],
        )

        print(tool_node.invoke({"messages": [message_with_single_tool_call]}))


        model_with_tools = self.chat.bind_tools(tools)
        toolargs= model_with_tools.invoke("what's the weather in sf?").tool_calls
        print(toolargs)
        msg= tool_node.invoke({"messages": [model_with_tools.invoke("what's the weather in francisco?")]})
        print(msg)


# def test_random_multi():
#     for i in range(300):
#         uv_json = getDemandNeed()
#
#         Uinfo, Vinfo, U2MultiV, V2MultiU = uv_json["Passengers"], uv_json["Taxis"], uv_json["U2MultiV"],uv_json["V2MultiU"]
#         pairs = []
#         for  u_id, v_ids in U2MultiV.items():
#             pair = decide_multiV_singleU(u_id, v_ids)
#             pairs.append(pair)
#
#         implement_action(pairs)

if __name__ == "__main__":

    #

    system = AgentSystem(cfg=cfg,env=None)

    agent = system.initialize_agent(name="taxi")
    system.test_agent()
    # # a=agentsystem.initialize_agent(name="compiler")
    # # a.test_multi_hop(a.graph)
    #
    # for i in range(2):
    #     uv_json = getDemandNeed()
    #     step, Uinfo, Vinfo, U2MultiV, V2MultiU =uv_json["step"], uv_json["Passengers"], uv_json["Taxis"], uv_json["U2MultiV"], uv_json["V2MultiU"]
    #     system.env.store_UV(step, Uinfo, Vinfo, U2MultiV, V2MultiU)
    #
    #
    #     present_decision_space_prompt,V_space = system.env.present_decision_space_prompt(step,max_num_vehicles=6)
    #     basic_uv_prompt, Vinfo = system.env.present_UV_prompt(step, V_space,max_num_vehicles=3)
    #     # construct the basic info from the backend
    #
    #     res= agent.agent_run(basic_uv_prompt, present_decision_space_prompt)
    #
    #     implement_action(res)
        # a
        # pairs = []
        # for u_id, v_ids in U2MultiV.items():
        #     pair = decide_multiV_singleU(u_id, v_ids)
        #     pairs.append(pair)

    # POIbyLocation(env=None,cfg = cfg).test_usage()
















