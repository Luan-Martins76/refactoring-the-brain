# 🧠 Refactoring the Brain — Sulivan

> Assistente virtual da UniEVANGÉLICA, movido por uma pipeline multi-modelo local via Ollama.

Este repositório é o backend e front teste do **Sulivan** — um chatbot acadêmico construído com Flask, projetado para responder dúvidas institucionais, interpretar arquivos e conversar com contexto de memória persistente entre sessões.

> ⚠️ **Estado atual:** versão funcional inicial. Refatoração de segurança e arquitetura em andamento.

---

## ✨ Funcionalidades

- 💬 **Chat com memória** — resumo automático do histórico via `mistral-nemo:12b`, resposta via `gemma3:4b`
- 🖼️ **Multimodal** — interpreta imagens (OCR + visão via `llava-llama3`), PDFs e documentos `.docx`
- 🧑‍💻 **Análise de código** — pipeline especializado com `qwen2.5-coder:7b` para arquivos de código
- 📋 **Engine de regras** — respostas diretas e precisas para agenda, cursos, disciplinas e calendário acadêmico
- 🔐 **Autenticação** — cadastro e login com senhas hasheadas via Werkzeug + sessões Flask
- 📁 **Upload de arquivos** — suporte a imagens, PDFs, `.docx`, `.txt` e dezenas de extensões de código
- 🗃️ **Histórico persistente** — mensagens armazenadas por usuário em SQLite

---

## 🏗️ Arquitetura

```
refactoring_the_brain/
│
├── app.py                  # Rotas Flask (chat, auth, histórico, uploads)
│
├── services/
│   ├── ia_service.py       # Pipeline LLM: memória, resposta, visão e código
│   └── baseado_regras.py   # Engine de regras: agenda semanal, aliases, fallbacks
│
├── login/
│   └── logica_login.py     # Autenticação, cadastro e histórico (SQLite)
│
├── dados/
│   ├── cursos.json         # Dados de cursos por campus
│   ├── materias.json       # Disciplinas por curso
│   ├── calendario.json     # Calendário acadêmico por campus
│   ├── institucional.json  # Dados institucionais
│   └── integração_dados.py # Loader central dos JSONs
│
└── templates/
    └── chat-test.html      # Interface do chat (SPA)
```

---

## 🤖 Pipeline de IA

O Sulivan usa uma pipeline multi-modelo local via [Ollama](https://ollama.com):

| Modelo | Papel |
|---|---|
| `gemma3:4b` | Modelo principal — gera as respostas ao usuário |
| `mistral-nemo:12b` | Modelo de memória — resume o histórico da conversa |
| `llava-llama3` | Modelo de visão — interpreta imagens enviadas |
| `qwen2.5-coder:7b` | Especialista em código — analisa arquivos de código antes do modelo principal |

**Fluxo padrão:**
1. A mensagem passa pela engine de regras. Se houver match (agenda, curso, calendário), responde direto sem LLM.
2. Se for arquivo de código → `qwen2.5-coder:7b` analisa → resultado é injetado no prompt do `gemma3:4b`.
3. O histórico recente é resumido pelo `mistral-nemo:12b` para compor o contexto de memória.
4. O `gemma3:4b` gera a resposta final com o contexto montado.

---

## ⚙️ Requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado e rodando localmente
- Modelos Ollama baixados:

```bash
ollama pull gemma3:4b
ollama pull mistral-nemo:12b
ollama pull llava-llama3
ollama pull qwen2.5-coder:7b
```

### Dependências Python

```bash
pip install flask python-dotenv werkzeug requests markdown pdfplumber python-docx easyocr
```

---

## 🚀 Como rodar

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/refactoring-the-brain.git
cd refactoring-the-brain
```

**2. Configure o `.env`**

Crie um arquivo `.env` na raiz com:

```env
SECRET_KEY=sua_chave_secreta_aqui
```

> Nunca commite o `.env` real. Use `.env.example` como referência.

**3. Suba o Ollama**

```bash
ollama serve
```

**4. Rode o Flask**

```bash
python app.py
```

Acesse em `http://localhost:5000`.

---

## 📡 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/login` | Autenticar usuário |
| `POST` | `/cadastro` | Criar conta |
| `POST` | `/logout` | Encerrar sessão |
| `POST` | `/chat` | Enviar mensagem (JSON) |
| `POST` | `/chat/arquivo` | Enviar mensagem + arquivo (multipart) |
| `GET` | `/historico` | Buscar histórico do usuário logado |
| `DELETE` | `/historico` | Apagar histórico do usuário logado |
| `GET` | `/health` | Healthcheck |

---

## 🔒 Segurança — Status Atual

> Esta versão é funcional mas ainda **não está hardened para produção**. As seguintes melhorias estão planejadas para a próxima fase de refatoração:

- [ ] Remover `debug=True` do `app.run()` em produção
- [ ] Migrar `SECRET_KEY` para variável de ambiente com validação na inicialização
- [ ] Adicionar rate limiting nos endpoints de chat e auth
- [ ] Sanitizar e validar entradas dos formulários no backend
- [ ] Revisar expiração e segurança das sessões Flask
- [ ] Adicionar `.env.example` e garantir que `.env` está no `.gitignore`
- [ ] Avaliar migração do SQLite para banco mais robusto em produção

---

## 🗺️ Roadmap

- [x] Pipeline multi-modelo (memória + resposta)
- [x] Engine de regras para dados institucionais
- [x] Upload e interpretação de arquivos (imagens, PDF, DOCX, código)
- [x] Autenticação com hash de senha
- [x] Histórico persistente por usuário
- [ ] Refatoração de segurança
- [ ] Testes automatizados
- [ ] Dockerização
- [ ] Deploy em produção

---

## 👨‍💻 Autor

**Luan Martins** — IA na UniEVANGÉLICA  
[GitHub](https://github.com/Luan-Martins76) · [LinkedIn](https://linkedin.com/in/luan-martins5533) · [Site](https://unuskawnai.com)

---

## 📄 Licença

MIT License — pode usar, estudar, modificar e distribuir.  
Só pede uma coisa: **dá um salve ao autor** se usar em alguma coisa. Um crédito no README, um email, um seguir no GitHub, qualquer coisa. Não custa nada e significa muito.

📧 Contato: [LinkedIn](https://linkedin.com/in/luan-martins5533)

---

## 📝 Sobre esta documentação

> Esta documentação foi escrita pelo **Claude** (Anthropic) a pedido do Luan, que preferiu ser transparente sobre o uso de IA em vez de fingir que escreveu às 2 da manhã.  
> O Luan tirou 560 na redação do ENEM, algem acha que ele consegue escrever um texto? Claude não vai comentar sobre isso. 
(-Luan: IA é fogo, fica jogando na cara...)
> O código, a arquitetura e as ideias malucas de colocar quatro modelos de LLM numa máquina só? Esses são dele. 🫡
# refactoring-the-brain
