import os
import random
import sys
import time
from pymilvus import connections, Collection, DataType, FieldSchema, CollectionSchema
import mysql.connector
from pymongo import MongoClient
import numpy as np

def connect_milvus(max_retries=10, retry_delay=10):
    for attempt in range(max_retries):
        try:
            connections.connect(
                alias="default",
                host=os.getenv('MILVUS_HOST', 'vector_db'),
                port=os.getenv('MILVUS_PORT', '19530'),
                user=os.getenv('MILVUS_USERNAME'),
                password=os.getenv('MILVUS_PASSWORD')
            )
            print("Successfully connected to Milvus")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to connect to Milvus: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...", file=sys.stderr)
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to Milvus.", file=sys.stderr)
                raise

def insert_milvus_data():
    try:
        connect_milvus()
        dim = 128
        collection_name = "test_collection"
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
        ]
        schema = CollectionSchema(fields, "Test collection")
        collection = Collection(collection_name, schema)

        vectors = [[random.random() for _ in range(dim)] for _ in range(10)]
        collection.insert([vectors])
        print(f"Inserted {len(vectors)} vectors into Milvus")
    except Exception as e:
        print(f"Error inserting data into Milvus: {e}", file=sys.stderr)

def connect_mariadb():
    try:
        return mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'relational_db'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
	    collation='utf8mb4_unicode_520_ci'
        )
    except mysql.connector.Error as e:
        print(f"Error connecting to MariaDB: {e}", file=sys.stderr)
        raise

def insert_mariadb_data():
    try:
        conn = connect_mariadb()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            value INT
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci
        """)
        
        for i in range(10):
            cursor.execute(
                "INSERT INTO test_table (name, value) VALUES (%s, %s)",
                (f"test_name_{i}", random.randint(1, 100))
            )
        conn.commit()
        print(f"Inserted 10 rows into MariaDB")
    except mysql.connector.Error as e:
        print(f"Error inserting data into MariaDB: {e}", file=sys.stderr)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def connect_mongodb():
    try:
        return MongoClient(
            host=os.getenv('MONGODB_HOST', 'nosql_db'),
            port=int(os.getenv('MONGODB_PORT', 27017)),
            username=os.getenv('MONGODB_ROOT_USERNAME'),
            password=os.getenv('MONGODB_ROOT_PASSWORD')
        )
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}", file=sys.stderr)
        raise

def insert_mongodb_data():
    client = None
    try:
        client = connect_mongodb()
        db = client['test_database']
        collection = db['test_collection']

        documents = [
            {"name": f"test_doc_{i}", "value": random.randint(1, 100)}
            for i in range(10)
        ]
        result = collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}", file=sys.stderr)
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    try:
        insert_milvus_data()
        insert_mariadb_data()
        insert_mongodb_data()
        print("Data insertion completed successfully")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
