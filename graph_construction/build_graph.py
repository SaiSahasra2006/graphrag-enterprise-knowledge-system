
import json
import os
from pathlib import Path
from neo4j import GraphDatabase

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT_ROOT / "data" / "processed_incidents.json"

# Neo4j connection
URI = "bolt://localhost:7687"
USERNAME = "neo4j"

# Set your Neo4j password in the environment variable
PASSWORD = os.getenv("NEO4J_PASSWORD")


class GraphBuilder:

    def __init__(self):
        if not PASSWORD:
            raise ValueError(
                "Please set the NEO4J_PASSWORD environment variable."
            )

        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def close(self):
        self.driver.close()

    # Create Equipment nodes
    def create_equipment(self, equipment_name):
        query = """
        MERGE (e:Equipment {name: $name})
        """

        with self.driver.session(database="graphrag") as session:
            session.run(query, name=equipment_name)

    def build_equipment_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        equipment_names = {
            record["equipment"]
            for record in records
            if record.get("equipment")
        }

        for equipment in equipment_names:
            self.create_equipment(equipment)

        print(f"Equipment nodes created: {len(equipment_names)}")

    # Create Device nodes and connect them to Equipment
    def create_device_relationship(self, equipment_name, device_name):
        query = """
        MERGE (e:Equipment {name: $equipment})
        MERGE (d:Device {name: $device})
        MERGE (e)-[:HAS_DEVICE]->(d)
        """

        with self.driver.session(database="graphrag") as session:
            session.run(
                query,
                equipment=equipment_name,
                device=device_name
            )

    def build_device_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        for record in records:
            equipment = record.get("equipment")
            device = record.get("device")

            if equipment and device:
                self.create_device_relationship(equipment, device)

        print("Device nodes and equipment relationships created!")


if __name__ == "__main__":
    builder = GraphBuilder()

    try:
        builder.build_equipment_nodes()
        builder.build_device_nodes()

    finally:
        builder.close()
