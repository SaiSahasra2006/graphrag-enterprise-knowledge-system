from question_processing.response_formatter import ResponseFormatter

formatter = ResponseFormatter()

# Test 1: Incident details
incident_result = {
    "status": "success",
    "intent": "incident_details",
    "evidence": {
        "incident_id": "INC001",
        "time": "2024/2/1 8:30",
        "summary": "Conveyor motor stopped.",
        "details": "Motor stopped due to overload.",
        "equipment": ["Hydraulic Press #3"],
        "devices": ["Product Discharge Conveyor"],
        "locations": ["Processing A Line"],
        "impact_scope": "Production loss",
        "causes": ["Motor overload"],
        "immediate_actions": ["Reset motor"],
        "permanent_actions": ["Improve motor inspection"]
    }
}

print("\nTEST 1: INCIDENT DETAILS")
print(formatter.format_response(incident_result))


# Test 2: Common causes
causes_result = {
    "status": "success",
    "intent": "common_causes",
    "evidence": [
        {
            "cause": "Insufficient functional check of sensor",
            "count": 5,
            "incident_ids": ["INC052", "INC054"]
        }
    ]
}

print("\nTEST 2: COMMON CAUSES")
print(formatter.format_response(causes_result))


# Test 3: Equipment incidents
equipment_result = {
    "status": "success",
    "intent": "equipment_incidents",
    "evidence": [
        {
            "incident_id": "INC001",
            "categories": ["Mechanical"],
            "causes": ["Motor overload"]
        }
    ]
}

print("\nTEST 3: EQUIPMENT INCIDENTS")
print(formatter.format_response(equipment_result))


# Test 4: Incident not found
not_found_result = {
    "status": "not_found",
    "message": "No incident found with ID INC999."
}

print("\nTEST 4: NOT FOUND")
print(formatter.format_response(not_found_result))


# Test 5: Unsupported question
unsupported_result = {
    "status": "unsupported",
    "message": "Could not identify the question type."
}

print("\nTEST 5: UNSUPPORTED QUESTION")
print(formatter.format_response(unsupported_result))