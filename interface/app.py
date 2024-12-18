import streamlit as st
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import tempfile
from tools.basic_calculator import basic_calculator
from tools.reverser import reverse_string
from tools.sql_database_toolkit import get_metadata, list_tables, check_query, execute_query
from models.openai_models import OpenAIModel
# from models.ollama_models import OllamaModel
from agents.agents import Agent

# Streamlit App
st.title("Database Chatbot")
st.markdown("""
Upload a database file and interact with a chatbot to query the database using natural language.
""")

# Step 1: File Uploader for Database
uploaded_file = st.file_uploader("Upload your SQLite database file (.db)", type=["db"])

# Check if a file is uploaded
if uploaded_file is not None:
    # Save the uploaded file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_file.write(uploaded_file.read())
    temp_file.close()

    # Generate SQLite connection string
    connection_string = f"sqlite:///{temp_file.name}"
    st.success(f"Database loaded successfully: {temp_file.name}")

    # Step 2: Initialize the Agent
    tools = [basic_calculator, reverse_string, get_metadata, list_tables, check_query, execute_query]

    model_service = OpenAIModel
    model_name = 'gpt-4o'
    stop = None


    # # Uncomment below to run with Ollama
    # model_service = OllamaModel
    # model_name = 'sqlcoder:7b'
    # stop = "<|eot_id|>"

    agent = Agent(
        tools=tools,
        model_service=model_service,
        model_name=model_name,
        connection_string=connection_string,
        stop=stop
    )

    # Step 3: Chat Interface
    st.header("Chat with Your Database")
    user_query = st.text_input("Ask me anything about your database:")

    if st.button("Submit Query"):
        if user_query.strip():
            try:
                response = agent.work(user_query)

                if isinstance(response, dict) and "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    st.markdown(f"**Response:**\n{response}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a query.")
else:
    st.info("Please upload a database file to begin.")


