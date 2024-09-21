from types import SimpleNamespace

from langchain_openai import ChatOpenAI
class LLMOptions:
    def __init__(self ):
        pass
    @staticmethod
    def getClinetByName(name,temperature=0.5):
        if name == 'deepseek':
            client= ChatOpenAI(
                model='deepseek-chat',
                openai_api_key="sk-1e549e9107204045aee4fffa1a2c1e45",
                openai_api_base='https://api.deepseek.com/v1',
                temperature=0.5)
            return client
cfg = SimpleNamespace()
cfg.langchain_key = "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"
cfg.LANGCHAIN_TRACING_V2 = "true"
cfg.project_name =  "graph_test"
cfg.OutputDir = "agentLog"

cfg.STEP_STATE_DIR = "step_states"
cfg.STEP_STATE_JSON_FILE = "step_states.json"

# cfg.ERROR_CALL_BACK = "agent_id_tool.log"

cfg.output_file = "tool_test"
cfg.poi_cache_file = "poi_cache.json"
cfg.origin_poi_file = "origin_poi.json"
cfg.baidu_url = "https://api.map.baidu.com/reverse_geocoding/v3"
cfg.baidu_ak = "tRwY30uG8lXYRkj7ObL3t67lMvRr7Qmq"
# mssage="""\ Model vehicle_routing
# \ LP format - for model browsing. Use MPS format to capture full model detail.
# Minimize
#   3.23 x[0,0] + 0 y[0,0,0]
# Subject To
#  constr1_0: x[0,0] = 1
#  constr2_0: x[0,0] <= 1
# Bounds
# Binaries
#  x[0,0] y[0,0,0]
# End"""
# response = LLMOptions.getClinetByName("deepseek").invoke(mssage)
# print(response.content)