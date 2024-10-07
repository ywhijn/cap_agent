'''
@Author: WANG Maonan
@Date: 2024-01-06 16:40:15
@Description: Agent Tools Prompts
@LastEditTime: 2024-01-06 20:26:05
'''
AGENT_MESSAGE_TOOL = \
"""{uv_pairs}
{decision_space}
To distribute the requests to taxi services, you must follow the given rules:
{rules}
Let's take a deep breath and think step by step.
Once you have made all of final decision, you must output them in the following format: \n
{output_format}
"""
AGENT_MESSAGE = \
"""{uv_pairs}
{decision_space}
You must follow the rules:
{rules}
Please assign taxi drivers to passengers according to the given rules and information. 
Provide your response only in the following format for each assignment without extra words:

u_ID: Passenger ID
v_ID: Driver ID
reason: Brief explanation for this assignment


Make sure to provide an assignment for each passenger if possible. Separate each assignment with a blank line.
"""

BASIC_rules={
"Constrain": "Each taxi driver can only take one passenger at a time, and each passenger can only be assigned to at most one taxi driver.",
"CoT":"Let's take a deep breath and think step by step.",
"complete_rule":
"Don't finish the task until you have a final answer. Make sure you have considered all the given information.",
"output_rule":
"You must output a list of assignment decision and reasons in order of the given passenger requests.",
"failed_request_handling":
"If all of the taxi drivers are not available or too far away from certain passenger, you must assign the passenger to a special taxi id -1, which means the order is NOT assigned to any taxi driver. "
}
TOOL_rule={
"fix_tools": "You can only use tools mentioned to help you make decision. Don't fabricate any other tool name not mentioned.",
"remeber_tools": "Remember what tools you have used, you can use same tool to solve the problems of identical property.",
"easy_tool" : "If the assignment decision is too obvious, such as only one candidate taxi id is in a passengers' options, you can directly assign the driver to the passenger without using any tool."
}


output_format="""
Once you made a final decision, output it in the following format: \n
```
Final Answer: 
"decision": {{ list of request assignment tuple(int, int) that indicate the request (1st id) from a passenger is assigned to a taxi driver (2nd id) }},
"explanation": {{ your explanation about your decision, described your suggestions to the taxi drivers }}
```
"""
# AGENT_MESSAGE = """As the 'traffic signal light', you are tasked with controlling the traffic signal at an intersection. You've been in control for {sim_step} seconds. The last decision you made was {last_step_action}, with the explanation {last_step_explanation}. Now, you need to assess the current situation and make a decision for the next step.
#
# To do this, you must describe the Static State and Dynamic State of the traffic light, including the Intersection Layout, Signal Phase Structure, and Current Occupancy. Determine if you are facing a long-tail problem, such as the presence of an ambulance, impassable movements or the detectors are not work well.
## The decision space for passenger requests is as follows:
# {dict_to_str(U2MultiV)}"""
#         if len(V2MultiU)<2:
#             decision_space_prompt += f"""
# If it's a standard situation, refer to the Traditional Decision and justify your decision based on the observed scene. If it's a long-tail scenario, analyze the possible actions, make a judgment, and output your decision.
#
# Remember to prioritize public transportation and emergency vehicles, follow the signal phase durations, and do not give a green light to impassable movements.
#
# Here are your attentions points:
# 1. DONOT finish the task until you have a final answer. You must output a decision when you finish this task. Your final output decision must be unique and not ambiguous. For example you cannot say "I can either keep lane or accelerate at current time".
# 2. You can only use tools mentioned before to help you make decision. DONOT fabricate any other tool name not mentioned.
# 3. Remember what tools you have used, DONOT use the same tool repeatedly.
#
# Let's take a deep breath and think step by step. Once you made a final decision, output it in the following format: \n
# ```
# Final Answer:
#     "decision":{{"traffic signal light decision, ONE of the available actions"}},
#     "expalanations":{{"your explaination about your decision, described your suggestions to the Crossing Guard"}}
# ``` \n
# """

# SYSTEM_MESSAGE_PREFIX = """You are ChatGPT, a large language model trained by OpenAI.
# You are now act as a mature traffic signal control assistant, who can give accurate and correct advice for human in complex traffic light control scenarios with different cases.
#
# TOOLS:
# ------
# You have access to the following tools:
# """
FORMAT_INSTRUCTIONS = """The way you use the tools is by specifying a json blob.
Specifically, this json should have a `action` key (with the name of the tool to use) and a `action_input` key (with the input to the tool going here).
The only values that should be in the "action" field are one of: {tool_names}

The $JSON_BLOB should only contain a SINGLE action, do NOT return a list of multiple actions. **Here is an example of a valid $JSON_BLOB**:
```
{{{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}}}
```

ALWAYS use the following format when you use tool:
Question: the input question you must answer
Thought: always summarize the tools you have used and think what to do next step by step
Action:
```
$JSON_BLOB
```
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
"""

SYSTEM_MESSAGE_PREFIX_TOOL = """You are a mature taxi manager for vehicle dispatch and passenger assignment, who can give reasonable and efficient advice to taxi drivers in complex traffic scenarios. 

TOOLS:
------
You have access to the following tools:
"""
# SYSTEM_MESSAGE_PREFIX = """You are a super decision-maker for vehicle dispatch and passenger assignment, who can give reasonable and efficient advice to taxi drivers in complex traffic scenarios.
# """
SYSTEM_MESSAGE_PREFIX = "You are an AI assistant tasked with assigning taxi drivers to passengers, who can explore more information to do more clever decision. "
SYSTEM_MESSAGE_SUFFIX = """
The taxi assignment control task usually involves many steps. You can break this task down into subtasks and complete them one by one. 
There is no rush to give a final answer unless you are confident that the answer is correct.
Answer the following questions as best you can. Begin! 

Take a deep breath and work on this problem step-by-step.
Reminder you MUST use the EXACT characters `Final Answer` when responding the final answer of the original input question.
"""

HUMAN_MESSAGE = "{input}\n\n{agent_scratchpad}"

HANDLE_PARSING_ERROR = """Check your output and make sure it conforms the format instructions! **Here is an example of a valid **format instructions**:
```
{
  "action": TOOL_NAME
  "action_input": INPUT
}
```"""


