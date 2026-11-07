
from retrieval.graph_retriever import GraphRetriever
from question_processing.question_router import QuestionRouter
from question_processing.answer_generator import AnswerGenerator


retriever = GraphRetriever()
router = QuestionRouter(retriever)
answer_generator = AnswerGenerator(retriever)

try:
    questions = [
        "What happened in INC001?",
        "What are the common causes in Hydraulic Press #3?",
        "Show incidents in Hydraulic Press #3",
        "Tell me about the machine",
        "What happened in INC999?"
    ]

    for question in questions:

        print("\n" + "=" * 60)
        print("QUESTION:", question)

        # Step 1: Understand the question
        route_result = router.route_question(question)
        print("\nROUTER:", route_result)

        # Step 2: Retrieve evidence
        answer = answer_generator.generate_answer(route_result)

        print("\nRETRIEVED RESULT:")
        print("Status:", answer["status"])

        if "evidence" in answer:
            evidence = answer["evidence"]
            print("Evidence:", evidence)
        else:
            print("Message:", answer["message"])

finally:
    retriever.close()
