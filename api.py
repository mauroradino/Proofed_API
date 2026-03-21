from fastapi import FastAPI
from main import get_instructions as get_instructions_from_agent
from main import check_repo as evaluator

app = FastAPI()



@app.post("/get_instruction")
def get_instructions(theme: str):
    instruction = get_instructions_from_agent(theme)
    return {"instruction": instruction}

@app.post("/check_repo")
def check_repo(url: str, instruction: str):
    response = evaluator(url, instruction)
    return response
