
class AnswerGenerator:

    def __init__(self, retriever):
        self.retriever = retriever

    def generate_answer(self, route_result):

        intent = route_result.get("intent")

        # 1. Retrieve a specific incident
        if intent == "incident_details":

            incident_id = route_result.get("incident_id")

            result = self.retriever.retrieve_incident(incident_id)

            if not result:
                return {
                    "status": "not_found",
                    "message": f"No incident found with ID {incident_id}."
                }

            return {
                "status": "success",
                "intent": intent,
                "evidence": result
            }

        # 2. Retrieve incidents associated with equipment
        elif intent == "equipment_incidents":

            equipment = route_result.get("equipment")

            result = self.retriever.retrieve_incidents_by_equipment(
                equipment
            )

            if not result:
                return {
                    "status": "not_found",
                    "message": f"No incidents found for {equipment}."
                }

            return {
                "status": "success",
                "intent": intent,
                "equipment": equipment,
                "evidence": result
            }

        # 3. Retrieve common causes
        elif intent == "common_causes":

            equipment = route_result.get("equipment")

            result = self.retriever.retrieve_common_causes(equipment)

            if not result:
                return {
                    "status": "not_found",
                    "message": f"No common causes found for {equipment}."
                }

            return {
                "status": "success",
                "intent": intent,
                "equipment": equipment,
                "evidence": result
            }

        # 4. Handle unsupported questions
        else:

            return {
                "status": "unsupported",
                "message": route_result.get(
                    "message",
                    "Sorry, I could not understand your question."
                )
            }
