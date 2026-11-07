
from retrieval.graph_retriever import GraphRetriever
from question_processing.question_router import QuestionRouter
from question_processing.answer_generator import AnswerGenerator
from question_processing.response_formatter import ResponseFormatter


def main():

    print("\n" + "=" * 60)
    print("       GRAPHRAG ENTERPRISE KNOWLEDGE SYSTEM")
    print("=" * 60)

    retriever = None

    try:
        # 1. Initialize Neo4j connection
        print("\nConnecting to Neo4j...")

        retriever = GraphRetriever()

        print("Neo4j connection successful!")

        # 2. Initialize project components
        router = QuestionRouter(retriever)

        answer_generator = AnswerGenerator(retriever)

        formatter = ResponseFormatter()

        print("\nAll system components initialized successfully!")

        print("\n" + "-" * 60)
        print("You can now ask questions about manufacturing incidents.")
        print("Type 'exit' to close the application.")
        print("-" * 60)

        # 3. Continuous question-answering loop
        while True:

            question = input("\nAsk your question: ").strip()

            if not question:
                print("Please enter a question.")
                continue

            if question.lower() in ["exit", "quit"]:
                print("\nClosing GraphRAG system...")
                break

            try:
                # Step 1: Understand the question
                route_result = router.route_question(question)

                # Step 2: Retrieve relevant graph evidence
                answer_result = answer_generator.generate_answer(
                    route_result
                )

                # Step 3: Format the retrieved evidence
                response = formatter.format_response(answer_result)

                # Step 4: Display the response
                print("\n" + "=" * 60)
                print("ANSWER")
                print("=" * 60)
                print(response)
                print("=" * 60)

            except Exception as error:
                print("\nAn error occurred while processing your question.")
                print("Error:", error)

    except Exception as error:
        print("\nCould not initialize the GraphRAG system.")
        print("Error:", error)

    finally:
        # 4. Close Neo4j connection
        if retriever is not None:
            retriever.driver.close()
            print("\nNeo4j connection closed.")

        print("GraphRAG Enterprise Knowledge System stopped.")


if __name__ == "__main__":
    main()
