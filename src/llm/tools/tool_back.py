from src.llm.LLM_options import LLMOptions,cfg
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage
)
from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )




repl = PythonREPL()
from langgraph.prebuilt import ToolNode
import os
def try_python():
    python_repl_node = ToolNode([python_repl])
    cls_took_ars = [{'name': 'python_repl', 'args': {
        'code': 'import os\nprint(os.listdir())\nprint(1+1)'},
                     'id': 'call_0_30cf2e36-207d-458f-aabf-b1ac44c8429f', 'type': 'tool_call'}, ]
    tool_calls = AIMessage(
        content="",
        tool_calls=cls_took_ars
    )

    pres = python_repl_node.invoke({"messages": [tool_calls]})
    return pres
res=try_python()
print(res['messages'][0].content)