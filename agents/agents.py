from prompts.prompts import agent_system_prompt_template
from models.openai_models import OpenAIModel
# from models.ollama_models import OllamaModel
# from tools.basic_calculator import basic_calculator
# from tools.reverser import reverse_string
from tools.database_conn import create_db_connection
from tools.sql_database_toolkit import get_metadata, list_tables, check_query, execute_query
from toolbox.toolbox import ToolBox
import pandas as pd


class Agent:
    def __init__(self, tools, model_service, model_name,connection_string=None, stop=None):
        """
        Initializes the agent with a list of tools, a model, and an optional database connection.

        Parameters:
        tools (list): List of tool functions.
        model_service (class): The model service class with a generate_text method.
        model_name (str): The name of the model to use.
        connection_string (str, optional): Connection string for the database (if using SQL tools).
        stop (str, optional): A stopping condition for the model generation.
        """
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name
        self.stop = stop
        # comment for openai
        # self.model_main = model_main
        self.connection_string = connection_string
        self.db_engine = None
        #comment for openai 
        # self.stop = stop


        # Initialize the database connection if a connection string is provided
        if connection_string:
            self.db_engine = create_db_connection(connection_string)

    def prepare_tools(self):
        """
        Stores the tools in the toolbox and returns their descriptions.

        Returns:
        str: Descriptions of the tools stored in the toolbox.
        """
        toolbox = ToolBox()
        toolbox.store(self.tools)
        tool_descriptions = toolbox.tools()
        return tool_descriptions
    


    def think(self, prompt):
        """
        Runs the generate_text method on the model using the system prompt template,
        tool descriptions, and database schema (if available).

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        dict: The response from the model as a dictionary.
        """
        tool_descriptions = self.prepare_tools()

        # Retrieve schema information if the database connection is initialized
        schema_info = ""
        if self.db_engine:
            schema_info = f"Database Schema:\n{get_metadata(self.db_engine)}\n"

        # Format the system prompt
        agent_system_prompt = agent_system_prompt_template.format(
            tool_descriptions=tool_descriptions,
            schema_info=schema_info,
            
        )

        # Create an instance of the model service with the system prompt
        model_instance = self.model_service(
            model=self.model_name,
            system_prompt=agent_system_prompt,
            temperature=0,
            # stop = self.stop

        )

        # Generate and return the response dictionary
        agent_response_dict = model_instance.generate_text(prompt)
        return agent_response_dict
    
    def format_query_response(self, query_result):
        """
        Formats a query execution result into a natural language sentence.

        Args:
            query_result (pd.DataFrame): The result of the SQL query execution.

        Returns:
            str: Natural language description of the query result.
        """

        # Validate query_result is a DataFrame
        if not isinstance(query_result, pd.DataFrame):
            print("Query Result is not a DataFrame.")
            return "The query result format is unsupported or invalid."

        # Handle empty DataFrame
        if query_result.empty:
            print("Query Result is empty.")
            return "The query returned no results."

        # Extract column names and first row values
        column_names = query_result.columns.tolist()
        first_row = query_result.iloc[0].tolist()

        # Handle DataFrame with no rows
        if not first_row:
            print("Query Result has no rows.")
            return "The query returned no data to process."

        # Format the result dynamically
        result_sentences = []
        for col, val in zip(column_names, first_row):
            # Replace underscores in column names with spaces for readability
            col_name = col.replace("_", " ")
            # Format numbers with commas
            if pd.api.types.is_numeric_dtype(query_result[col]):
                val = f"{val:,}"  # Add commas for large numbers
            result_sentences.append(f"{col_name} is {val}")

        formatted_result = ", ".join(result_sentences)
        print("Formatted Query Response:", formatted_result)
        return formatted_result




    
    def work(self, prompt):
        """
        Parses the dictionary returned from think and executes the appropriate tool.

        Parameters:
            prompt (str): The user query to generate a response for.

       Returns:
            the tool response or tool_input if no matching tool is found."
        """
        agent_response_dict = self.think(prompt)
        tool_choice = agent_response_dict.get("tool_choice")
        tool_input = agent_response_dict.get("tool_input")

        # Handle SQL multi-tool logic
        if tool_choice == "execute_query":
            # Step 1: Get Schema (if necessary)
            schema = get_metadata(self.db_engine)
            print("Schema Retrieved:", schema)

            # Step 2: Validate Query
            query = tool_input if isinstance(tool_input, str) else tool_input.get("query")
            is_valid = check_query(self.db_engine, query)
            if "Invalid" in is_valid:
                print("Query Validation Failed:", is_valid)
                return is_valid

            # Step 3: Execute Query
            query_result = execute_query(self.db_engine, query)
            print("Query Execution Response:", query_result)

            formatted_response = self.format_query_response(query_result)
            return formatted_response



        for tool in self.tools:
            if tool.__name__ == tool_choice:
                # Handle SQL tools
                if tool in [get_metadata, list_tables, check_query, execute_query]:
                    if not self.db_engine:
                        raise ValueError("Database engine is not initialized. Provide a valid connection string.")

                    # Remove 'engine' key if present in tool_input
                    if isinstance(tool_input, dict) and "engine" in tool_input:
                        tool_input.pop("engine")

                    # Execute the tool
                    query_result = tool(self.db_engine, **tool_input)
                else:
                    # Handle non-SQL tools
                    query_result = tool(tool_input)


        print(tool_input)
        return tool_input



