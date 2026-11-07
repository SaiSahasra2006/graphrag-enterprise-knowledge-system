
import re


class QuestionRouter:

    def __init__(self, retriever):
        self.retriever = retriever
        self.equipment_list = retriever.get_all_equipment()

    def route_question(self, question):

        question_lower = question.lower()

        # 1. Check for an incident ID
        incident_match = re.search(
            r"\bINC\d+\b",
            question,
            re.IGNORECASE
        )

        if incident_match:
            return {
                "intent": "incident_details",
                "incident_id": incident_match.group().upper()
            }

        # 2. Identify equipment mentioned in the question
        matched_equipment = None

        for equipment in self.equipment_list:
            if equipment.lower() in question_lower:
                matched_equipment = equipment
                break

        if not matched_equipment:
            return {
                "intent": "unknown",
                "message": "Could not identify equipment or incident."
            }

        # 3. Identify the type of question
        if any(word in question_lower for word in [
            "common cause", "frequent cause",
            "recurring cause", "most common"
        ]):
            return {
                "intent": "common_causes",
                "equipment": matched_equipment
            }

        if any(word in question_lower for word in [
            "incident", "failure", "problem",
            "history", "issues", "occurred"
        ]):
            return {
                "intent": "equipment_incidents",
                "equipment": matched_equipment
            }

        return {
            "intent": "unknown",
            "message": "Could not identify the question type."
        }
