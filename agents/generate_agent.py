from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_community.utilities.sql_database import SQLDatabase

from agents.utils import *

class SQLgeneration():
    def __init__(self):
        # use impala -> cache
        # self.schema_cache = DatabaseSchemaCache()
        # self.conn = connect_to_impala_db()
        # self.schema = self.schema_cache.get_schema(self.conn)

        # use chinook, sqlite -> no cache
        # self.engine = get_engine_for_chinook_db()
        # self.db = SQLDatabase(self.engine)

        # use chinook, sqlite -> cache
        self.schema_cache = DatabaseSchemaCache()
        self.engine = get_engine_for_chinook_db()
        self.schema = self.schema_cache.get_schema(self.engine)
        self.db = SQLDatabase(self.engine)

        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.prefix = "사용자의 자연어 질문을 SQL로 변환하세요. SQL만 생성하고 실행하지 마세요."

    def create_custom_sql_agent(self):
        return create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            prefix=self.prefix
        )

    def generate_sql(self, user_input: str):
        agent = self.create_custom_sql_agent()
        result = agent.run(user_input)
        return result
