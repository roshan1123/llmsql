from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
#from mysql.connector import Error
#from langchain_groq import ChatGroq
import streamlit as st
from langchain.chains import create_sql_query_chain
import re
import os 
#sql_query=""

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: Show me Album Name Starts with Albhabets "A"
    SELECT * FROM Album WHERE `Title` LIKE "%A";
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  
  llm = ChatOpenAI(model="gpt-3.5-turbo")
  #llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )
    


import re

def extract_sql_query_from_runnable(runnable_object):
    # Extract the 'template' string or relevant message part from the RunnableSequence
    # For example, if the text is within a nested structure, we access it appropriately
    
    # Try to access the nested message string (adjust according to your actual object structure)
    try:
        # This will depend on your exact object structure, but for now we assume you need the template text
        message_template = runnable_object.middle[0].messages[0].prompt.template
    except AttributeError:
        print("Error: Could not find the template text in the runnable object.")
        return None
    
    # Now you can apply the regular expression to the string
    return extract_sql_query_from_template(message_template)

def extract_sql_query_from_template(text):
    print(text)
    # Regular expression to capture the SQL query after the prompt template
    pattern = r"SQL Query:\s*(SELECT[\s\S]+?;)"
    
    # Search for the pattern in the text
    match = re.search(pattern, text)
    
    if match:
        return match.group(1)  # Return the found SQL query
    else:
        return None  # If no SQL query is found

# Example usage: assuming 'middle' is the object you're passing
# This will need to be the actual object you have, not a string version of it



def get_response(user_query: str, db: SQLDatabase, chat_history: list):
  sql_chain = get_sql_chain(db)
  print(sql_chain)

  # Extract SQL query
  sql_query = extract_sql_query_from_runnable(sql_chain)
  print("Actual SQL Query", sql_query)
  
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    日本語で回答ください。
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""
  
  prompt = ChatPromptTemplate.from_template(template)
  
  llm = ChatOpenAI(model="gpt-3.5-turbo")
  #llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)


  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: db.get_table_info(),
    
      response=lambda vars: db.run(vars["query"]),
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  #query = create_sql_query_chain(llm, db)
  #print("SQL Chain",sql_chain)
  #print("SQL Query", query)
  #print(prompt)
 

  return chain.invoke({
    "question": user_query,
    "chat_history": chat_history,
  })
    
  
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]



st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

st.title("Chat with MySQL")
    #st.subheader("Settings")
    #st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
    #st.text_input("Host", value="localhost", key="Host")
    #st.text_input("Port", value="3307", key="Port")
    #st.text_input("User", value="root", key="User")
    #st.text_input("Password", type="password", value="", key="Password")
    #st.text_input("Database", value="Chinook", key="Database")

try:
 db = init_database(user, password, host, port,database)
 print("Database connection established.")
 st.session_state.db = db
except Exception as e:
 print(f"An error occurred: {e}")



for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        #query_respons = st.session_state.db.run(sql_query)
        #print("SQL Query: ", response[1])
        #query = response[1]
        #st.markdown(response[1])
        #sql_query=""
        #query_respons = st.session_state.db.run(query)
        #query_respons = db.run("SELECT * FROM Artist LIMIT 10;")
        #st.markdown(query_respons)


        
    st.session_state.chat_history.append(AIMessage(content=response))