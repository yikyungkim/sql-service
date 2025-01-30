from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from sqlalchemy import inspect
from agents.utils import *

class SQLgeneration:
    def __init__(self):
        self.engine = get_engine_for_chinook_db()
        self.db_schema = self._get_db_schema()

        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.prompt_template = self._create_prompt_template()

    def _get_db_schema(self):
        inspector = inspect(self.engine)
        schema = []
        for table_name in inspector.get_table_names():
            columns = [f"{col['name']} ({col['type']})" for col in inspector.get_columns(table_name)]
            schema.append(f"Table: {table_name}\nColumns: {', '.join(columns)}")
        return "\n\n".join(schema)
    

    def _create_prompt_template(self):
        system_template = """
        You are an expert SQL assistant. Based on the given database schema and the user's natural language query,generate a valid SQL query.
        
        Instructions:
        1. Convert the user's natural language question into an SQL query.
        2. Use only the columns and tables available in the provided schema.
        3. Make sure the SQL syntax is correct for a standard SQL database (e.g. SQLite)..
        4. Only generate the SQL query; do not execute it.
        5. Do not include any explanations or additional text; provide only the SQL query.
        """
        
        human_template = """
        Database Schema:
        {db_schema}

        User's question: {user_input}

        SQL Query:
        """
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        
        prompt_template = ChatPromptTemplate.from_messages([system_message, human_message])
        return prompt_template


    def generate_sql(self, user_input: str):
        prompt = self.prompt_template.format_messages(
            db_schema=self.db_schema,
            user_input=user_input
        )
        response = self.llm(prompt)
        return response.content.strip()