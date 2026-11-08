# GraphRAG Enterprise Knowledge System

An AI-powered enterprise knowledge assistant for manufacturing incident analysis using Neo4j Knowledge Graphs, graph-based retrieval, and a locally running Large Language Model (LLM).

## 1. Project Overview

The GraphRAG Enterprise Knowledge System helps users retrieve and understand manufacturing incident information through natural-language questions.

The system uses a manufacturing Root Cause Analysis (RCA) dataset containing 100 incident records. It stores structured information in a Neo4j knowledge graph and uses a local LLM to generate readable answers based on retrieved evidence.

### Key Features

- Manufacturing incident information retrieval.
- Equipment-based incident search.
- Root cause analysis.
- Common cause identification.
- Knowledge graph-based relationships.
- Natural-language question answering.
- Local LLM integration using Ollama.
- Interactive React chat interface.
- REST API using FastAPI.

## 2. System Architecture

The system follows this workflow:

1. Manufacturing RCA dataset is loaded and preprocessed.
2. Structured incident information is converted into a knowledge graph.
3. Neo4j stores incidents, equipment, devices, causes, actions, and locations.
4. The question router identifies the type of user question.
5. The graph retriever fetches relevant information from Neo4j.
6. Ollama with Qwen2.5 1.5B generates an answer using the retrieved evidence.
7. FastAPI returns the answer to the React frontend.

### Architecture Flow

```text
             User
               |
               v
        React Frontend
               |
               v
         FastAPI Backend
               |
               v
        Question Router
               |
               v
        Graph Retriever
               |
               v
          Neo4j Graph
               |
               v
       Retrieved Evidence
               |
               v
       Ollama LLM
       Qwen2.5 1.5B
               |
               v
       Generated Answer
               |
               v
        React Frontend
```

## 3. Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | React.js |
| Frontend Development Server | Vite |
| Backend | FastAPI |
| API Server | Uvicorn |
| Knowledge Graph Database | Neo4j |
| Graph Query Language | Cypher |
| Local LLM Runtime | Ollama |
| LLM Model | Qwen2.5 1.5B |
| Data Processing | Pandas |
| API Communication | REST API |

## 4. Dataset

The project uses the Manufacturing RCA dataset:

`data/ManufacturingRCA_doc.csv`

The dataset contains 100 manufacturing incident records and includes information such as:

- Incident ID
- Incident Category
- Equipment
- Device
- Root Cause
- Immediate Countermeasure
- Permanent Countermeasure
- Location

The preprocessing script cleans and structures the dataset before graph construction.

## 5. Knowledge Graph Structure

The Neo4j knowledge graph contains the following node types:

- Equipment
- Device
- Incident
- IncidentCategory
- RootCause
- ImmediateAction
- PermanentAction
- Location

### Relationships

- Equipment → HAS_DEVICE → Device
- Incident → INVOLVES_DEVICE → Device
- Equipment → EXPERIENCED → Incident
- Incident → BELONGS_TO → IncidentCategory
- Incident → HAS_CAUSE → RootCause
- Incident → RESOLVED_BY → ImmediateAction
- Incident → PREVENTED_BY → PermanentAction
- Incident → OCCURRED_AT → Location

## 6. Project Folder Structure

```text
graphrag-enterprise-knowledge-system/
│
├── api/
│   └── server.py
│
├── config/
│   └── database.py
│
├── data/
│   ├── ManufacturingRCA_doc.csv
│   └── processed_incidents.json
│
├── document_processing/
│   └── preprocess.py
│
├── graph_construction/
│   └── build_graph.py
│
├── retrieval/
│   └── graph_retriever.py
│
├── question_processing/
│   ├── answer_generator.py
│   ├── question_router.py
│   └── response_formatter.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── main.py
├── requirements.txt
├── README.md
└── .env
```

## 7. Installation and Setup

### Prerequisites

Install the following software:

- Python 3.12 or compatible version
- Node.js and npm
- Neo4j Desktop
- Ollama

### Step 1: Clone the Repository

```bash
git clone https://github.com/SaiSahasra2006/graphrag-enterprise-knowledge-system.git

cd graphrag-enterprise-knowledge-system
```

### Step 2: Create a Python Virtual Environment

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
```

### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure Neo4j

1. Open Neo4j Desktop.
2. Start your Neo4j DBMS.
3. Create or select the `graphrag` database.
4. Configure the database credentials.

Create a `.env` file in the project root:

```env
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=graphrag
```

Replace the password placeholder with your actual local Neo4j password.

Do not upload `.env` or database credentials to GitHub.

### Step 5: Preprocess the Dataset

Run:

```powershell
python .\document_processing\preprocess.py
```

This generates the processed incident data.

### Step 6: Build the Knowledge Graph

Run:

```powershell
python .\graph_construction\build_graph.py
```

This creates the manufacturing knowledge graph in Neo4j.

### Step 7: Install and Configure Ollama

Install Ollama and download the model:

```powershell
ollama pull qwen2.5:1.5b
```

Verify the model:

```powershell
ollama list
```

The project uses the locally hosted Qwen2.5 1.5B model for answer generation.

No OpenAI API key is required for the configured local LLM workflow.

### Step 8: Start the Backend

From the project root:

```powershell
uvicorn api.server:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Step 9: Start the Frontend

Open another terminal:

```powershell
cd frontend

npm install

npm run dev
```

Frontend URL:

`http://localhost:5173/`

Keep the backend and frontend terminals running while using the application.

## 8. API Endpoints

### Health Check

```http
GET /health
```

Checks whether the backend is running.

### Chat Endpoint

```http
POST /api/chat
```

Example request:

```json
{
  "question": "Show details for incident INC001"
}
```

Example questions:

- Show details for incident INC001.
- Show incidents for Hydraulic Press #3.
- What are the common causes for Hydraulic Press #3?

## 9. Testing

The integrated application was tested using the React frontend, FastAPI backend, Neo4j, and Ollama.

| Test Case | Result |
|---|---|
| Incident details retrieval | Passed |
| Equipment-based incident retrieval | Passed |
| Common cause identification | Passed |
| Ollama answer generation | Passed |
| FastAPI response | HTTP 200 OK |
| Frontend integration | Passed |

The three end-to-end LLM generation tests completed successfully.

## 10. Team Contributions

The project was developed collaboratively by three team members.

**Member 1 – Document Processing and Knowledge Graph Construction**
- Dataset preprocessing.
- Data cleaning and structuring.
- Neo4j knowledge graph construction.
- Graph node and relationship creation.

**Member 2 – Graph Retrieval and Question Processing**
- Graph retrieval implementation.
- Question routing.
- Answer generation pipeline.
- Response formatting.

**Member 3 – Frontend and LLM Integration**
- React frontend development.
- FastAPI backend development.
- Ollama integration.
- Local Qwen2.5 1.5B model configuration.
- Frontend and backend integration.
- End-to-end testing.

## 11. Future Enhancements

- Advanced semantic and vector-based retrieval.
- Improved question understanding.
- More manufacturing datasets.
- Advanced analytics and incident visualization.
- Authentication and user management.
- Production deployment and performance optimization.

## 12. Repository

GitHub:

https://github.com/SaiSahasra2006/graphrag-enterprise-knowledge-system

---

**GraphRAG Enterprise Knowledge System**

An intelligent manufacturing knowledge assistant combining Knowledge Graphs, graph-based retrieval, and locally hosted Large Language Models.