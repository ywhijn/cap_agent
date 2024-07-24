'''
@Author: WANG Maonan
@Date: 2023-09-18 17:52:04
@Description: Output parse
@LastEditTime: 2023-10-15 23:54:16
'''
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
output_format_prompt_text = f"Output the a list of order assignment tuple(int, int) that indicate the order(1st id) from a passenger is assigned to a taxi driver(2nd id). " \
                            "For example, If the final decision is assign order 1 to taxi driver 2 and order 2 to taxi driver 3, please output [(1, 2), (2, 3)] as a list of tuple."
class OutputParse(object):
    def __init__(self, env=None, llm=None) -> None:
        self.sce = env
        self.llm = llm

        self.response_schemas = [
            ResponseSchema(
                name="decision", description=output_format_prompt_text),
            ResponseSchema(
                name="explanation", description=f"Explain for the taxi driver why you make such decision.")
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()

    def parser_output(self, final_results:str) -> str:
        prompt_template = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(
                    "Parse the problem response follow the format instruction.\nformat_instructions:{format_instructions}\n Response: {answer}")
            ],
            input_variables=["answer"],
            partial_variables={"format_instructions": self.format_instructions}
        )

        custom_message = prompt_template.format_messages(
            answer = final_results,
        )
        output = self.llm(custom_message)
        self.final_parsered_output = self.output_parser.parse(output.content)
        
        return self.final_parsered_output