import os
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from dotenv import load_dotenv
import pandas as pd
import re
load_dotenv() 

# Database connection parameters
db_user = "root"
db_password = ""
db_host = "localhost"
db_name = "Chinook"
db_port = 3307

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# Initialize SQLDatabase
db = SQLDatabase(engine, sample_rows_in_table_info=20)

# Initialize LLM
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])
k=20
# Create SQL query chain
chain = create_sql_query_chain(llm, db,prompt=None,k=20)


def extract_column_names(sql_query):
    # Regular expression to match column names
    pattern = r"`\w+`\.`(\w+)`"
    # Find all matches
    matches = re.findall(pattern, sql_query)
    return matches

def execute_query(question):
    try:
        # Generate SQL query from question
        response = chain.invoke({"question": question})
        print(response)
        print("###################################################")
        # Strip the formatting markers from the response
        cleaned_query = response.strip('```sql\n').strip('\n```')
        print("############Clean Query##############################")     
        print(cleaned_query)
        print("#############Execute Clean Query#############################")     
        # Execute the query
        result = db.run(cleaned_query)
        # Extract column names
        #column_names = extract_column_names(cleaned_query) 
        print("################Column Names######################")        
        #print(column_names)   
        result = pd.DataFrame(eval(result))
        print("###################################################")        
        # Display the result
        print(result)
                
        # Return the query and the result
        return cleaned_query, result
    except ProgrammingError as e:
        st.error(f"An error occurred: {e}")
        return None, None

# Streamlit interface
st.title("Question Answering App")

# Input from user
question = st.text_input("Enter your question:")

if st.button("Execute"):
    if question:
        cleaned_query, query_result = execute_query(question)
        
        if cleaned_query and query_result is not None:
            st.write("Generated SQL Query:")
            st.code(cleaned_query, language="sql")
            st.write("Query Result:")
            st.write(query_result)
        else:
            st.write("No result returned due to an error.")
    else:
        st.write("Please enter a question.")
        