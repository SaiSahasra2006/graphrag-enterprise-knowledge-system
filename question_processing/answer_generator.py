
import json
import logging
import time
import urllib.request

logger = logging.getLogger(__name__)


class AnswerGenerator:

    def __init__(self, retriever):
        self.retriever = retriever
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "qwen2.5:1.5b"

    def _generate_with_ollama(self, intent, evidence, route_result):

        if intent == "incident_details":
            task = (
                "Explain the manufacturing incident, including its "
                "summary, details, equipment, root causes and actions."
            )
            llm_evidence = evidence

        elif intent == "equipment_incidents":
            task = (
                "Summarize the equipment incident history. State the "
                "total number of incidents and summarize the selected "
                "incident records. Clearly identify them as selected records."
            )

            # Keep the complete count but send only 10 records to the LLM.
            llm_evidence = {
                "total_incidents": len(evidence),
                "selected_incidents": [
                    {
                        "incident_id": item.get("incident_id"),
                        "categories": item.get("categories", []),
                        "causes": item.get("causes", [])[:2]
                    }
                    for item in evidence[:10]
                ]
            }

        elif intent == "common_causes":
            task = (
                "Explain the most frequently reported root causes. "
                "Include incident counts and related incident IDs."
            )

            llm_evidence = evidence[:10]

        else:
            return None

        prompt = f"""
Task: {task}

Equipment: {route_result.get('equipment', 'Not specified')}
Incident ID: {route_result.get('incident_id', 'Not specified')}

Neo4j evidence:
{json.dumps(llm_evidence, ensure_ascii=False, default=str)}

Rules:
- Use only the supplied evidence.
- Never invent facts, causes, dates, counts or incident IDs.
- Preserve numerical counts accurately.
- Clearly distinguish selected records from total records.
- Mention unavailable information when necessary.
- Write a concise, professional answer.
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a manufacturing knowledge assistant. "
                        "Answer strictly using the supplied Neo4j evidence. "
                        "Accuracy is more important than creativity."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.1,
                "num_ctx": 2048,
                "num_predict": 200
            }
        }

        request = urllib.request.Request(
            self.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            start_time = time.perf_counter()

            with urllib.request.urlopen(
                request,
                timeout=300
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            elapsed = time.perf_counter() - start_time

            answer = result.get("message", {}).get(
                "content", ""
            ).strip()

            if answer:
                logger.info(
                    "Ollama generated answer in %.2f seconds.",
                    elapsed
                )
                return answer

            return None

        except Exception:
            logger.exception(
                "Ollama generation failed. Using evidence fallback."
            )
            return None

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

        # 2. Retrieve equipment incidents
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

        # 3. Retrieve common causes
        elif intent == "common_causes":

            equipment = route_result.get("equipment")

            result = self.retriever.retrieve_common_causes(equipment)

            if not result:
                return {
                    "status": "not_found",
                    "message": f"No common causes found for {equipment}."
                }

        # 4. Unsupported questions
        else:

            return {
                "status": "unsupported",
                "message": route_result.get(
                    "message",
                    "Sorry, I could not understand your question."
                )
            }

        # 5. Generate answer using Ollama
        llm_answer = self._generate_with_ollama(
            intent,
            result,
            route_result
        )

        if llm_answer:
            logger.info("Ollama successfully generated the answer.")
        else:
            logger.warning("Ollama failed. Using evidence fallback.")

        return {
            "status": "success",
            "intent": intent,
            "evidence": result,
            "llm_answer": llm_answer,
            "llm_used": llm_answer is not None
        }
