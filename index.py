from main import get_instructions as get_instructions_from_agent
from fastapi.middleware.cors import CORSMiddleware
from main import check_repo as evaluator
from utils import get_repo_authenticity
from fastapi import FastAPI

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_instruction")
def get_instructions(theme: str):
    instruction = get_instructions_from_agent(theme)
    return {"instruction": instruction}

@app.post("/check_repo")
def check_repo(url: str, instruction: str):
    response = evaluator(url, instruction)
    return response

@app.post("/check_authenticity")
def check_authenticity(owner: str, repo:str):
    response = get_repo_authenticity(owner, repo)
    return response