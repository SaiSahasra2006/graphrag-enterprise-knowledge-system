from neo4j import GraphDatabase
import os

PASSWORD = os.getenv("NEO4J_PASSWORD")

if not PASSWORD:
    raise ValueError("Please set the NEO4J_PASSWORD environment variable.")
# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"



class Neo4jConnection:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def verify_connection(self):
        self.driver.verify_connectivity()
        print("Successfully connected to Neo4j!")

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    connection = Neo4jConnection()

    try:
        connection.verify_connection()
    except Exception as error:
        print("Connection failed:", error)
    finally:
        connection.close()