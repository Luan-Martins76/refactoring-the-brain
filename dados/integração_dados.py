import json
import os

def carregar_json(caminho):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, caminho), 'r', encoding='utf-8') as f:
        return json.load(f)

dados = {
    "institucional": carregar_json("institucional.json"),  
    "cursos":        carregar_json("cursos.json"),
    "professores":   carregar_json("professores.json"),
    "materias":      carregar_json("materias.json"),
    "secretaria":    carregar_json("secretaria.json"),
    "calendario":    carregar_json("calendario.json"),
}