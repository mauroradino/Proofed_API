from anthropic import Anthropic
import os
from dotenv import load_dotenv
from prompt import auditor_agent_prompt, explorer_agent_prompt, instructions_agent_prompt
from tools import repo_tool, get_repo_files  

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


""" 
while True:
    user_input = input("\nUsuario: ")

    if user_input.lower() in ["salir", "exit", "quit"]:
        break

    chat_history.append({"role": "user", "content": user_input})

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system_prompt,
            messages=chat_history,
            tools=[repo_tool]
        )

        # Tool use: puede haber múltiples rondas (loop en vez de if)
        while response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input
            tool_use_id = tool_use.id

            # Guardamos la intención de Claude antes de ejecutar
            chat_history.append({"role": "assistant", "content": response.content})

            if tool_name == "get_repo_files":  # ✅ nombre correcto
                print(f"--- [SISTEMA] Analizando repositorio: {tool_input['github_url']} ---")
                import json
                resultado = get_repo_files(tool_input["github_url"])
                content = json.dumps(resultado, ensure_ascii=False)
            else:
                content = json.dumps({"error": f"Herramienta desconocida: {tool_name}"})

            chat_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": content,
                    }
                ],
            })

            # Nueva llamada con el resultado de la tool
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                system=system_prompt,
                messages=chat_history,
                tools=[repo_tool]
            )

        # Leer solo bloques de texto en la respuesta final ✅
        ai_text = next(
            (block.text for block in response.content if block.type == "text"),
            "No se obtuvo respuesta de texto."
        )

        print(f"\nClaude: {ai_text}")

        # Guardar respuesta final como string en el historial
        chat_history.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        print(f"Error: {e}") 
"""