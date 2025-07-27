from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_loader import agent

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or set your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str


@app.post("/ask")
async def ask_query(request: QueryRequest):
    try:
        result = agent.query(request.query)
        return {"result": str(result)}
    except Exception as e:
        return {"error": str(e)}
