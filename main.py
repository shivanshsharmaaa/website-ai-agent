
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import run_agent
from file_tools import WORKSPACE

app = FastAPI(title="Website Builder AI Agent")

# Frontend ko baad mein connect karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BuildRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=3000,
        description="Describe the website you want to build"
    )


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Website Builder AI Agent is running"
    }


@app.post("/build")
def build_website(request: BuildRequest):
    try:
        result = run_agent(request.message)

        return {
            "success": True,
            "reply": result,
            "workspace": str(WORKSPACE)
        }

    except Exception as error:
        print("Agent error:", repr(error))
        raise HTTPException(
            status_code=500,
            detail="Agent request failed. Check the backend terminal."
        )




