from neo4j import GraphDatabase
import os


class GraphRetriever:

    def __init__(self):
        self.uri = "bolt://localhost:7687"
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
    def retrieve_incident(self, incident_id):

        query = """
        MATCH (i:Incident {incident_id: $incident_id})

        OPTIONAL MATCH (e:Equipment)-[:EXPERIENCED]->(i)
        OPTIONAL MATCH (e)-[:HAS_DEVICE]->(d:Device)

        OPTIONAL MATCH (i)-[:BELONGS_TO]->(c:IncidentCategory)
        OPTIONAL MATCH (i)-[:HAS_CAUSE]->(cause:RootCause)
        OPTIONAL MATCH (i)-[:RESOLVED_BY]->(ia:ImmediateAction)
        OPTIONAL MATCH (i)-[:PREVENTED_BY]->(pa:PermanentAction)
        OPTIONAL MATCH (i)-[:OCCURRED_AT]->(l:Location)

        RETURN
            i.incident_id AS incident_id,
            collect(DISTINCT e.name) AS equipment,
            collect(DISTINCT d.name) AS devices,
            collect(DISTINCT c.name) AS categories,
            collect(DISTINCT cause.description) AS causes,
            collect(DISTINCT ia.description) AS immediate_actions,
            collect(DISTINCT pa.description) AS permanent_actions,
            collect(DISTINCT l.name) AS locations
        """

        with self.driver.session(database="graphrag") as session:
            result = session.run(query, incident_id=incident_id)
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
        results = retriever.retrieve_common_causes(
            "Hydraulic Press #3"
        )

        print("\nCommon Root Causes for Hydraulic Press #3:\n")

        for item in results:
            print(
                f"Cause: {item['cause']}\n"
                f"Incident Count: {item['incident_count']}\n"
                f"Incident IDs: {item['incident_ids']}\n"
            )

    finally:
        retriever.close()        