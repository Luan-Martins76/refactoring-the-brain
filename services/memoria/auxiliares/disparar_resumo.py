from flask import session, has_request_context


_kivy_cache_resumo: str | None = None
_kivy_cache_resumo_em_n_msgs: int = 0

def _get_cache_resumo() -> tuple[str | None, int]:
    """Lê o cache do resumo do contexto correto (sessão Flask ou fallback Kivy)."""
    if has_request_context():
        return session.get("resumo_cache"), session.get("resumo_cache_n", 0)
    return _kivy_cache_resumo, _kivy_cache_resumo_em_n_msgs


def _set_cache_resumo(resumo: str, n_msgs: int) -> None:
    """Salva o cache do resumo no contexto correto (sessão Flask ou fallback Kivy)."""
    global _kivy_cache_resumo, _kivy_cache_resumo_em_n_msgs
    if has_request_context():
        session["resumo_cache"] = resumo
        session["resumo_cache_n"] = n_msgs
    else:
        _kivy_cache_resumo = resumo
        _kivy_cache_resumo_em_n_msgs = n_msgs



def _contar_msgs_usuario(historico: list) -> int:
    return sum(1 for msg in historico if msg["remetente"] == "user")


def _serializar_historico(historico: list) -> str:
    """Converte lista de mensagens em texto corrido para o modelo de memória."""
    linhas = []
    for msg in historico:
        prefixo = "Usuário" if msg["remetente"] == "user" else "Sulivan"
        linhas.append(f"{prefixo}: {msg['conteudo']}")
    return "\n".join(linhas)

def _get_contador_total() -> int:
    if has_request_context():
        return session.get("total_msgs_usuario", 0)
    return 0

def _incrementar_contador() -> int:
    if has_request_context():
        n = session.get("total_msgs_usuario", 0) + 1
        session["total_msgs_usuario"] = n
        return n
    return 0