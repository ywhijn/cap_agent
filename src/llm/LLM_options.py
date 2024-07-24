from langchain_openai import ChatOpenAI
class LLMOptions:
    def __init__(self ):
        pass
    @staticmethod
    def getClinetByName(name,temperature=0.5):
        if name == 'deepseek':
            client= ChatOpenAI(
                model='deepseek-chat',
                openai_api_key="sk-ab9ba3f8d082420fa61ab453c14d6477",
                openai_api_base='https://api.deepseek.com/v1',
                temperature=0.85)
            return client
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