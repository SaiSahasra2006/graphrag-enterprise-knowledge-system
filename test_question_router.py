
from retrieval.graph_retriever import GraphRetriever
from question_processing.question_router import QuestionRouter


retriever = GraphRetriever()
router = QuestionRouter(retriever)

try:
    test_questions = [
        "What happened in INC001?",
        "What are the common causes in Hydraulic Press #3?",
        "Show incidents in Hydraulic Press #3",
        "Tell me about the machine"
    ]

    for question in test_questions:

        print("\nQuestion:", question)

        result = router.route_question(question)

        print("Router result:", result)

finally:
    retriever.close()
