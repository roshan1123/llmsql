import os
import streamlit as st
#from sql_execution import execute_query
from langchain_community.llms import OpenAI
from langchain.prompts import load_prompt
from pathlib import Path 
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import yaml

# Load environment variables from .env file
load_dotenv()

#Load YAML 
with open("prompts/data_prompt2.yaml", "r", encoding="utf-8") as file:
    prompts = yaml.safe_load(file)

#Prepare Final Prompt Template
def get_prompt_template(table_name, user_input):
    for template in prompts['templates']:
        if "kanagawa_park" in template['template'] and table_name == "kanagawa_park":
            prompt_template = PromptTemplate(input_variables=["input"], template=template['template'])
            return prompt_template.format(input=user_input)
        elif "kanagawa_public_school" in template['template'] and table_name == "kanagawa_public_school":
            prompt_template = PromptTemplate(input_variables=["input"], template=template['template'])
            return prompt_template.format(input=user_input)
    return None

# Set Table Name from the Query
def get_table_name(user_input):
    """
    Determines the table name based on keywords in user input.
    Args:
        user_input (str): The input provided by the user.
    Returns:
        str: The table name corresponding to the user input.
    """
    if "公園" in user_input:
        return "kanagawa_park"
    elif "学校" in user_input:
        return "kanagawa_public_school"
    else:
        return None


# Access the OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def main():
    #setup env variable 
    os.environ["OPENAI_API_KEY"]=OPENAI_API_KEY
    #FrontEnd 
    st.title("SQL Agent")
    user_input = st.text_input("質問を聞いてください。")
    table_name = get_table_name(user_input)
    if table_name:
        print(f"Selected table: {table_name}")
    else:
        print("No matching table found for the input.")
    
    #Set the final Prompt 
    final_prompt = get_prompt_template(table_name, user_input)
    print(final_prompt)

    # Initialize the OpenAI LLM with appropriate parameters
    llm = OpenAI(model_name="davinci-002", temperature=0.9)
    #llm = OpenAI(temperature=0.9)


    if final_prompt:
        response = llm(prompt=final_prompt)
        print(response)
        with st.expander(label="SQL Query",expanded=False):
            st.write(response)
       #output = execute_query(response)
        #st.write(output) """

if __name__ == "__main__":
    main()

