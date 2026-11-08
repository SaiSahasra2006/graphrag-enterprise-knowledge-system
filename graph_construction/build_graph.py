
import json
import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT_ROOT / "data" / "processed_incidents.json"

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
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

    # 1. Create Equipment nodes
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

    # 2. Create Device nodes and connect them to Equipment

    def create_device_relationship(self, equipment_name, device_name, incident_id):
        query = """
        MERGE (e:Equipment {name: $equipment})
        MERGE (d:Device {name: $device})
        MERGE (e)-[:HAS_DEVICE]->(d)

        MERGE (i:Incident {incident_id: $incident_id})
        MERGE (i)-[:INVOLVES_DEVICE]->(d)
        """

        with self.driver.session(database="graphrag") as session:
            session.run(
                query,
                equipment=equipment_name,
                device=device_name,
                incident_id=incident_id
            )


    def build_device_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        for record in records:
            equipment = record.get("equipment")
            device = record.get("device")

            if equipment and device:
                self.create_device_relationship(
                    equipment,
                    device,
                    record["incident_id"]
            )
        print("Device nodes and equipment relationships created!")

    # 3. Create Incident nodes and connect them to Equipment
    def create_incident_relationship(self, equipment_name, incident_id):
        query = """
        MERGE (e:Equipment {name: $equipment})
        MERGE (i:Incident {incident_id: $incident_id})
        MERGE (e)-[:EXPERIENCED]->(i)
        """

        with self.driver.session(database="graphrag") as session:
            session.run(
                query,
                equipment=equipment_name,
                incident_id=incident_id
            )

    def build_incident_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        incident_count = 0

        for record in records:
            equipment = record.get("equipment")
            incident_id = record.get("incident_id")

            if equipment and incident_id:
                self.create_incident_relationship(
                    equipment,
                    incident_id
                )
                incident_count += 1

        print(f"Incident nodes and relationships created: {incident_count}")
    def build_incident_properties(self):
        """Store detailed incident information as node properties."""

        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        SET
            i.time = $time,
            i.discoverer = $discoverer,
            i.summary = $summary,
            i.details = $details,
            i.impact_scope = $impact_scope
        """

        with self.driver.session(database="graphrag") as session:
            for record in records:
                session.run(
                    query,
                    incident_id=record["incident_id"],
                    time=record.get("time"),
                    discoverer=record.get("discoverer"),
                    summary=record.get("summary"),
                    details=record.get("details"),
                    impact_scope=record.get("impact_scope")
                )

        print("Additional incident properties stored successfully!")

    # 4. Create Incident Category nodes and relationships
    def build_category_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        MERGE (c:IncidentCategory {name: $category})
        MERGE (i)-[:BELONGS_TO]->(c)
        """

        with self.driver.session(database="graphrag") as session:
            for record in records:
                session.run(
                    query,
                    incident_id=record["incident_id"],
                    category=record["category"]
                )

        print("Incident category nodes and relationships created!")
    # 5. Create Root Cause nodes and relationships
    def build_cause_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        MERGE (c:RootCause {description: $cause})
        MERGE (i)-[:HAS_CAUSE]->(c)
        """

        relationship_count = 0

        with self.driver.session(database="graphrag") as session:
            for record in records:
                for cause in record.get("causes", []):
                    if cause.strip():
                        session.run(
                            query,
                            incident_id=record["incident_id"],
                            cause=cause.strip()
                        )
                        relationship_count += 1

        print(f"Root cause relationships created: {relationship_count}")
    # 6. Create Immediate Action nodes and relationships
    def build_immediate_action_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        MERGE (a:ImmediateAction {description: $action})
        MERGE (i)-[:RESOLVED_BY]->(a)
        """

        relationship_count = 0

        with self.driver.session(database="graphrag") as session:
            for record in records:
                for action in record.get("immediate_actions", []):
                    if action.strip():
                        session.run(
                            query,
                            incident_id=record["incident_id"],
                            action=action.strip()
                        )
                        relationship_count += 1

        print(
            f"Immediate action relationships created: {relationship_count}"
        )
    # 7. Create Permanent Action nodes and relationships
    def build_permanent_action_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        MERGE (a:PermanentAction {description: $action})
        MERGE (i)-[:PREVENTED_BY]->(a)
        """

        relationship_count = 0

        with self.driver.session(database="graphrag") as session:
            for record in records:
                for action in record.get("permanent_actions", []):
                    if action.strip():
                        session.run(
                            query,
                            incident_id=record["incident_id"],
                            action=action.strip()
                        )
                        relationship_count += 1

        print(
            f"Permanent action relationships created: {relationship_count}"
        )
    # 8. Create Location nodes and relationships
    def build_location_nodes(self):
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            records = json.load(file)

        query = """
        MATCH (i:Incident {incident_id: $incident_id})
        MERGE (l:Location {name: $location})
        MERGE (i)-[:OCCURRED_AT]->(l)
        """

        relationship_count = 0

        with self.driver.session(database="graphrag") as session:
            for record in records:
                location = record.get("location", "").strip()

                if location:
                    session.run(
                        query,
                        incident_id=record["incident_id"],
                        location=location
                    )
                    relationship_count += 1

        print(
            f"Location relationships created: {relationship_count}"
        )
# Main execution
if __name__ == "__main__":
    builder = GraphBuilder()

    try:
        builder.build_equipment_nodes()
        builder.build_device_nodes()
        builder.build_incident_nodes()
        builder.build_incident_properties()
        builder.build_category_nodes()
        builder.build_cause_nodes()
        builder.build_immediate_action_nodes()
        builder.build_permanent_action_nodes()
        builder.build_location_nodes()
    finally:
        builder.close()
