import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BANCO = os.path.join(os.path.dirname(__file__), "..", "dados", "usuarios.db")


def _conectar():
    """Abre conexão com o banco e garante que as tabelas existem."""
    os.makedirs(os.path.dirname(BANCO), exist_ok=True)
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER  PRIMARY KEY AUTOINCREMENT,
            nome      TEXT     NOT NULL,
            email     TEXT     NOT NULL UNIQUE,
            senha     TEXT     NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ✅ NOVA TABELA: histórico de mensagens por usuário
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mensagens (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER  NOT NULL,
            remetente   TEXT     NOT NULL CHECK(remetente IN ('user', 'bot')),
            conteudo    TEXT     NOT NULL,
            criado_em   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    return conn


def validar_usuario(email, password):
    """
    Verifica se o email existe e se a senha está correta.
    Retorna o usuário (dict) se válido, ou None se inválido.
    """
    conn = _conectar()
    try:
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email.lower(),)
        ).fetchone()

        if usuario and check_password_hash(usuario["senha"], password):
            return dict(usuario)

        return None
    finally:
        conn.close()


def criar_conta(nome, email, password):
    """
    Cria um novo usuário no banco.
    Retorna (True, usuario) se criado com sucesso.
    Retorna (False, mensagem_de_erro) se o email já existe.
    """
    conn = _conectar()
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
            (nome, email.lower(), generate_password_hash(password))
        )
        conn.commit()

        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email.lower(),)
        ).fetchone()

        return True, dict(usuario)

    except sqlite3.IntegrityError:
        return False, "Email já cadastrado"

    finally:
        conn.close()


# ─────────────────────────────────────────────
# ✅ NOVAS FUNÇÕES DE HISTÓRICO
# ─────────────────────────────────────────────

def salvar_mensagem(usuario_id: int, remetente: str, conteudo: str):
    """
    Persiste uma mensagem (do usuário ou do bot) no banco.
    remetente deve ser 'user' ou 'bot'.
    """
    conn = _conectar()
    try:
        conn.execute(
            "INSERT INTO mensagens (usuario_id, remetente, conteudo) VALUES (?, ?, ?)",
            (usuario_id, remetente, conteudo)
        )
        conn.commit()
    finally:
        conn.close()


def carregar_historico(usuario_id: int, limite: int = 100):
    """
    Retorna as últimas `limite` mensagens do usuário em ordem cronológica.
    Cada item é um dict com: id, remetente, conteudo, criado_em.
    """
    conn = _conectar()
    try:
        rows = conn.execute(
            """
            SELECT id, remetente, conteudo, criado_em FROM (
                SELECT id, remetente, conteudo, criado_em
                FROM mensagens
                WHERE usuario_id = ?
                ORDER BY criado_em DESC
                LIMIT ?
            ) ORDER BY criado_em ASC
            """,
            (usuario_id, limite)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def limpar_historico(usuario_id: int):
    """Apaga todo o histórico de um usuário (opcional, mas útil pro frontend)."""
    conn = _conectar()
    try:
        conn.execute("DELETE FROM mensagens WHERE usuario_id = ?", (usuario_id,))
        conn.commit()
    finally:
        conn.close()
