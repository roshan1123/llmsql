import mysql.connector
from mysql.connector import Error
import pandas as pd 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def execute_query(sql):
    #MySQL Connection Parameter
    connection_params = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_NAME")
    }

    query = sql
    try:
        #Establish a connection to mysql 
        conn = mysql.connector.connect(**connection_params)
        print("Connected mysql server successfully")
        #Create a Cursor Object
        cur = conn.cursor()

        #Execute The Query 
        try:
            cur.execute(query)
        except mysql.connector.errors.ProgrammingError as pe:
            print("Query Complilation Error", pe)
            return("Query Compilation Error")
    
        #Fetch All Results
        query_results = cur.fetchall()

        #Get column name from the cursor description 
        column_names = [[col[0] for col in cur.description]]
        #print(column_names)

        # Create a Pandas DataFrame
        data_frame = pd.DataFrame(query_results, columns=column_names)
        #print(data_frame)
        # Print the DataFrame
        #print(data_frame)
        return data_frame
    except mysql.connector.errors.DatabaseError as de:
        print("Mysql Database Error", de)
    
    except Exception as e:
        print("An error occurred:", e)

    finally:
        #Close the cursor and connections 
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
            print("Mysql Database Closed")
        except:
            pass


def create_connection():
    """Create a connection to the MySQL database using parameters from .env."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            print("Connection to MySQL database was successful")
        return connection
    except Error as e:
        print(f"Error: '{e}' occurred")
        return None

def close_connection(connection):
    """Close the MySQL connection."""
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection closed")

# Example usage
if __name__ == "__main__":
    query = '''
            SELECT * FROM `kanagawa_park` WHERE `Address`LIKE '%横浜市%';
            '''
    execute_query(query)