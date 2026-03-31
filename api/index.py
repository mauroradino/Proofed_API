from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .utils import get_repo_authenticity
# Importamos el cliente de GenLayer (ajustado según lo que vimos antes)
from genlayer_py import create_client
from genlayer_py.chains import testnet_bradbury

app = FastAPI()

# Configuración GenLayer
client = create_client(chain=testnet_bradbury)
CONTRACT_ADDR = "0x5D0f832B8B8220CB422ea8fdd3856cEcAE74B03f"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit_and_evaluate")
def submit_and_evaluate(challenge_id: str, url: str):
    """
    Este es el endpoint clave. Envía el repo al contrato y dispara 
    el consenso de los 3 LLMs.
    """
    try:
        # 1. Registramos el repo en el contrato (Llama a 'submit' de Roheemah)
        # Esto guarda el github_url en el estado del contrato
        client.write_contract(
            address=CONTRACT_ADDR,
            function_name="submit",
            args=[challenge_id, url]
        )

        # 2. Pedimos la evaluación (Llama a 'evaluate' de Roheemah)
        # AQUÍ es donde los 3 LLMs se ponen de acuerdo internamente
        client.write_contract(
            address=CONTRACT_ADDR,
            function_name="evaluate",
            args=[challenge_id]
        )

        return {"status": "success", "message": "Evaluación por consenso iniciada"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_result")
def get_result(challenge_id: str, user_address: str):
    """
    Consultamos el veredicto final guardado en la blockchain.
    """
    try:
        # Llamamos a 'get_submission' de Roheemah
        result = client.read_contract(
            address=CONTRACT_ADDR,
            function_name="get_submission",
            args=[challenge_id, user_address]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))