from termcolor import colored
from prompts.prompts import agent_system_prompt_template
from models.ollama_models import OllamaModel
from tools.basic_Calculator import basic_Calculator
from tools.reverser import reverse_string
from toolbox.toolbox import ToolBox


class Agent:
    def __init__(self, tools, model_service, model_name, stop=None):
        """
        Initializes the agent with a list of tools and a model.

        Parameters:
        tools (list): List of tool functions.
        model_service (class): The model service class with a generate_text method.
        model_name (str): The name of the model to use.
        """
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name
        self.stop = stop

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
        Runs the generate_text method on the model using the system prompt template and tool descriptions.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        dict: The response from the model as a dictionary.
        """
        tool_descriptions = self.prepare_tools()
        agent_system_prompt = agent_system_prompt_template.format(tool_descriptions=tool_descriptions)

        # Create an instance of the model service with the system prompt

        if self.model_service == OllamaModel:
            model_instance = self.model_service(
                model=self.model_name,
                system_prompt=agent_system_prompt,
                temperature=0,
                stop=self.stop
            )
        else:
            model_instance = self.model_service(
                model=self.model_name,
                system_prompt=agent_system_prompt,
                temperature=0
            )

        # Generate and return the response dictionary
        agent_response_dict = model_instance.generate_text(prompt)
        return agent_response_dict

    def work(self, prompt):
        """
        Parses the dictionary returned from think and executes the appropriate tool.

        Parameters:
        prompt (str): The user query to generate a response for.

        Returns:
        The response from executing the appropriate tool or the tool_input if no matching tool is found.
        """
        agent_response_dict = self.think(prompt)
        tool_choice = agent_response_dict.get("tool_choice")
        tool_input = agent_response_dict.get("tool_input")

        for tool in self.tools:
            if tool.__name__ == tool_choice:
                response = tool(tool_input)

                print(colored(response, 'cyan'))
                
                return tool(tool_input)

        print(colored(tool_input, 'cyan'))
        
        return


# Example usage
if __name__ == "__main__":

    tools = [basic_Calculator, reverse_string]


    # Uncoment below to run with OpenAI
    # model_service = OpenAIModel
    # model_name = 'gpt-3.5-turbo'
    # stop = None

    # Uncomment below to run with Ollama
    model_service = OllamaModel
    model_name = 'llama3.2:latest'
    stop = "<|eot_id|>"

    agent = Agent(tools=tools, model_service=model_service, model_name=model_name, stop=stop)

    while True:
        prompt = input("Ask me anything: ")
        if prompt.lower() == "exit":
            break
    
        agent.work(prompt)


# from termcolor import colored
# from prompts.prompts import agent_system_prompt_template
# from models.ollama_models import OllamaModel
# from tools.basic_Calculator import basic_Calculator
# from tools.reverser import reverse_string
# from tools.database_conn import create_db_connection
# from tools.sql_database_toolkit import get_metadata, list_tables, check_query, execute_query
# from toolbox.toolbox import ToolBox


# class Agent:
#     def __init__(self, tools, general_model_service, general_model_name, sql_model_service, sql_model_name, connection_string=None, stop=None):
#         """
#         Initializes the agent with tools, general-purpose model, and SQL-specific model.

#         Parameters:
#         tools (list): List of tool functions.
#         general_model_service (class): The model service class for general tasks.
#         general_model_name (str): The name of the general-purpose model.
#         sql_model_service (class): The model service class for SQL tasks.
#         sql_model_name (str): The name of the SQL-specific model.
#         stop (str): Optional stopping condition for model responses.
#         """
#         self.tools = tools
#         self.general_model_service = general_model_service
#         self.general_model_name = general_model_name
#         self.sql_model_service = sql_model_service
#         self.sql_model_name = sql_model_name
#         self.stop = stop
#         self.db_engine = None


#         # Initialize the database connection if a connection string is provided
#         if connection_string:
#             self.db_engine = create_db_connection(connection_string)


#     def prepare_tools(self):
#         """
#         Stores the tools in the toolbox and returns their descriptions.

#         Returns:
#         str: Descriptions of the tools stored in the toolbox.
#         """
#         toolbox = ToolBox()
#         toolbox.store(self.tools)
#         tool_descriptions = toolbox.tools()
#         return tool_descriptions
    

#     def think(self, prompt, sql_task=False):
#         """
#         Runs the generate_text method on the appropriate model based on the task type.

#         Parameters:
#         prompt (str): The user query to generate a response for.
#         sql_task (bool): Whether the task involves SQL operations.

#         Returns:
#         dict: The response from the chosen model as a dictionary.
#         """
#         tool_descriptions = self.prepare_tools()

#         # Retrieve schema information if the database connection is initialized
#         schema_info = ""
#         if self.db_engine:
#             schema_info = f"Database Schema:\n{get_metadata(self.db_engine)}\n"

#         # Format the system prompt
#         agent_system_prompt = agent_system_prompt_template.format(
#             tool_descriptions=tool_descriptions,
#             schema_info=schema_info,
            
#         )

#         # Select the appropriate model
#         if sql_task:
#             model_instance = self.sql_model_service(
#                 model=self.sql_model_name,
#                 system_prompt=agent_system_prompt,
#                 temperature=0,
#                 stop=self.stop
#             )
#         else:
#             model_instance = self.general_model_service(
#                 model=self.general_model_name,
#                 system_prompt=agent_system_prompt,
#                 temperature=0,
#                 stop=self.stop
#             )

#         # Generate and return the response dictionary
#         agent_response_dict = model_instance.generate_text(prompt)
#         return agent_response_dict

#     def work(self, prompt):
#         """
#         Parses the dictionary returned from think and executes the appropriate tool.

#         Parameters:
#             prompt (str): The user query to generate a response for.

#         Returns:
#             The tool response or tool_input if no matching tool is found.
#         """
#         sql_tools = ["get_metadata", "list_tables", "check_query", "execute_query"]

#         # Step 1: Use the appropriate model based on the tool choice
#         # Initial think with the general-purpose model
#         agent_response_dict = self.think(prompt)
#         tool_choice = agent_response_dict.get("tool_choice")
#         tool_input = agent_response_dict.get("tool_input")

#         # Step 2: Re-think with SQL-specific model if required
#         if tool_choice in sql_tools:
#             # Use the SQL-specific model
#             agent_response_dict = self.think(prompt)
#             tool_choice = agent_response_dict.get("tool_choice")
#             tool_input = agent_response_dict.get("tool_input")

#         # Step 3: Handle SQL multi-tool logic
#         if tool_choice == "execute_query":
#             # Step 3.1: Get Schema (if necessary)
#             schema = get_metadata(self.db_engine)
#             print("Schema Retrieved:", schema)

#             # Step 3.2: Validate Query
#             query = tool_input if isinstance(tool_input, str) else tool_input.get("query")
#             is_valid = check_query(self.db_engine, query)
#             if "Invalid" in is_valid:
#                 print("Query Validation Failed:", is_valid)
#                 return is_valid

#             # Step 3.3: Execute Query
#             query_result = execute_query(self.db_engine, query)
#             print("Query Execution Response:", query_result)

#             formatted_response = self.format_query_response(query_result)
#             return formatted_response

#         # Step 4: Execute the corresponding tool
#         for tool in self.tools:
#             if tool.__name__ == tool_choice:
#                 if tool in [get_metadata, list_tables, check_query, execute_query]:
#                     # Handle SQL tools
#                     if not self.db_engine:
#                         raise ValueError("Database engine is not initialized. Provide a valid connection string.")

#                     if tool == get_metadata:
#                         # Call get_metadata directly with self.db_engine
#                         query_result = tool(self.db_engine)
#                     elif isinstance(tool_input, dict):
#                         # Use tool_input for other SQL tools
#                         query_result = tool(self.db_engine, **tool_input)
#                     else:
#                         raise ValueError(f"Invalid tool_input for {tool_choice}: {tool_input}")
#                 else:
#                     # Handle non-SQL tools
#                     query_result = tool(tool_input)

#                 print(query_result)
#                 return query_result

#         # Step 5: Return the tool_input if no matching tool is found
#         print(tool_input)
#         return tool_input

# Example usage
if __name__ == "__main__":

    tools = [basic_Calculator, reverse_string, get_metadata, list_tables, check_query, execute_query]


    # Uncoment below to run with OpenAI
    # model_service = OpenAIModel
    # model_name = 'gpt-3.5-turbo'
    # stop = None
    sql_model_service = OllamaModel
    sql_model_name = 'sqlcoder:7b'

    # Uncomment below to run with Ollama
    general_model_service = OllamaModel
    general_model_name = 'llama3.2:latest'

    stop = "<|eot_id|>"

    connection_string = "sqlite:///transactions.db"



    agent = Agent(tools=tools,
                   general_model_service=general_model_service, 
                   general_model_name=general_model_name,
                   sql_model_service=sql_model_service,
                   sql_model_name=sql_model_name,
                   connection_string=connection_string,
                   stop=stop)

    while True:
        prompt = input("Ask me anything: ")
        if prompt.lower() == "exit":
            break
    
        agent.work(prompt)