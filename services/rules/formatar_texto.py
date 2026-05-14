from services.rules.dicionarios import AGENDA_ALIASES
import unicodedata


def normalize_text(text):  
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def resolve_day(mensagem): 
    normalized = normalize_text(mensagem)
    for possible_day, canonical_day in AGENDA_ALIASES.items():
        if possible_day in normalized:
            return canonical_day
    return None


def formatar_cursos(dados, campus_nome): 
    chave = f"campus_{campus_nome.lower()}"
    cursos_json = dados.get("cursos", {})
    campus_dados = cursos_json.get(chave)

    if not campus_dados:
        return f"❌ Campus '{campus_nome}' não encontrado."

    cursos = campus_dados.get("curso", [])
    total = campus_dados.get("quantidade_cursos", len(cursos))

    texto = f"📍 Cursos em {campus_nome.capitalize()}:\n\n"
    for curso in cursos:
        texto += f"• {curso.title()}\n"
    texto += f"\n📊 Total: {total} cursos"
    return texto


def formatar_materia(dados, curso): 
    chave = normalize_text(curso).upper()
    materias_json = dados.get("materias", {})
    curso_dados = materias_json.get(chave)

    if not curso_dados:
        return f"❌ Curso '{curso}' não encontrado."

    online = curso_dados.get("disciplina_online", [])
    presenciais = curso_dados.get("disciplina_presenciais", [])

    texto = f"📚 Disciplinas de {chave.title()}:\n\n"
    if online:
        texto += "🖥️ Online:\n"
        for d in online:
            texto += f"• {d.split(' - ')[0]}\n"
    if presenciais:
        texto += "\n🏫 Presenciais:\n"
        for d in presenciais:
            texto += f"• {d.split(' - ')[0]}\n"
    return texto


def formatar_calendario(dados, campus, mes=None): 
    chave_campus = normalize_text(campus).replace(" ", "_")
    calendario_json = dados.get("calendario", {})
    campus_dados = calendario_json.get(chave_campus)

    if not campus_dados:
        return f"❌ Campus '{campus}' não encontrado."

    if mes:
        chave_mes = normalize_text(mes)
        mes_dados = campus_dados.get(chave_mes)
        if not mes_dados:
            return f"❌ Mês '{mes}' não encontrado para o campus {campus}."
        return _formatar_mes(chave_mes, mes_dados)

    texto = f"📅 Calendário — {chave_campus.replace('_', ' ').title()}:\n\n"
    for nome_mes, mes_dados in campus_dados.items():
        texto += _formatar_mes(nome_mes, mes_dados) + "\n"
    return texto


def _formatar_mes(nome_mes, mes_dados): 
    texto = f"🗓️ {nome_mes.title()}:\n"

    eventos = mes_dados.get("eventos", {})
    if eventos:
        texto += "  📌 Eventos:\n"
        for data, descricao in eventos.items():
            texto += f"    • {data}: {descricao}\n"

    dias_letivos = mes_dados.get("dias_letivos")
    feriados = mes_dados.get("feriados")

    if dias_letivos is not None:
        texto += f"  📖 Dias letivos: {dias_letivos}\n"
    if feriados is not None:
        texto += f"  🔴 Feriados: {feriados}\n"

    return texto