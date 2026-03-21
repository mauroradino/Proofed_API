from anthropic import Anthropic
import os
from dotenv import load_dotenv
from prompt import auditor_agent_prompt, explorer_agent_prompt, instructions_agent_prompt
from tools import repo_tool, get_repo_files  
import uvicorn

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

chat_history = []

print("--- Chat iniciado (Escribe 'salir' para terminar) ---")



def get_instructions(theme):
    response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=instructions_agent_prompt,
            messages=[{"role": "user", "content": f"El tema que quiere evaluar el usuario es: {theme}"}]
        )
    return response.content[0].text

def check_repo(url, instructions):

    response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=explorer_agent_prompt,
            messages=[{"role": "user", "content": f"El repositorio que quiere evaluar el usuario es: {url}"}],
            tools=[repo_tool]
        )
    
    if response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name

            if tool_name == "get_repo_files": 
                import json
                resultado = get_repo_files(url)
                content = json.dumps(resultado, ensure_ascii=False)
                calification_response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1024,
                    system=auditor_agent_prompt,
                    messages=[{"role": "user", "content": f"La consigna que quiere evaluar el usuario es: {instructions}, y el contenido del repositorio es: {content}"}]
                )
                return calification_response.content[0].text
            else:
                content = json.dumps({"error": f"Herramienta desconocida: {tool_name}"})
                return "error en la calificacion"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)