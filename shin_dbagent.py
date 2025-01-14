import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
from langchain_community.utilities import SQLDatabase
import pandas as pd
import re
import logging
import os 
from dotenv import load_dotenv

load_dotenv()

# Create an in-memory SQLite database
db = SQLDatabase.from_uri("sqlite:///db/Chinook.db")
#print(db.dialect)
#print(db.get_usable_table_names())
#result = db.run("SELECT * FROM Artist;")
#print(result)


# Initialize LLM
# Initialize LLM
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

# Create SQL query chain
chain = create_sql_query_chain(llm, db)
#response = chain.invoke({"question": "How many employees are there"})
#print(response)


def execute_query(question):
    """
    Execute a SQL query generated from the user's question.
    """
    try:
        # Generate SQL query from the question
        response = chain.invoke({"question": question})
        cleaned_query = response.strip('```sql\n').strip('\n```')
        print(cleaned_query)
        result = db.run(cleaned_query)
        # Execute the quer
        
        # Convert result to a DataFrame
        #column_names = [col for col in result[0].keys()] if result else []
        result_df = pd.DataFrame(eval(result))
        
        return cleaned_query, result_df

    except ProgrammingError as e:
        logging.error("SQL Programming Error: %s", e)
        st.error("A database error occurred while processing your query. Please try again later.")
        return None, None
    except OperationalError as e:
        logging.error("Database Connection Error: %s", e)
        st.error("There was a problem with the database. Please contact the administrator.")
        return None, None
    except Exception as e:
        logging.error("Unexpected Error: %s", e)
        st.error("An unexpected error occurred. Please try again later.")
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
            st.warning("No result returned due to an error.")
    else:
        st.warning("Please enter a question.")