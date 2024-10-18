# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
import logging
from databases import Database

# We are enabling both sql_lite and postgresql databases
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_LITE_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../db/hlth_demo.db')}"
sql_lite_database = Database(SQL_LITE_DATABASE_URL)

app = FastAPI()
class SQLQuery(BaseModel):
    query: str

ENV = os.getenv('ENV')

VERSION = "0.1.3_hybrid"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Configure CORS
origins = [
    "http://localhost:3000",  # React app running on localhost
    "http://127.0.0.1:3000",  # React app running on localhost
    "https://delightful-bay-025c9560f.5.azurestaticapps.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def connect_to_db() -> asyncpg.Connection:
    """Connect to the PostgreSQL database."""
    sslmode = 'require' if ENV == 'dev' else 'disable'
    database = os.getenv('DB_NAME')
    host = os.getenv('DB_HOST')

    try:
        conn = await asyncpg.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=database,
            host=host,
            port=os.getenv('DB_PORT'),
            ssl=sslmode
        )
        logging.info(f"Successfully connected to the database. db: {database}. host: {host}")  
        return conn
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL database: {e}")
        raise

# API Endpoint to get table sizes
@app.get("/api/tables")
async def get_table_sizes():
    conn = await connect_to_db()
    try:
        # SQL query to fetch all tables and their sizes
        query = """
            select * from silver.ref_geography limit 10;
        """
        tables = await conn.fetch(query)
        return {"tables": tables}
    finally:
        await conn.close()

@app.get("/api/testtables")
async def get_tables():
    return [
        {"id": 1, "name": "Table1", "data": {"key1": "value1", "key2": "value2"}},
        {"id": 2, "name": "Table2", "data": {"key1": "value3", "key2": "value4"}}
    ]

@app.get("/api/silvertables")
async def get_tables():
    return [
        {
            "name": "Visit Data",
            "fields": [
                {"name": "Field1", "description": "Description1", "selected": False},
                {"name": "Field2", "description": "Description2", "selected": False}
            ]
        },
        {
            "name": "Provider Data",
            "fields": [
                {"name": "Field1", "description": "Description1", "selected": False},
                {"name": "Field2", "description": "Description2", "selected": False}
            ]
        }
    ]

@app.get("/api/listtables")
async def get_list_tables():
    conn = await connect_to_db()
    try:
        query = """
        SELECT 
            table_name, 
            column_name
        FROM 
            information_schema.columns
        WHERE 
            table_schema = 'silver'
        ORDER BY 
            table_name, 
            ordinal_position;
        """
        tables_and_fields = await conn.fetch(query)
        return tables_and_fields
    finally:
        await conn.close()

@app.get("/api/ping")
async def ping():
    return {"ping": "pong from Version " + VERSION}

@app.on_event("startup")
async def startup_event():
    logging.info("FastAPI application has started.")

@app.get("/api/sl_tables")
async def get_table_metadata():
    try:
        query = "SELECT * FROM table_metadata"
        result = await sql_lite_database.fetch_all(query=query)
        return {"results": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/sl_execute_sql")
async def execute_sql(sql_query: SQLQuery):
    logging.info(f"Executing SQL query: {sql_query.query}")
    try:
        result = await sql_lite_database.fetch_all(query=sql_query.query)
        return {"results": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))