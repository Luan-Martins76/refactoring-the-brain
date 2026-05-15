from services.config_ollama import (
    call_llm,
    HISTORICO_MEMORIA_MAX,
    RESUMO_MINIMO_MSGS,
    RESUMO_INTERVALO_MSGS,
    MEMORY_TIMEOUT_SECONDS,
    MODELO_MEMORIA
)
from services.memoria.auxiliares.disparar_resumo import (
    _get_cache_resumo,
    _serializar_historico,
    _set_cache_resumo
    

)


def gerar_resumo_memoria(historico: list, n_total: int = 0) -> tuple[str | None, bool]:
    """
    Envia as últimas HISTORICO_MEMORIA_MAX mensagens para o MODELO_MEMORIA
    e retorna (resumo, foi_gerado_agora).

    Usa n_total (contador absoluto da sessão) para decidir quando regenerar.
    O cache é isolado por sessão Flask — sem vazamento entre usuários.

    Retorna (None, False) se o histórico for pequeno demais ou se o modelo falhar.
    """
    janela = historico[-HISTORICO_MEMORIA_MAX:]

    if len(janela) < RESUMO_MINIMO_MSGS:
        return None, False

    cache_atual, cache_gerado_em = _get_cache_resumo()

    # ← sessão nova: n_total menor que cache_em significa que reiniciou
    if n_total < cache_gerado_em:
        cache_atual = None
        cache_gerado_em = 0
        _set_cache_resumo("", 0)  # limpa o cache velho

    msgs_desde_ultimo_resumo = n_total - cache_gerado_em

    cache_atual, cache_gerado_em = _get_cache_resumo()
    msgs_desde_ultimo_resumo = n_total - cache_gerado_em

    print(f"[MEMORIA] n_total={n_total} | cache_em={cache_gerado_em} | desde_ultimo={msgs_desde_ultimo_resumo} | cache_existe={cache_atual is not None}")

    #  Ainda dentro do intervalo — devolve o cache sem chamar o modelo
    if cache_atual and msgs_desde_ultimo_resumo < RESUMO_INTERVALO_MSGS:
        print("[MEMORIA] → usando cache, não regenera")
        return cache_atual, False  

    
    historico_texto = _serializar_historico(janela)

    prompt_memoria = f"""Você é um sistema especializado em compressão de contexto conversacional.

Sua tarefa é analisar as últimas mensagens de um usuário e gerar um resumo estruturado, objetivo e útil para outro modelo de linguagem usar como memória.

REGRAS IMPORTANTES:
- NÃO invente informações.
- NÃO complete lacunas com suposições.
- Use APENAS o que está explicitamente nas mensagens.
- Seja conciso, mas preserve informações importantes.
- Priorize intenção, contexto e continuidade.
- Ignore conversas irrelevantes, ruído ou repetições.
- NÃO inclua opinião, julgamento ou explicações desnecessárias.

ENTRADA:
Você receberá até 15 mensagens recentes do usuário.

SAÍDA (FORMATO OBRIGATÓRIO):

Resumo Geral:
- (Resumo curto do que o usuário está fazendo, perguntando ou tentando resolver)

Objetivos do Usuário:
- (Lista clara do que o usuário quer alcançar)

Contexto Relevante:
- (Informações importantes que impactam respostas futuras)

Preferências/Estilo:
- (Como o usuário se comunica ou prefere respostas, se identificável)

Pendências:
- (O que ainda não foi resolvido ou pode ser continuidade)

Sinais de Atenção:
- (Possíveis ambiguidades, mudanças de direção ou dúvidas)

RESTRIÇÕES:
- Máximo de 150-200 palavras.
- Use bullet points.
- Linguagem clara e direta.
- Não repita mensagens literalmente, resuma.

IMPORTANTE:
Esse resumo será usado por outro modelo para continuar a conversa com precisão. Qualquer erro ou invenção prejudica o sistema.

HISTÓRICO:
{historico_texto}

RESUMO DO CONTEXTO:"""

    try:
        resumo = call_llm(MODELO_MEMORIA, prompt_memoria, temperature=0.3, timeout=MEMORY_TIMEOUT_SECONDS, keep_alive=False)
        resumo = resumo.strip()
        if resumo:
            _set_cache_resumo(resumo, n_total)  
            return resumo, True  
        return None, False
    except Exception as e:
        print(f"[MEMORIA] ❌ ERRO no modelo: {e}")
        return cache_atual or None, False
