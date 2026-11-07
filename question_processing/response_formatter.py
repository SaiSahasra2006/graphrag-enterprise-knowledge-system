class ResponseFormatter:

    def format_response(self, result):

        status = result.get("status")

        if status == "not_found":
            return result.get(
                "message",
                "No matching records were found."
            )

        if status == "unsupported":
            return result.get(
                "message",
                "Sorry, I could not understand your question."
            )

        if status != "success":
            return result.get(
                "message",
                "Sorry, I could not process your question."
            )

        evidence = result.get("evidence", {})
        intent = result.get("intent")

        if intent == "incident_details":
            return self._format_incident(evidence)

        elif intent == "equipment_incidents":
            return self._format_equipment_incidents(evidence)

        elif intent == "common_causes":
            return self._format_common_causes(evidence)

        return "I could not understand the retrieved information."

    def _format_incident(self, data):

        response = []

        response.append(
            f"Incident: {data.get('incident_id', 'Unknown')}"
        )

        response.append(
            f"Date and time: {data.get('time', 'Not available')}"
        )

        response.append(
            f"Summary: {data.get('summary', 'Not available')}"
        )

        response.append(
            f"Details: {data.get('details', 'Not available')}"
        )

        response.append(
            f"Equipment: {', '.join(data.get('equipment', [])) or 'Not available'}"
        )

        response.append(
            f"Devices: {', '.join(data.get('devices', [])) or 'Not available'}"
        )

        response.append(
            f"Location: {', '.join(data.get('locations', [])) or 'Not available'}"
        )

        response.append(
            f"Impact: {data.get('impact_scope', 'Not available')}"
        )

        response.append("\nRoot causes:")
        for cause in data.get("causes", []):
            response.append(f"- {cause}")

        response.append("\nImmediate countermeasures:")
        for action in data.get("immediate_actions", []):
            response.append(f"- {action}")

        response.append("\nPermanent countermeasures:")
        for action in data.get("permanent_actions", []):
            response.append(f"- {action}")

        return "\n".join(response)

    def _format_equipment_incidents(self, data):

        if not data:
            return "No incidents were found for this equipment."

        response = [
            f"Total incidents found: {len(data)}",
            "\nIncident records:"
        ]

        for incident in data:
            incident_id = incident.get("incident_id", "Unknown")
            categories = incident.get("categories", [])
            causes = incident.get("causes", [])

            response.append(f"\nIncident: {incident_id}")

            if categories:
                response.append(f"Categories: {', '.join(categories)}")

            if causes:
                response.append(f"Causes: {', '.join(causes)}")

        return "\n".join(response)

    

    def _format_common_causes(self, data):

        if not data:
            return "No common causes were found."

        response = ["Most frequently reported causes:"]

        # Display only the top 10 causes
        for index, item in enumerate(data[:10], start=1):

            cause = item.get("cause", "Unknown cause")

            # Match the actual GraphRetriever field name
            count = item.get("incident_count", 0)

            incident_ids = item.get("incident_ids", [])

            response.append(
                f"\n{index}. {cause}"
                f"\n   Number of incidents: {count}"
                f"\n   Related incidents: {', '.join(incident_ids)}"
            )

        return "\n".join(response)
