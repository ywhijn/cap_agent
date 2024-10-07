from src.llm.tools.tools import  get_distance_time_between_positions
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
from src.llm.Agent import DecisionPair
from langgraph.graph import StateGraph, MessagesState, START,END
import operator
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Annotated, Sequence, TypedDict, List, Literal, Tuple
from langchain_core.messages import BaseMessage
def construct_simpleTool(env,chat,tools):

    # class DecisionPair(BaseModel):
    #     u_id: int = Field(description="id of the passenger")
    #     v_id: int = Field(description="id of the place")
    # class ActionPairs(BaseModel):
    #     decisions: List[Tuple[int,int]] = Field(
    #         description="list of assignment decision tuples, each of which indicates the passenger id is assigned to a place id"
    #     )
    # env.load_cache()
    # step = 1
    # present_decision_space_prompt, V_space = env.present_decision_space_prompt(step, max_num_vehicles=3)
    # basic_uv_prompt, Vinfo = env.present_UV_prompt(step, V_space, max_num_vehicles=1)
    # get_distance_time_tool = GetDistanceTimeByPos_Debug()
    # custom_message = agent.input_format(basic_uv_prompt, present_decision_space_prompt)
    # tools = [get_distance_time_tool]
    # tools = [get_distance_time_between_positions]
    tool_node = ToolNode(tools)
    BASE_URL = "http://localhost:10086"


    model_with_tools = chat.bind_tools(tools+[DecisionPair], tool_choice="any")

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
    def route(state: AgentState) -> Literal["action", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish
        if not last_message.tool_calls:
            return "__end__"
        # Otherwise if there is, we need to check what type of function call it is
        if last_message.tool_calls[0]["name"] == DecisionPair.__name__:
            return "__end__"
        # Otherwise we continue
        return "action"

    def call_model(state: AgentState):
        messages = state["messages"]
        print(f'messages, {messages}')
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define a new graph
    workflow = StateGraph(AgentState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", call_model)
    workflow.add_node("action", tool_node)

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.add_edge(START, "agent")

    # We now add a conditional edge
    workflow.add_conditional_edges(
        # First, we define the start node. We use `agent`.
        # This means these are the edges taken after the `agent` node is called.
        "agent",
        # Next, we pass in the function that will determine which node is called next.
        route,
    )

    # We now add a normal edge from `tools` to `agent`.
    # This means that after `tools` is called, `agent` node is called next.
    workflow.add_edge("action", "agent")

    # Finally, we compile it!
    # This compiles it into a LangChain Runnable,
    # meaning you can use it as you would any other runnable

    app = workflow.compile()

    from IPython.display import Image, display

    display(Image(app.get_graph(xray=True).draw_mermaid_png()))

    return app
def construct_noTool(sys_prompt,env,chat):

    # class DecisionPair(BaseModel):
    #     u_id: int = Field(description="id of the passenger")
    #     v_id: int = Field(description="id of the place")
    # class ActionPairs(BaseModel):
    #     decisions: List[Tuple[int,int]] = Field(
    #         description="list of assignment decision tuples, each of which indicates the passenger id is assigned to a place id"
    #     )
    # env.load_cache()
    # step = 1
    # present_decision_space_prompt, V_space = env.present_decision_space_prompt(step, max_num_vehicles=3)
    # basic_uv_prompt, Vinfo = env.present_UV_prompt(step, V_space, max_num_vehicles=1)
    # get_distance_time_tool = GetDistanceTimeByPos_Debug()
    # custom_message = agent.input_format(basic_uv_prompt, present_decision_space_prompt)
    # tools = [get_distance_time_tool]
    # tools = [get_distance_time_between_positions]


    model_with_tools = sys_prompt | chat.bind_tools([DecisionPair], tool_choice="any")

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
    def route(state: AgentState) -> Literal["action", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        # If there is no function call, then we finish

        # Otherwise if there is, we need to check what type of function call it is
        if last_message.tool_calls[0]["name"] == DecisionPair.__name__:
            return "__end__"

        return "__end__"
        # Otherwise we continue
        # return "action"

    def call_model(state: AgentState):
        messages = state["messages"]
        print(f'messages, {messages}')
        response = model_with_tools.invoke(state)
        return {"messages": [response]}

    # Define a new graph
    workflow = StateGraph(AgentState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", call_model)
    # workflow.add_node("action", tool_node)

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    # We now add a conditional edge
    # workflow.add_conditional_edges(
    #     # First, we define the start node. We use `agent`.
    #     # This means these are the edges taken after the `agent` node is called.
    #     "agent",
    #     # Next, we pass in the function that will determine which node is called next.
    #     route,
    # )

    # We now add a normal edge from `tools` to `agent`.
    # This means that after `tools` is called, `agent` node is called next.
    # workflow.add_edge("action", "agent")

    # Finally, we compile it!
    # This compiles it into a LangChain Runnable,
    # meaning you can use it as you would any other runnable

    app = workflow.compile()

    from IPython.display import Image, display

    display(Image(app.get_graph(xray=True).draw_mermaid_png()))

    return app