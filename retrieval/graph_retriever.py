from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class GraphRetriever:

    def __init__(self):
        self.uri = "bolt://127.0.0.1:7687"
        self.username = "neo4j"
        self.password = os.getenv("NEO4J_PASSWORD")

        if not self.password:
            raise ValueError(
                "Please set the NEO4J_PASSWORD environment variable."
            )

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    def close(self):
        self.driver.close()

    def get_all_equipment(self):

        query = """
        MATCH (e:Equipment)
        RETURN e.name AS equipment
        ORDER BY equipment
        """

        with self.driver.session(database="graphrag") as session:
            result = session.run(query)
            return [record["equipment"] for record in result]

    def retrieve_incident(self, incident_id):

        query = """
            MATCH (i:Incident {incident_id: $incident_id})

            OPTIONAL MATCH (e:Equipment)-[:EXPERIENCED]->(i)
            OPTIONAL MATCH (i)-[:INVOLVES_DEVICE]->(d:Device)

            OPTIONAL MATCH (i)-[:BELONGS_TO]->(c:IncidentCategory)
            OPTIONAL MATCH (i)-[:HAS_CAUSE]->(cause:RootCause)
            OPTIONAL MATCH (i)-[:RESOLVED_BY]->(ia:ImmediateAction)
            OPTIONAL MATCH (i)-[:PREVENTED_BY]->(pa:PermanentAction)
            OPTIONAL MATCH (i)-[:OCCURRED_AT]->(l:Location)

            RETURN
                i.incident_id AS incident_id,
                i.time AS time,
                i.discoverer AS discoverer,
                i.summary AS summary,
                i.details AS details,
                i.impact_scope AS impact_scope,
                collect(DISTINCT e.name) AS equipment,
                collect(DISTINCT d.name) AS devices,
                collect(DISTINCT c.name) AS categories,
                collect(DISTINCT cause.description) AS causes,
                collect(DISTINCT ia.description) AS immediate_actions,
                collect(DISTINCT pa.description) AS permanent_actions,
                collect(DISTINCT l.name) AS locations
            """


        with self.driver.session(database="graphrag") as session:
            result = session.run(
                query,
                incident_id=incident_id
            )
            record = result.single()

        if not record or record["incident_id"] is None:
            return None

        return record.data()

    def retrieve_incidents_by_equipment(self, equipment_name):

        query = """
        MATCH (e:Equipment {name: $equipment_name})-[:EXPERIENCED]->(i:Incident)

        OPTIONAL MATCH (i)-[:BELONGS_TO]->(c:IncidentCategory)
        OPTIONAL MATCH (i)-[:HAS_CAUSE]->(cause:RootCause)

        RETURN
            e.name AS equipment,
            i.incident_id AS incident_id,
            collect(DISTINCT c.name) AS categories,
            collect(DISTINCT cause.description) AS causes

        ORDER BY incident_id
        """

        with self.driver.session(database="graphrag") as session:
            result = session.run(
                query,
                equipment_name=equipment_name
            )

            return [record.data() for record in result]

    def retrieve_common_causes(self, equipment_name):

        query = """
        MATCH (e:Equipment {name: $equipment_name})
              -[:EXPERIENCED]->(i:Incident)
              -[:HAS_CAUSE]->(cause:RootCause)

        RETURN
            cause.description AS cause,
            count(DISTINCT i) AS incident_count,
            collect(DISTINCT i.incident_id) AS incident_ids

        ORDER BY incident_count DESC, cause
        """

        with self.driver.session(database="graphrag") as session:
            result = session.run(
                query,
                equipment_name=equipment_name
            )

            return [record.data() for record in result]


if __name__ == "__main__":

    retriever = GraphRetriever()

    try:
        # Test 1: Retrieve one incident
        print("\n========== TEST 1: INCIDENT DETAILS ==========")

        result = retriever.retrieve_incident("INC001")

        if result:
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print("Incident not found!")

        # Test 2: Retrieve incidents by equipment
        print("\n========== TEST 2: INCIDENTS BY EQUIPMENT ==========")

        incidents = retriever.retrieve_incidents_by_equipment(
            "Hydraulic Press #3"
        )

        print("Total incidents:", len(incidents))

        for incident in incidents:
            print(incident)

        # Test 3: Retrieve common causes
        print("\n========== TEST 3: COMMON CAUSES ==========")

        causes = retriever.retrieve_common_causes(
            "Hydraulic Press #3"
        )

        for cause in causes:
            print(cause)
        print("\nAvailable Equipment:")
        print(retriever.get_all_equipment())

    finally:
        retriever.close()
