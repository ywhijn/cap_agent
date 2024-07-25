'''
@Author: WANG Maonan
@Date: 2024-01-06 16:40:15
@Description: Agent Tools Prompts
@LastEditTime: 2024-01-06 20:26:05
'''
AGENT_MESSAGE = """{uv_pairs}
To do this, you must determine whether the current passenger request pickup position is in the taxi driver's service range or not. 
1. Don't finish the task until you have a final answer. You must output a list of decision when you finish this task.
2. You can only use tools mentioned before to help you make decision. Don't fabricate any other tool name not mentioned.
3. Remember what tools you have used, you can use same tool to solve the problems of identical property.
4. If all of the taxi drivers are not available or too far away from the certain passenger, you must leave assign the order to id '-1', which means the order is not assigned to any taxi driver. 
5. Output the list of passenger assignment decision in order of the given passenger request before. 
Let's take a deep breath and think step by step. Once you made a final decision, output it in the following format: \n
```
Final Answer: 
"decision": {{list of request assignment tuple(int, int) that indicate the request(1st id) from a passenger is assigned to a taxi driver(2nd id)}},
"explanation": {{your explanation about your decision, described your suggestions to the taxi drivers}}
``` \n"""
# AGENT_MESSAGE = """As the 'traffic signal light', you are tasked with controlling the traffic signal at an intersection. You've been in control for {sim_step} seconds. The last decision you made was {last_step_action}, with the explanation {last_step_explanation}. Now, you need to assess the current situation and make a decision for the next step.
#
# To do this, you must describe the Static State and Dynamic State of the traffic light, including the Intersection Layout, Signal Phase Structure, and Current Occupancy. Determine if you are facing a long-tail problem, such as the presence of an ambulance, impassable movements or the detectors are not work well.
#
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

SYSTEM_MESSAGE_PREFIX = """You are a mature taxi manager for vehicle dispatch and passenger assignment, who can give reasonable and efficient advice to taxi drivers in complex traffic scenarios. 

TOOLS:
------
You have access to the following tools:
"""

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


