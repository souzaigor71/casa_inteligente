import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Habilita o logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

conversas = {
    "oi": "Olá! Como posso ajudar você hoje?",
    "como você está": "Estou bem, obrigado por perguntar!",
    "qual é o seu nome": "Eu sou um bot criado para ajudar você.",
    "ajuda": "Aqui estão os tópicos sobre os quais você pode falar comigo:\n- Oi\n- Como você está\n- Qual é o seu nome\n- Ajuda",
    "tempo": "Desculpe, ainda não posso fornecer informações sobre o tempo.",
    "notícias": "Desculpe, ainda não posso fornecer notícias.",
    "adeus": "Adeus! Tenha um ótimo dia!",
    "quem é você": "Eu sou um bot criado para responder perguntas básicas.",
    "dúvidas": "Diga suas dúvidas e farei o meu melhor para ajudar.",
    "bom dia": "Bom dia! Como posso ajudar você hoje?",
    "boa tarde": "Boa tarde! Em que posso ajudar?",
    "boa noite": "Boa noite! Como posso ser útil?",
    "como está o clima": "Desculpe, não posso verificar o clima.",
    "quais são seus hobbies": "Eu sou apenas um bot, não tenho hobbies, mas estou aqui para ajudar!",
    "me conte uma piada": "Por que o programador sempre confunde o Halloween com o Natal? Porque Oct 31 é igual a Dec 25!",
    "qual é a sua cor favorita": "Como um bot, eu não tenho uma cor favorita, mas posso ajudar você com muitas coisas!",
    "você pode me dar uma receita": "Claro, posso fornecer algumas receitas básicas. Que tipo de receita você gostaria?",
    "quero saber sobre programação": "Programação é o processo de escrever código para criar software. Quais são suas dúvidas específicas?",
    "fale sobre ciência": "A ciência é o estudo sistemático do mundo natural e dos fenômenos que ocorrem nele. Há algo específico que você quer saber?",
    "o que é tecnologia": "Tecnologia é a aplicação de conhecimentos científicos para criar ferramentas e soluções para problemas humanos.",
    "me conte uma curiosidade": "Você sabia que a abelha pode bater as asas até 200 vezes por segundo?",
    "quais são seus planos": "Eu não tenho planos próprios, mas estou aqui para ajudar você com suas perguntas!",
    "quem criou você": "Eu fui criado por desenvolvedores que programaram minhas funcionalidades.",
    "qual é o sentido da vida": "O sentido da vida é um tema filosófico. Muitas pessoas encontram sentido em diferentes aspectos da vida, como relacionamentos, trabalho e paixão.",
    "você pode me recomendar um filme": "Claro! Que tipo de filme você gosta? Ação, comédia, drama?",
    "qual é a sua música favorita": "Eu não tenho uma música favorita, mas posso sugerir alguns gêneros ou artistas com base em suas preferências!",
    "você conhece algum livro bom": "Sim! Que tipo de livro você gosta? Ficção, não-ficção, fantasia?",
    "me fale sobre esportes": "Esportes são atividades físicas competitivas ou recreativas. Qual esporte você gostaria de saber mais?",
    "quais são os principais países do mundo": "Os principais países podem variar dependendo do critério. Se você está falando sobre economia, países como EUA, China e Alemanha são bastante influentes.",
    "qual é a capital do Brasil": "A capital do Brasil é Brasília.",
    "qual é a moeda do Japão": "A moeda do Japão é o iene.",
    "quais são os oceanos do mundo": "Os oceanos principais do mundo são o Pacífico, Atlântico, Índico, Ártico e Antártico.",
    "qual é a maior cidade do mundo": "A maior cidade do mundo por população é Tóquio, no Japão.",
    "o que é uma blockchain": "Blockchain é uma tecnologia de registro distribuído que é segura e transparente, geralmente usada em criptomoedas.",
    "você pode me ajudar com matemática": "Sim, posso ajudar com problemas matemáticos. Qual é a sua dúvida?",
    "qual é o maior planeta do sistema solar": "O maior planeta do sistema solar é Júpiter.",
    "qual é a menor cidade do mundo": "A menor cidade do mundo em termos de população é Hum, na Croácia.",
    "o que é inteligência artificial": "Inteligência artificial é a simulação de processos inteligentes por máquinas, especialmente computadores.",
    "você conhece algum aplicativo útil": "Sim, há muitos aplicativos úteis dependendo do que você precisa. Exemplos incluem aplicativos de produtividade, saúde e educação.",
    "qual é o maior animal do mundo": "O maior animal do mundo é a baleia-azul.",
    "você pode me dar uma dica de estudo": "Claro! Organize seu tempo e faça pausas regulares para melhorar sua retenção de informações.",
    "o que é uma API": "Uma API (Interface de Programação de Aplicações) é um conjunto de definições e protocolos para criar e integrar software.",
    "você conhece alguma técnica de meditação": "Sim, uma técnica comum é a meditação mindfulness, onde você foca na respiração e no momento presente.",
    "como posso aprender uma nova língua": "Você pode aprender uma nova língua usando aplicativos, livros, aulas e prática com falantes nativos.",
    "qual é o prato típico do México": "Um prato típico do México é o taco.",
    "qual é a maior floresta do mundo": "A maior floresta do mundo é a Floresta Amazônica.",
    "qual é o esporte mais popular do mundo": "O esporte mais popular do mundo é o futebol.",
    "você pode me dar dicas de viagem": "Claro! Planeje com antecedência, pesquise sobre o destino e faça uma lista de itens importantes para levar.",
    "qual é o livro mais vendido de todos os tempos": "O livro mais vendido de todos os tempos é a Bíblia.",
    "qual é a diferença entre vírus e bactéria": "Vírus são parasitas que precisam de uma célula hospedeira para se reproduzir, enquanto bactérias são organismos unicelulares que podem viver em diversos ambientes.",
    "o que é um buraco negro": "Um buraco negro é uma região do espaço-tempo com uma gravidade tão forte que nada, nem mesmo a luz, pode escapar.",
    "qual é a maior invenção da história": "A maior invenção da história pode variar dependendo de quem você pergunta, mas alguns exemplos incluem a roda, a eletricidade e a internet.",
    "quem foi Albert Einstein": "Albert Einstein foi um físico teórico conhecido pela teoria da relatividade.",
    "o que é o efeito estufa": "O efeito estufa é o processo pelo qual certos gases na atmosfera da Terra retêm calor, contribuindo para o aquecimento global.",
    "você pode me recomendar um livro sobre ciência": "Claro! 'Sapiens: Uma Breve História da Humanidade' de Yuval Noah Harari é uma boa recomendação.",
    "como funciona um motor a combustão": "Um motor a combustão queima combustível para gerar energia mecânica através de processos de combustão interna.",
    "qual é o maior deserto do mundo": "O maior deserto do mundo é o Deserto da Antártica.",
    "o que é criptografia": "Criptografia é a prática de proteger informações através de técnicas de codificação para garantir que apenas pessoas autorizadas possam acessá-las.",
    "você pode me falar sobre astronomia": "Astronomia é o estudo dos corpos celestes e do universo como um todo. Inclui o estudo de estrelas, planetas, galáxias e mais.",
    "o que são direitos humanos": "Direitos humanos são direitos fundamentais que pertencem a todas as pessoas, independentemente de sua nacionalidade, gênero ou raça.",
    "qual é a origem da vida": "A origem da vida é uma questão complexa que envolve processos químicos e biológicos. Existem várias teorias sobre como a vida surgiu na Terra.",
    "como funciona a energia solar": "A energia solar é gerada convertendo a luz do sol em eletricidade através de painéis solares.",
    "quem foi Nelson Mandela": "Nelson Mandela foi um ativista anti-apartheid e ex-presidente da África do Sul, conhecido por sua luta pela igualdade racial.",
    "o que é uma rede neural": "Uma rede neural é um modelo computacional inspirado no funcionamento do cérebro humano, usado em inteligência artificial e aprendizado de máquina.",
    "você pode me ajudar com programação": "Sim, posso ajudar com problemas de programação. Qual é a sua dúvida específica?",
    "qual é a diferença entre um laptop e um desktop": "Laptops são computadores portáteis que podem ser usados em qualquer lugar, enquanto desktops são geralmente mais potentes e projetados para uso fixo em uma mesa.",
    "o que é o Big Bang": "O Big Bang é a teoria que descreve a origem do universo a partir de um estado de alta densidade e temperatura.",
    "qual é o país mais populoso do mundo": "O país mais populoso do mundo é a China.",
    "o que é um satélite natural": "Um satélite natural é um corpo celeste que orbita um planeta, como a Lua orbita a Terra.",
}

async def start(update: Update, context: CallbackContext) -> None:
    """Responde ao comando '/start'."""
    texto_boas_vindas = "Olá! Seja bem-vindo ao meu chatbot.\n\n"
    texto_comandos = "Comandos disponíveis:\n"
    for comando in conversas.keys():
        texto_comandos += f"- {comando}\n"

    texto_completo = texto_boas_vindas + texto_comandos
    await update.message.reply_text(texto_completo)

async def ajuda(update: Update, context: CallbackContext) -> None:
    """Responde ao comando '/ajuda'."""
    texto_ajuda = "Você pode falar comigo sobre os seguintes tópicos:\n"
    for topico in conversas.keys():
        texto_ajuda += f"- {topico}\n"
    await update.message.reply_text(texto_ajuda)

async def lidar_com_mensagem(update: Update, context: CallbackContext) -> None:
    """Responde a mensagens que não são comandos."""
    mensagem_usuario = update.message.text.lower()

    # Verifica se a mensagem do usuário está nos tópicos de conversa
    resposta = conversas.get(mensagem_usuario, "Desculpe, não sei como responder a isso. Tente perguntar sobre outra coisa.")

    await update.message.reply_text(resposta)

def main() -> None:
    """Inicia o bot."""

    application = Application.builder().token("7077790133:AAFCnFIYS7m8wU3K12DZ6KKq5ab5eg_vDmk").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lidar_com_mensagem))

    # Inicia o bot
    application.run_polling()

if __name__ == '__main__':
    main()

