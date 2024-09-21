'''
@Author: WANG Maonan
@Date: 2023-09-04 20:51:49
@Description: traffic light control LLM Agent
@LastEditTime: 2024-01-06 17:02:26
'''
import os
from typing import List, Literal, Any
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.memory import ConversationSummaryMemory
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents import create_tool_calling_agent,AgentExecutor
from langchain.agents import Tool
from .get_abs_path import get_abs_path
from .callback_handler import create_file_callback
from .llm_rl_prompt import (
    SYSTEM_MESSAGE_PREFIX,
    SYSTEM_MESSAGE_SUFFIX,
    HUMAN_MESSAGE,
    AGENT_MESSAGE
)
from langchain.chains.openai_functions import create_structured_output_runnable
from langchain.output_parsers import PydanticOutputParser
from langchain import hub
from langchain_core.messages import (
    HumanMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langgraph.graph import END
from langchain_core.pydantic_v1 import BaseModel, Field
class DecisionPair(BaseModel):
    u_id: int = Field(description="id of the passenger")
    v_id: int = Field(description="id of the taxi driver")
class ActionPairs(BaseModel):
    decisions: List[DecisionPair] = Field(
        description= "list of assignment decision pairs, each of which indicates the request (u_id) from a passenger is assigned to a taxi driver (v_id)"
    )

# response_schemas = [
#     ResponseSchema(name="answer", description="answer to the user's question"),
#     ResponseSchema(name="source", description="source used to answer the user's question, should be a website.")
# ]
# output_parser = StructuredOutputParser.from_response_schemas(response_schemas)


class TaxiAgent:
    def __init__(self,
                 env,
                 llm: ChatOpenAI,
                 tools: List[Tool],
                 cfg: Any = None,
                 verbose: bool = True
                 ) -> None:
        self.env = env
        self.llm = llm  # ChatGPT Model
        # print("SYSTEM_MESSAGE_PREFIX\n", SYSTEM_MESSAGE_PREFIX)
        # print("SYSTEM_MESSAGE_SUFFIX\n", SYSTEM_MESSAGE_SUFFIX)
        # print("HUMAN_MESSAGE\n", HUMAN_MESSAGE)
        # print("AGENT_MESSAGE\n", AGENT_MESSAGE)
        # callback
        path_convert = get_abs_path(__file__)
        self.file_callback = create_file_callback(path_convert('../agent_id_tool.log'))
        # functions = [convert_to_openai_function(t) for t in tools]
        # self.tools = []  # agent 可以使用的 tools
        # for ins in tools:
        #     func = getattr(ins, 'inference')
        #     print(func.name, func.description)
        #     self.tools.append(
        #         Tool(name=func.name, description=func.description, func=func)
        #     )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE_PREFIX),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.memory = ConversationSummaryMemory(
            llm=self.llm,
        )
        self.action_output_parser = PydanticOutputParser(pydantic_object=ActionPairs)
        self.output_format_prompt = self.action_output_parser.get_format_instructions()
        # self.agent = create_tool_calling_agent(llm, tools, prompt)
        self.agent = create_tool_calling_agent(llm, tools, prompt=prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, verbose=True)
        # self.agent = initialize_agent(
        #     tools=self.tools,
        #     llm=self.llm,
        #     agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        #     verbose=verbose,
        #     memory=self.memory,
        #     agent_kwargs={
        #         'system_message_prefix': SYSTEM_MESSAGE_PREFIX,
        #         'system_message_suffix': SYSTEM_MESSAGE_SUFFIX,
        #         'human_message': HUMAN_MESSAGE,
        #         # 'format_instructions': FORMAT_INSTRUCTIONS,
        #     },
        #     # handle_parsing_errors=HANDLE_PARSING_ERROR,
        #     max_iterations=4,
        #     early_stopping_method="generate",
        # )

    def input_format(self, basic_uv_prompt,present_decision_space_prompt):
        """Agent Run
        """
        prompt_template = ChatPromptTemplate.from_template(AGENT_MESSAGE)
        custom_message = prompt_template.format_messages(
            uv_pairs=basic_uv_prompt,
            decision_space=present_decision_space_prompt,
            output_format=self.output_format_prompt
        )
        return custom_message
        # print("AGENT prompt")
        # for message in custom_message:
        #     print(message.content)
        # print("AGENT RUN")
        # llm_response = self.agent_executor.invoke({
        #     "input": custom_message
        # })
        # print(llm_response)
        # action_pairs = []
        # try:
        #     structured_output = self.action_output_parser.parse(llm_response)
        #     print("Structured Output:", structured_output)
        #     # 现在 structured_output 是一个 ActionPairs 对象
        #     for decision in structured_output.decisions:
        #         print(f"Passenger {decision.u_id} assigned to Driver {decision.v_id}")
        #         action_pairs.append((int(decision.u_id), int(decision.v_id)))
        # except Exception as e:
        #     print("Error parsing output:", e)
        # # self.memory.clear()
        # return action_pairs
    def agent_run(self, basic_uv_prompt,present_decision_space_prompt):
        """Agent Run
        """
        prompt_template = ChatPromptTemplate.from_template(AGENT_MESSAGE)
        custom_message = prompt_template.format_messages(
            uv_pairs=basic_uv_prompt,
            decision_space=present_decision_space_prompt,
            output_format=self.output_format_prompt
        )
        print("AGENT prompt")
        for message in custom_message:
            print(message.content)
        print("AGENT RUN")
        llm_response = self.agent_executor.invoke({
            "input": custom_message
        })
        print(llm_response)
        action_pairs = []
        try:
            structured_output = self.action_output_parser.parse(llm_response)
            print("Structured Output:", structured_output)
            # 现在 structured_output 是一个 ActionPairs 对象
            for decision in structured_output.decisions:
                print(f"Passenger {decision.u_id} assigned to Driver {decision.v_id}")
                action_pairs.append((int(decision.u_id), int(decision.v_id)))
        except Exception as e:
            print("Error parsing output:", e)
        # self.memory.clear()
        return action_pairs
from src.llm.tools.math_tools import get_math_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from src.llm.complier.compiler_modules import JoinOutputs, select_recent_messages, _parse_joiner_output, create_plan_and_schedule, \
    create_planner, build_graph


class CompilerAgent:
    def __init__(self,
                 env,
                 llm: ChatOpenAI,
                 tools: List[Tool],
                 verbose: bool = True
                 ) -> None:
        self.env = env
        self.llm = llm  # ChatGPT Model

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE_PREFIX),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        # self.memory = ConversationSummaryMemory(
        #     llm=self.llm,
        # )
        # self.agent = create_tool_calling_agent(llm, tools, prompt)
        # self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, verbose=True)
        #
        self.tools = self.initialize_tools()
        prompt = hub.pull("wfh/llm-compiler")
        print("wfh/llm-compiler",prompt)
        self.planner = create_planner(llm, self.tools, prompt)
        joiner_prompt = hub.pull("wfh/llm-compiler-joiner").partial(
            examples=""
        )  # You can optionally add examples
        print("wfh/llm-compiler-joiner",joiner_prompt)

        self.plan_and_schedule = create_plan_and_schedule(self.planner)
        joinOutputParser = create_structured_output_runnable(JoinOutputs, llm, joiner_prompt)
        self.joiner = select_recent_messages | joinOutputParser | _parse_joiner_output
        self.graph=build_graph(self.plan_and_schedule,self.joiner)

        from IPython.display import Image, display

        try:
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except Exception:
            # This requires some extra dependencies and is optional
            pass

    def initialize_tools(self):
        os.environ["TAVILY_API_KEY"]="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"
        self.search = TavilySearchResults(
            max_results=1,
            description='tavily_search_results_json(query="the search query") - a search engine.',
        )
        self.calculate = get_math_tool(self.llm)
        tools = [self.search, self.calculate]
        return tools

    def test_math(self):
        response  = self.calculate.invoke(
            {
                "problem": "What's the temp of sf + 5?",
                "context": ["The temperature of sf is 32 degrees"],
            }
        )
        print(response)
    def test_planner(self):
        example_question = "What's the temperature in SF raised to the 3rd power?"
        for task in self.planner.stream([HumanMessage(content=example_question)]):
            print(task["tool"], task["args"])
            print("---")
    def test_plan_and_schedule(self):
        example_question = "What's the temperature in SF raised to the 3rd power?"
        tool_messages = self.plan_and_schedule.invoke([HumanMessage(content=example_question)])
        print(tool_messages)
    def test_joiner(self):
        example_question = "What's the temperature in SF raised to the 3rd power?"
        tool_messages = self.plan_and_schedule.invoke([HumanMessage(content=example_question)])
        input_messages = [HumanMessage(content=example_question)] + tool_messages
        self.joiner.invoke(input_messages)
    def test_graph(self,chain):
        for step in chain.stream([HumanMessage(content="What's the GDP of New York?")]):
            print(step)
            print("---")
        print(step[END][-1].content)
    def test_multi_hop(self,chain):
        steps = chain.stream(
            [
                HumanMessage(
                    content="What's the oldest parrot alive, and how much longer is that than the average?"
                )
            ],
            {
                "recursion_limit": 100,
            },
        )
        for step in steps:
            print(step)
            print("---")
        print(step[END][-1].content)

