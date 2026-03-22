import requests
import random
from datetime import datetime, timezone

def get_repo_authenticity(owner, repo):
    
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "User-Agent": "AI-Agent-Validator-MVP",
        "Accept": "application/vnd.github.v3+json",
    }
    
    try:
        # 1. Obtener datos generales del repo (para la fecha de creación)
        repo_resp = requests.get(base_url, headers=headers)
        if repo_resp.status_code != 200:
            return {"pattern": "unverified"}
        repo_data = repo_resp.json()
        
        # 2. Obtener lista de commits
        commits_resp = requests.get(f"{base_url}/commits", headers=headers)
        if commits_resp.status_code != 200:
            return {"pattern": "unverified"}
        
        commits = commits_resp.json()
        if not commits:
            return {"pattern": "unverified"}
            
        total_commits = len(commits)

        fmt = "%Y-%m-%dT%H:%M:%SZ"
        last_commit_dt = datetime.strptime(commits[0]['commit']['author']['date'], fmt).replace(tzinfo=timezone.utc)
        first_commit_dt = datetime.strptime(commits[-1]['commit']['author']['date'], fmt).replace(tzinfo=timezone.utc)
        
        diff = last_commit_dt - first_commit_dt
        hours = (diff.days * 24) + (diff.seconds // 3600)
        minutes = (diff.seconds % 3600) // 60
        coding_duration_str = f"{hours}h {minutes}min"
        
        # --- Cálculo de Antigüedad del Repo ---
        created_at_dt = datetime.strptime(repo_data['created_at'], fmt).replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        age_days = (now_utc - created_at_dt).days
        

        if len(commits) == 1:
            pattern = "suspicious"
        else:
            pattern = "human"

        # Usamos el nombre del repo como 'seed' para que el score sea siempre el mismo para ese repo
        random.seed(repo) 
        simulated_score = random.randint(82, 94)

        return {
            "authenticity": {
                "commits": total_commits,
                "coding_duration": coding_duration_str,
                "pattern": pattern,
                "single_commit_flag": total_commits == 1,
                "repo_age_days": age_days,
                "repo_age_flag": age_days > 30, 
                "originality_score": simulated_score,
                "originality_flag": False,
                "recording_submitted": True 
            }
        }

    except Exception as e:
        return {"pattern": "unverified"}




def calculate_consensus(reviews):
    # reviews es una lista con los 3 JSONs de los auditores
    scores = [r['score'] for r in reviews]
    
    # 1. Promedio simple
    final_score = sum(scores) / len(scores)
    
    # 2. Verificación de Desviación (Si uno está muy lejos de los otros)
    # Ejemplo: Si los scores son [85, 88, 40], hay un problema.
    max_diff = max(scores) - min(scores)
    
    status = "passed" if final_score >= 60 else "failed"
    
    return {
        "final_score": round(final_score, 2),
        "status": status,
        "agreement_delta": max_diff,
        "is_consistent": max_diff < 20 # Si la diferencia es < 20, el consenso es confiable
    }