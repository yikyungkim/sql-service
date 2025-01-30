# import json
# import os
# from impala.dbapi import connect

# def connect_to_impala_db():
#     conn = connect(
#         host='xxx.com',
#         port=xxx,
#     )
#     return conn

# class DatabaseSchemaCache:
#     def __init__(self, cache_file='db_schema_cache.json'):
#         self.cache_file = cache_file
#         self.schema_cache = self._load_cache()

#     def _load_cache(self):
#         if os.path.exists(self.cache_file):
#             with open(self.cache_file, 'r') as f:
#                 return json.load(f)
#         return {}

#     def _save_cache(self):
#         with open(self.cache_file, 'w') as f:
#             json.dump(self.schema_cache, f, indent=2)

#     def get_schema(self, conn):
#         cache_key = 'impala_schema'
        
#         if cache_key in self.schema_cache:
#             return self.schema_cache[cache_key]
        
#         cursor = conn.cursor()
        
#         schema = {}
#         cursor.execute("SHOW DATABASES")
#         databases = [row[0] for row in cursor.fetchall()]
        
#         for db in databases:
#             cursor.execute(f"SHOW TABLES IN {db}")
#             tables = [row[0] for row in cursor.fetchall()]
            
#             for table in tables:
#                 cursor.execute(f"DESCRIBE {db}.{table}")
#                 columns = [row[0] for row in cursor.fetchall()]
#                 schema[f"{db}.{table}"] = columns
        
#         self.schema_cache[cache_key] = schema
#         self._save_cache()
        
#         return schema

    # def _get_db_schema(self):
    #     cursor = self.conn.cursor()
    #     cursor.execute("SHOW TABLES")
    #     tables = cursor.fetchall()
        
    #     schema = []
    #     for table in tables:
    #         table_name = table[0]
    #         cursor.execute(f"DESCRIBE {table_name}")
    #         columns = cursor.fetchall()
    #         column_info = [f"{col[0]} ({col[1]})" for col in columns]
    #         schema.append(f"Table: {table_name}\nColumns: {', '.join(column_info)}")
        
    #     cursor.close()
    #     return "\n\n".join(schema)

####################################################################################################

import sqlite3
import requests
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from functools import lru_cache

@lru_cache(maxsize=1)
def get_engine_for_chinook_db():
    """Pull SQL file, populate in-memory database, and create engine. Cached to avoid repeated downloads."""
    url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
    response = requests.get(url)
    sql_script = response.text

    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


import json
import os
from sqlalchemy import inspect

class DatabaseSchemaCache:
    def __init__(self, cache_file='db_schema_cache.json'):
        self.cache_file = cache_file
        self.schema_cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.schema_cache, f, indent=2)

    def get_schema(self, engine):
        cache_key = 'chinook_schema'
        
        if cache_key in self.schema_cache:
            return self.schema_cache[cache_key]
        
        inspector = inspect(engine)
        
        schema = {}
        for table_name in inspector.get_table_names():
            columns = [column['name'] for column in inspector.get_columns(table_name)]
            schema[table_name] = columns
        
        self.schema_cache[cache_key] = schema
        self._save_cache()
        
        return schema