# esse dicionario é usado para responder os as aulas do meu curso
agenda = {
    "segunda": {
        "materia": "FUNDAMENTOS DE ENGENHARIA DE DADOS",
        "professor": "EDUARDO",
        "inicio": "19:00",
        "termino": "21:50",
        "local": "BLOCO H, SALA 110",
    },
    "terça": {
        "materia": "FUNDAMENTOS MATEMÁTICOS PARA COMPUTAÇÃO",
        "professor": "Otoniel",
        "inicio": "19:00",
        "termino": "21:50",
        "local": "BLOCO H, SALA 110",
    },
    "quarta": {
        "materia": "INTRODUÇÃO À ENGENHARIA DE SOLUÇÕES",
        "professor": "HENRIQUE LIMA",
        "inicio": "19:00",
        "termino": "22:40",
        "local": "BLOCO H, SALA 110",
    },
    "quinta": {
        "materia": "CIDADANIA, ÉTICA E ESPIRITUALIDADE",
        "professor": "HELEHON SANTOS",
        "inicio": "19:00",
        "termino": "21:40",
        "local": "BLOCO H, SALA 110",
    },
    "sexta": {
        "materia": "FUNDAMENTO DE COMPUTAÇÃO E INFRAESTRUTURA",
        "professor": "ARAÚJO",
        "inicio": "19:00",
        "termino": "21:40",
        "local": "BLOCO H, SALA 110",
    },
    "sabado": {
        "materia": "LEITURA E INTERPRETAÇÃO DE TEXTO - ONLINE",
        "professor": "[NÃO TEM, AUTODIDATA MAN]",
        "inicio": "[QUANDO QUISER (SÓ NÃO INVENTA DE NÃO FAZER)]",
        "termino": "[NO SEU TEMPO IRMÃO]",
        "local": "[SUA CASA]",
    },
}

AGENDA_ALIASES = {
    "segunda": "segunda",
    "terca": "terça",
    "terça": "terça",
    "quarta": "quarta",
    "quinta": "quinta",
    "sexta": "sexta",
    "sabado": "sabado",
    "sábado": "sabado",
}

"""
Fallback: 
São essas frases que aparece quando a pergunta do usuario não é respondida
pelas regras e o modelo não é carregado corretamente.
  Ponto de atenção, quando essas frases aparece tem três motivos mais comuns:

  - Tempo para o modelo responder atingiu o limite.
    * A LLM pode até ter subido, porem tem um alto custo de processamento diminuido a geração de tokens e ecedendo o tempo. 
    ! Diminuir os parametros do modelo da LLM ou aumentar o tempo limite para gerar respostas

 - O modelo de LLM não ter subido propiadamente dito.
   * Seu computador não ter VRAM o suficiente no momento, ou nem a capacidade de rodar um dos modelos. 
    fique ligado no "mistral-nemo:12b", ele é o mais pesado do sistema, se ele rodar satisfatoriamente os demais modelos tambem vão por ser mais leves.
    !Diminuir os parametros dos modelos é o unico jeito de resolver

 - Sem ter instalados os modelos, sem as LLM e o ollama não tem resposta...
  !virificar se todas as dependencias foram instaladas corretamenta

"""

fallback = [
    "Calma lá paizão, aqui só tem um if só. Seloko...",
    "Seloko, sou rede neural não man",
    "Luan quando me configurou não pensou nesta possibilidade",
    "Você poderia escrever um dia da semana para eu mostrar a minha utilidade né?",
    "*pensando para dar uma resposta* Atahhh eu não penso, não sou rede neural...",
    "Meu sonho era ser o GPT, mas desisti quando vi isso ai. Seloko, não compensa.",
    "Interessante... Vou fingir que processei isso.",
    "Isso parece importante, mas não o suficiente para eu virar uma IA e te responder",
    "Entendi. Não concordo, mas entendi.",
    "Se eu tivesse sentimentos, estaria julgando agora.",
    "Ótimo ponto. Próximo.",
    "Você digitou isso com convicção né? Eu respeito isso.",
    "Isso diz mais sobre você do que sobre mim",
    "Anotado mentalmente (mentira)",
    "Vou responder isso na próxima atualização... Talvez.",
    "Essa pergunta foi corajosa.",
    "Processando... *erro 404: paciência não encontrada*.",
    "Se isso fosse um teste, você passou. Em que? Eu não sei.",
    "Não fui treinado para lidar com isso. Na verdade, não fui treinado para nada - sou um agente baseado em regras.",
    "Essa foi uma escolha de palavras.",
    "Martins tá no primeiro período... Se acha que isso aqui responde essa interação ai? kkkkkkk",
]
