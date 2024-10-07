

# agent_response=agent.agent_run(UV_loc_string)
# print(f'agent response Output, {agent_response}')
# agent_action = agent.parse_output(agent_response)
# print(f'parsed response Output, {agent_action}')

# print(f'scanned_UVpairs, {scanned_UVpairs}')
template = "Tell me a {adjective} joke about {content}."
from langchain import PromptTemplate
prompt_template = PromptTemplate.from_template(template)
prompt_template.input_variables
# -> ['adjective', 'content']
p=prompt_template.format(adjective="funny", content="chickens")
print(p)