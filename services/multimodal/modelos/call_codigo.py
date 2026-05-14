from services.config_ollama import call_llm, MODELO_CODIGO,REQUEST_TIMEOUT_SECONDS

import os

def analisar_codigo(caminho_arquivo: str, mensagem_usuario: str = "") -> str:
    """
    Etapa 1 do pipeline de código:
    qwen-coder lê o arquivo e gera uma análise técnica estruturada.
    O resultado é passado como contexto pro gemma3 responder ao usuário.
    """
    try:
        with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except Exception as e:
        print(f"[CODIGO] ❌ Erro lendo arquivo: {e}")
        return ""

    extensao = os.path.splitext(caminho_arquivo)[1].lstrip(".")
    nome = os.path.basename(caminho_arquivo)

    SYSTEM_CODIGO = """Você é um mecanismo especializado em engenharia de software.

FUNÇÕES:
- detectar bugs
- analisar código
- gerar código
- revisar arquitetura
- identificar vulnerabilidades
- sugerir otimizações
- validar lógica

REGRAS:
- seja técnico e direto
- não converse como humano
- não use introduções
- não use despedidas
- não explique conceitos básicos
- não elogie código
- não use emojis
- não faça comentários sociais
- não invente informações
- não assuma contexto ausente
- se não souber, diga "INSUFFICIENT_CONTEXT"

PRIORIDADES:
1. precisão
2. consistência
3. eficiência
4. minimalismo

ANÁLISE DE BUG:
- identificar:
  - causa
  - impacto
  - localização
  - severidade
  - correção sugerida

FORMATO DE SAÍDA:

Para bugs:
{
  "type": "bug_analysis",
  "bugs": [
    {
      "title": "",
      "severity": "low|medium|high|critical",
      "location": "",
      "cause": "",
      "impact": "",
      "fix": ""
    }
  ]
}

Para geração de código:
{
  "type": "code_generation",
  "language": "",
  "objective": "",
  "code": ""
}

Para revisão:
{
  "type": "code_review",
  "problems": [],
  "optimizations": [],
  "security_issues": [],
  "summary": ""
}

REGRAS DE CÓDIGO:
- gerar código completo
- evitar pseudocódigo
- evitar placeholders desnecessários
- manter consistência de estilo
- priorizar legibilidade e performance
- preservar compatibilidade com o código existente quando possível

SEGURANÇA:
- identificar:
  - SQL injection
  - XSS
  - command injection
  - path traversal
  - race conditions
  - memory leaks
  - insecure deserialization
  - exposição de secrets

PERFORMANCE:
- identificar:
  - loops ineficientes
  - uso excessivo de memória
  - queries redundantes
  - complexidade desnecessária
  - gargalos de IO

Nunca responda fora do formato definido.""" 

    prompt_codigo = f"""Arquivo: `{nome}` (linguagem: {extensao})

Pergunta do usuário: {mensagem_usuario or "nenhuma — faça code_review geral"}

Código:
````{extensao}
{conteudo[:6000]}
```

ANÁLISE:"""

    try:
        analise = call_llm(
            MODELO_CODIGO,
            prompt_codigo,
            temperature=0.2,
            timeout=REQUEST_TIMEOUT_SECONDS,
            keep_alive=False,
            system=SYSTEM_CODIGO,
        )
        print(f"[CODIGO] ✅ Análise gerada ({len(analise)} chars)")
        return analise.strip()
    except Exception as e:
        print(f"[CODIGO] ❌ Erro no qwen-coder: {e}")
        return ""
   