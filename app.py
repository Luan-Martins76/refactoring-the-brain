from flask import Flask, render_template, request, jsonify, session, redirect
from dotenv import load_dotenv
from services.ia_service import chat
from services.ollamastart.start import garantir_ollama_rodando
from login.logica_login import (
    validar_usuario,
    criar_conta,
    salvar_mensagem,
    carregar_historico,
    limpar_historico,
)

import os
import tempfile

load_dotenv()
garantir_ollama_rodando()

EXTENSOES_PERMITIDAS = {
    "png", "jpg", "jpeg", "gif", "webp",
    "pdf",
    "docx",
    "txt",
    # códigos. vou ser vibe coder agora... (feat que adiciona modelo especializado em codigo, vibe coder... Se quiser sim? "Sulivan faz um SPA megolomanioco com 20MB no zip, não cometa erros 💀", o prompt ai do front...)
    "py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "cs",
    "go", "rs", "php", "rb", "kt", "swift", "sh", "sql",
    "html", "css", "json", "yaml", "yml", "toml", "xml", "md",
}
 

def extensao_permitida(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
print(os.getenv("SECRET_KEY"))

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    user = validar_usuario(data["email"], data["password"])

    if user:
        session["user_id"] = user["id"]
        session["user_nome"] = user["nome"]
        return jsonify({"status": "ok", "nome": user["nome"]})

    return jsonify({"erro": "Email ou senha inválidos"}), 401

@app.route("/cookie")
def cookie():
    return render_template("cookie_chat.html")



@app.route("/cadastro", methods=["POST"])
def cadastro():
    data = request.get_json()

    if not data or not data.get("nome") or not data.get("email") or not data.get("password"):
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    sucesso, resultado = criar_conta(data["nome"], data["email"], data["password"])

    if sucesso:
        session["user_id"] = resultado["id"]
        session["user_nome"] = resultado["nome"]
        return jsonify({"status": "ok", "nome": resultado["nome"]})

    return jsonify({"erro": resultado}), 409


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return render_template("chat-test.html")

@app.route("/index")
def painel():
    if "user_id" not in session:
        return redirect("/")
    return render_template("chat-test.html")


@app.route("/health", methods=["GET"])
def healthcheck():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    mensagem = request.json.get("mensagem")
    usuario_id = session.get("user_id")

    # Incrementa contador ANTES do chat (conta a mensagem atual)
    if usuario_id:
        from services.memoria.auxiliares.disparar_resumo import _incrementar_contador
        n_total = _incrementar_contador()
    else:
        n_total = 0

    # Busca histórico e injeta mensagem atual
    historico = carregar_historico(usuario_id, limite=15) if usuario_id else []
    historico_com_atual = historico + [{"remetente": "user", "conteudo": mensagem}]

    resposta_dict = chat(mensagem, historico=historico_com_atual, n_total=n_total)
    resposta = resposta_dict["resposta"] if isinstance(resposta_dict, dict) else resposta_dict

    # Persiste a troca
    if usuario_id:
        salvar_mensagem(usuario_id, "user", mensagem)
        salvar_mensagem(usuario_id, "bot", resposta)

    return jsonify({
        "response": resposta,
        "source": resposta_dict.get("source"),
        "memoria_atualizada": resposta_dict.get("memoria_atualizada", False),
        "resumo_memoria": resposta_dict.get("resumo_memoria"),
        "analise_codigo": resposta_dict.get("analise_codigo"),

    })

@app.route("/chat/arquivo", methods=["POST"])
def chat_arquivo_endpoint():
    # multipart/form-data — mensagem vem do form, não do JSON
    mensagem = request.form.get("mensagem", "").strip()
    arquivo  = request.files.get("arquivo")
    
    print(f"[DEBUG] mensagem='{mensagem}' | arquivo={arquivo} | filename='{getattr(arquivo, 'filename', None)}'")
    if not mensagem and not arquivo:
        return jsonify({"error": "Envie uma mensagem ou um arquivo."}), 400
 
    if arquivo and arquivo.filename and not extensao_permitida(arquivo.filename):
        return jsonify({"error": "Tipo de arquivo não suportado."}), 415
 
    usuario_id = session.get("user_id")
 
    # Incrementa contador igual à rota /chat
    if usuario_id:
        from services.memoria.auxiliares.disparar_resumo import _incrementar_contador
        n_total = _incrementar_contador()
    else:
        n_total = 0
 
    # Histórico igual à rota /chat
    historico = carregar_historico(usuario_id, limite=15) if usuario_id else []
    historico_com_atual = historico + [{"remetente": "user", "conteudo": mensagem}]
 
    # Salva o arquivo em disco temporariamente
    caminho_arquivo = None
    if arquivo:
        sufixo = "." + arquivo.filename.rsplit(".", 1)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
            arquivo.save(tmp)
            caminho_arquivo = tmp.name
 
    try:
        resposta_dict = chat(
            mensagem,
            historico=historico_com_atual,
            n_total=n_total,
            arquivo=caminho_arquivo,
            arquivo_mime=arquivo.mimetype if arquivo else None,
        )
    finally:
        # Limpa o arquivo temporário independente de erro
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
 
    resposta = resposta_dict["resposta"] if isinstance(resposta_dict, dict) else resposta_dict
 
    # Persiste igual à rota /chat
    if usuario_id:
        salvar_mensagem(usuario_id, "user", mensagem)
        salvar_mensagem(usuario_id, "bot", resposta)
 
    return jsonify({
        "response": resposta,
        "source": resposta_dict.get("source"),
        "memoria_atualizada": resposta_dict.get("memoria_atualizada", False),
        "resumo_memoria": resposta_dict.get("resumo_memoria"),
        "analise_codigo": resposta_dict.get("analise_codigo"),
    })


# ─────────────────────────────────────────────
# ✅ NOVOS ENDPOINTS DE HISTÓRICO
# ─────────────────────────────────────────────

@app.route("/historico", methods=["GET"])
def historico():
    """Retorna o histórico de mensagens do usuário logado."""
    usuario_id = session.get("user_id")
    if not usuario_id:
        return jsonify({"erro": "Não autenticado"}), 401

    mensagens = carregar_historico(usuario_id)
    return jsonify({"mensagens": mensagens})


@app.route("/historico", methods=["DELETE"])
def deletar_historico():
    """Apaga todo o histórico do usuário logado."""
    usuario_id = session.get("user_id")
    if not usuario_id:
        return jsonify({"erro": "Não autenticado"}), 401

    limpar_historico(usuario_id)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug= True)
