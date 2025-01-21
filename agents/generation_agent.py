import os
# import cx_Oracle
import sqlite3
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

class sql_generation:
    def __init__(self):
        self.sql_generation = None

    """
    간단한 스키마 정보를 예시로 보관하고 반환하는 모듈.
    실제 환경에선 사내 DB의 테이블 목록, 컬럼 정보, 관계(ERD) 등을
    여기서 가져오거나, 동적으로 불러오도록 구성할 수 있다.
    """

    def get_schema_info(self,):
        """
        예시로 2개 테이블(User, Order)만 정의.
        실제 환경에서는 더 복잡한 스키마를 
        DB에서 직접 읽어오거나 Config, YAML, Excel 등에서 관리할 수 있음.
        """
        schema_info = {
            "tables": {
                "users": {
                    "columns": ["id", "name", "email", "created_at"],
                    "primary_key": "id",
                    "description": "유저 정보 테이블"
                },
                "orders": {
                    "columns": ["id", "user_id", "product_name", "price", "order_date"],
                    "primary_key": "id",
                    "description": "주문 정보 테이블, user_id가 users.id를 참조"
                }
            },
            "relationships": [
                # 예: users.id = orders.user_id
                {
                    "table1": "users",
                    "table2": "orders",
                    "relation": "users.id = orders.user_id"
                }
            ]
        }
        return schema_info


    def build_sql_generation_prompt(self, natural_lang_query: str, schema_info: dict) -> str:
        """
        사용자 자연어 질의와 테이블 스키마 정보를 기반으로
        LLM에 전달할 '지시(prompt)'를 구성.
        Oracle SQL의 특성을 반영할 수 있도록 수정.
        """

        # 테이블 스키마 정보를 문자열로 만들어 LLM에 전달
        schema_description_parts = []
        for table_name, table_meta in schema_info["tables"].items():
            columns = ", ".join(table_meta["columns"])
            schema_description_parts.append(
                f"Table Name: {table_name}\n"
                f"Columns: {columns}\n"
                f"Description: {table_meta['description']}\n"
            )
        schema_description = "\n".join(schema_description_parts)

        # relationship 정보도 추가
        relationship_parts = []
        for rel in schema_info["relationships"]:
            relationship_parts.append(f"{rel['table1']}.{rel['relation']}")
        relationship_description = "\n".join(relationship_parts)

        prompt_code = ChatPromptTemplate.from_messages([
            ("system", 
            "You are an expert SQL assistant. "
            "Based on the given database schema and the user's natural language query, "
            "generate a valid SQL query. "
            "Follow these rules:\n"
            "1. Use only the columns and tables available in the provided schema.\n"
            "2. If a JOIN is needed, use the relationships described.\n"
            "3. Make sure the SQL syntax is correct for a standard SQL database (e.g. SQLite)..\n"
            "4. Do not include additional commentary, only the SQL statement."
            ),
            ("human", 
            "Here is the schema information: \n"
            "{schema_description}\n"
            "Here are the relationships between tables: \n"
            "{relationship_description}\n"
            "User's query: \n"
            "{natural_lang_query}\n"
            "Please generate the SQL query."
            )
        ])

        prompt = prompt_code.format_messages(
            schema_description=schema_description,
            relationship_description=relationship_description,
            natural_lang_query=natural_lang_query)

        # prompt_template = f"""
        # You are an expert SQL assistant for Oracle SQL. 
        # Based on the given database schema and the user's natural language query, 
        # generate a valid Oracle SQL query. 
        # Follow these rules:
        # 1. Use only the columns and tables available in the provided schema.
        # 2. If a JOIN is needed, use the relationships described.
        # 3. Make sure the SQL syntax is correct for Oracle SQL.
        # 4. Use Oracle-specific syntax for limiting rows (e.g., 'FETCH FIRST N ROWS ONLY' instead of 'LIMIT').
        # 5. If dealing with dates, use Oracle's SYSDATE or other appropriate functions.
        # 6. Do not include additional commentary, only the SQL statement.

        # -- Database Schema Info --
        # {schema_description}

        # -- Relationships Info --
        # {relationship_description}

        # -- User Query --
        # {natural_lang_query}

        # Provide only the SQL query as the output.
        # """

        return prompt


    def generate_sql(self, prompt: str) -> str:
        """
        LLM에게 prompt를 전달해 SQL을 생성한 뒤,
        결과(SQL 문자열)를 리턴.
        """

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=openai_api_key,
        )
        result = llm.predict_messages(prompt)
        sql_query = result.content

        return sql_query

    # """
    # DB 연결 및 쿼리 실행을 담당하는 모듈.
    # 여기서는 Oracle DB를 사용하도록 수정.
    # """
    # def execute_query(self, sql_query: str, db_user: str, db_password: str, db_host: str, db_port: int, db_service: str):
    #     """
    #     주어진 SQL 쿼리를 Oracle DB에 실행하고,
    #     결과(컬럼명, 로우 데이터)를 반환한다.
    #     """

    #     # Oracle DB 연결 URI 형식: 'username/password@hostname:port/service_name'
    #     dsn = cx_Oracle.makedsn(db_host, db_port, db_service)
    #     connection = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn)
    #     cursor = connection.cursor()

    #     try:
    #         cursor.execute(sql_query)
    #         # SELECT 결과 반환
    #         columns = [desc[0] for desc in cursor.description] if cursor.description else []
    #         rows = cursor.fetchall()
    #         connection.commit()
    #     except Exception as e:
    #         connection.rollback()
    #         raise e
    #     finally:
    #         cursor.close()
    #         connection.close()

    #     return columns, rows

# query_executor.py

    def execute_query(self, sql_query: str, db_path: str = "example.db"):
        """
        주어진 SQL 쿼리를 SQLite DB에 실행하고,
        결과(컬럼명, 로우 데이터)를 반환한다.
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(sql_query)
            # SELECT 결과 반환
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        return columns, rows
