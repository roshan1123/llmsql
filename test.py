from langchain.prompts import PromptTemplate
import yaml

# Load YAML
with open("prompts/data_prompt2.yaml", "r", encoding="utf-8") as file:
    prompts = yaml.safe_load(file)

def get_prompt_template(table_name, user_input):
    for template in prompts['templates']:
        if "kanagawa_park" in template['template'] and table_name == "kanagawa_park":
            prompt_template = PromptTemplate(input_variables=["input"], template=template['template'])
            return prompt_template.format(input=user_input)
        elif "kanagawa_public_school" in template['template'] and table_name == "kanagawa_public_school":
            prompt_template = PromptTemplate(input_variables=["input"], template=template['template'])
            return prompt_template.format(input=user_input)
    return None

# Example Usage
table = "kanagawa_park"
user_input = "Find all parks in Yokohama with swings and toilets."
final_prompt = get_prompt_template(table, user_input)
print(final_prompt)
