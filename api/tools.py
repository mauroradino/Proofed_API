import requests
import re

def get_repo_files(github_url: str) -> dict:
    """
    Recibe una URL de GitHub (cualquier formato) y devuelve
    el contenido real de los archivos relevantes.
    """
    # Extraer user/repo de la URL
    match = re.search(r"github\.com/([^/]+)/([^/]+)", github_url)
    if not match:
        return {"error": "URL de GitHub inválida"}
    
    user, repo = match.group(1), match.group(2).rstrip("/")

    # Intentar rama main y luego master
    for branch in ["main", "master"]:
        tree_url = f"https://api.github.com/repos/{user}/{repo}/git/trees/{branch}?recursive=1"
        response = requests.get(tree_url)
        if response.status_code == 200:
            break
    else:
        return {"error": f"No se pudo acceder al repo {user}/{repo}. Puede ser privado o inexistente."}

    tree = response.json()

    # Filtrar solo archivos de código y configuración relevantes
    EXTENSIONES = (".jsx", ".tsx", ".js", ".ts", ".html", ".css", ".py", ".json", ".scss", ".sql", ".php")
    IGNORAR = ("node_modules", ".git", "dist", "build", "eslint", "package-lock.json", "yarn.lock", "public")

    archivos_relevantes = [
        f for f in tree["tree"]
        if f["type"] == "blob"
        and (f["path"].endswith(EXTENSIONES) or f["path"] in ["package.json", "requirements.txt", "README.md"])
        and not any(ignorado in f["path"] for ignorado in IGNORAR)
    ]

    # Priorizar archivos de configuración y puntos de entrada
    def prioridad(path):
        lower_path = path.lower()
        if "package.json" in lower_path or "requirements.txt" in lower_path: return 0
        if "app" in lower_path or "main" in lower_path or "index" in lower_path: return 1
        if "components" in lower_path or "src" in lower_path: return 2
        return 3

    archivos_relevantes.sort(key=lambda f: prioridad(f["path"]))

    # Fetchear contenido real (límite razonable para no saturar el contexto)
    MAX_ARCHIVOS = 30
    contenidos = {}
    for archivo in archivos_relevantes[:MAX_ARCHIVOS]:
        raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{archivo['path']}"
        r = requests.get(raw_url)
        if r.status_code == 200:
            contenidos[archivo['path']] = r.text

    if not contenidos:
        return {"error": "El repositorio no contiene archivos de código accesibles."}

    return {
        "repo": f"{user}/{repo}",
        "branch": branch,
        "archivos_encontrados": list(contenidos.keys()),
        "codigo": contenidos
    }

repo_tool = {
        "name": "get_repo_files",
        "description": (
            "Obtiene el código fuente real de un repositorio público de GitHub. "
            "Úsala SIEMPRE como primer paso antes de evaluar. "
            "Nunca evalúes un repositorio sin haber llamado esta herramienta primero."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "github_url": {
                    "type": "string",
                    "description": "URL completa del repositorio de GitHub. Ej: https://github.com/user/repo"
                },
                "instructions": {
                    "type": "string",
                    "description": "Consigna de la tarea que debía realizar el usuario"
                }
            },
            "required": ["github_url", "instructions"]
        }
    }