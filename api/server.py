
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from retrieval.graph_retriever import GraphRetriever
from question_processing.question_router import QuestionRouter
from question_processing.answer_generator import AnswerGenerator
from question_processing.response_formatter import ResponseFormatter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    retriever = None

    try:
        logger.info("Connecting to Neo4j...")

        retriever = GraphRetriever()

        router = QuestionRouter(retriever)
        answer_generator = AnswerGenerator(retriever)
        formatter = ResponseFormatter()

        app.state.router = router
        app.state.answer_generator = answer_generator
        app.state.formatter = formatter

        logger.info("GraphRAG components initialized successfully.")

        yield

    finally:
        if retriever is not None:
            retriever.close()
            logger.info("Neo4j connection closed.")


app = FastAPI(
    title="GraphRAG Enterprise Knowledge System API",
    description="API for querying enterprise manufacturing knowledge.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@app.get("/")
def home():
    return {
        "message": "GraphRAG Enterprise Knowledge System API is running."
    }


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/api/chat")
def chat(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        route_result = app.state.router.route_question(question)

        answer_result = app.state.answer_generator.generate_answer(
            route_result
        )

        response = app.state.formatter.format_response(answer_result)

        return {
            "status": answer_result.get("status", "unknown"),
            "answer": response
        }

    except Exception:
        logger.exception("Error while processing question.")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question."
        )
