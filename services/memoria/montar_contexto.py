from services.memoria.auxiliares.gerar_resumo import gerar_resumo_memoria

def montar_contexto(historico: list, n_total: int = 0) -> tuple[str, bool]:
    """
    Pipeline de memória comprimida:
    1. Tenta gerar um resumo via MODELO_MEMORIA (mistral-nemo).
    2. Se conseguir → retorna (resumo formatado, foi_gerado_agora).
    3. Se falhar → cai de volta para as últimas 5 mensagens brutas (comportamento legado).
    """
    if not historico:
        return "", False

    resumo, gerado_agora = gerar_resumo_memoria(historico, n_total=n_total)

    if resumo:
        return f"RESUMO DO CONTEXTO DA CONVERSA (gerado automaticamente):\n{resumo}\n", gerado_agora

    # Fallback: últimas 5 mensagens brutas
    janela_curta = historico[-5:]
    linhas = [
        f"{'Usuário' if m['remetente'] == 'user' else 'Sulivan'}: {m['conteudo']}"
        for m in janela_curta
    ]
    return "HISTÓRICO RECENTE DA CONVERSA:\n" + "\n".join(linhas) + "\n", False
