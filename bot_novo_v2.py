from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pyperclip
import time
import subprocess
import os
import json
import re

from datetime import datetime, timedelta


# ==========================
# CONFIGURAÇÕES
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_CLIENTES = os.path.join(
    BASE_DIR,
    "clientes.json"
)

ARQUIVO_ACESSO = os.path.join(
    BASE_DIR,
    "acesso.txt"
)

ARQUIVO_SEVENBOT = os.path.join(
    BASE_DIR,
    "sevenbot.py"
)

TEMPO_TESTE_HORAS = 6

LINK_SITE = "https://lively-tartufo-6c84e6.netlify.app/#planos"


# ==========================
# ABRIR WHATSAPP
# ==========================

driver = webdriver.Chrome(
    service=Service(
        ChromeDriverManager().install()
    )
)

driver.maximize_window()

driver.get(
    "https://web.whatsapp.com"
)

print("Escaneie o QR Code no WhatsApp Web.")

time.sleep(20)

print("WhatsApp conectado!")


# ==========================
# BANCO DE CLIENTES
# ==========================

def carregar_clientes():

    if not os.path.exists(ARQUIVO_CLIENTES):

        return {}

    try:

        with open(
            ARQUIVO_CLIENTES,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

            if isinstance(dados, dict):

                return dados

    except Exception as erro:

        print(
            "Erro carregando clientes.json:",
            erro
        )

    return {}


def salvar_clientes(clientes):

    with open(
        ARQUIVO_CLIENTES,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            clientes,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


# ==========================
# LIMPAR NÚMERO
# ==========================

def limpar_numero(numero):

    return re.sub(
        r"\D",
        "",
        numero
    )


# ==========================
# PEGAR NÚMERO DA CONVERSA
# ==========================

def pegar_contato():

    try:

        elementos = driver.find_elements(
            By.XPATH,
            "//header//span[@dir='auto']"
        )

        for elemento in elementos:

            texto = elemento.text.strip()

            numero = limpar_numero(texto)

            if len(numero) >= 10:

                return numero

        elementos = driver.find_elements(
            By.XPATH,
            "//span[@dir='auto']"
        )

        for elemento in elementos:

            texto = elemento.text.strip()

            numero = limpar_numero(texto)

            if len(numero) >= 10:

                return numero

    except Exception:

        pass

    return None


# ==========================
# VERIFICAR E RESPONDER CONVERSAS
# ==========================

def verificar_conversa_e_responder():

    try:

        contato_atual = pegar_contato()
        
        if contato_atual and "Griepo" not in contato_atual:

            mensagem_atual = pegar_ultima_mensagem_cliente()

            if mensagem_atual:

                mensagem_normalizada = mensagem_atual.lower().strip()

                if ultima_mensagem_por_contato.get(contato_atual) != mensagem_normalizada:

                    print(
                        "Nova mensagem no chat aberto de:",
                        contato_atual,
                        "->",
                        mensagem_atual
                    )

                    ultima_mensagem_por_contato[contato_atual] = mensagem_normalizada

                    processar_mensagem(contato_atual, mensagem_atual)

                    return

        conversas = driver.find_elements(
            By.XPATH,
            "//div[@role='gridcell']"
        )

        for conversa in conversas:

            try:

                nome_lista = conversa.text.strip()

                if not nome_lista or "Griepo" in nome_lista:

                    continue

                indicadores = conversa.find_elements(
                    By.XPATH,
                    ".//span[@aria-label and (contains(@aria-label, 'não lida') or contains(@aria-label, 'unread'))]"
                )

                if indicadores:

                    conversa.click()

                    time.sleep(1.5)

                    contato = pegar_contato()

                    if not contato:

                        continue

                    mensagem = pegar_ultima_mensagem_cliente()

                    if not mensagem:

                        continue

                    mensagem_normalizada = mensagem.lower().strip()

                    if ultima_mensagem_por_contato.get(contato) == mensagem_normalizada:

                        continue

                    print(
                        "Nova mensagem da lista de:",
                        contato,
                        "->",
                        mensagem
                    )

                    ultima_mensagem_por_contato[contato] = mensagem_normalizada

                    processar_mensagem(contato, mensagem)

                    break

            except Exception as erro:

                continue

    except Exception as erro:

        print(
            "Erro procurando conversas:",
            erro
        )


# ==========================
# PEGAR ÚLTIMA MENSAGEM DO CLIENTE
# ==========================

def pegar_ultima_mensagem_cliente():

    try:

        mensagens = driver.find_elements(
            By.XPATH,
            "//div[@data-pre-plain-text]"
        )

        mensagens_cliente = []

        for mensagem in mensagens:

            try:

                classe = mensagem.get_attribute(
                    "class"
                ) or ""

                if "message-in" in classe:

                    texto = mensagem.text.strip()

                    if texto:

                        mensagens_cliente.append(
                            texto
                        )

            except Exception:

                continue

        if not mensagens_cliente:

            mensagens = driver.find_elements(
                By.XPATH,
                "//div[@data-pre-plain-text]//span[contains(@class,'selectable-text')]"
            )

            for mensagem in mensagens:

                texto = mensagem.text.strip()

                if texto:

                    mensagens_cliente.append(
                        texto
                    )

        if not mensagens_cliente:

            return None

        return mensagens_cliente[-1]

    except Exception:

        return None


# ==========================
# ENVIAR MENSAGEM
# ==========================

def enviar_mensagem(texto):

    try:

        caixas = driver.find_elements(
            By.XPATH,
            "//div[@contenteditable='true']"
        )

        if not caixas:

            print(
                "Caixa de mensagem não encontrada."
            )

            return False

        caixa = caixas[-1]

        caixa.click()

        pyperclip.copy(
            texto
        )

        caixa.send_keys(
            Keys.CONTROL,
            "v"
        )

        caixa.send_keys(
            Keys.ENTER
        )

        print(
            "Mensagem enviada."
        )

        return True

    except Exception as erro:

        print(
            "Erro enviando mensagem:",
            erro
        )

        return False


# ==========================
# CRIAR TESTE IPTV
# ==========================

def criar_teste():

    try:

        if os.path.exists(
            ARQUIVO_ACESSO
        ):

            os.remove(
                ARQUIVO_ACESSO
            )

        if not os.path.exists(
            ARQUIVO_SEVENBOT
        ):

            print(
                "sevenbot.py não encontrado."
            )

            return None

        subprocess.Popen(
            [
                "python",
                ARQUIVO_SEVENBOT
            ],
            cwd=BASE_DIR
        )

        print(
            "Esperando acesso..."
        )

        for _ in range(60):

            if os.path.exists(
                ARQUIVO_ACESSO
            ):

                break

            time.sleep(1)

        if not os.path.exists(
            ARQUIVO_ACESSO
        ):

            print(
                "O acesso não foi criado dentro do tempo esperado."
            )

            return None

        with open(
            ARQUIVO_ACESSO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return arquivo.read().strip()

    except Exception as erro:

        print(
            "Erro criando teste:",
            erro
        )

        return None


# ==========================
# AVISAR CLIENTE ESPECÍFICO
# ==========================

def enviar_mensagem_para_contato(
    numero,
    texto
):

    try:

        driver.get(
            "https://web.whatsapp.com/send?phone="
            + numero
        )

        time.sleep(3)

        enviar_mensagem(
            texto
        )

    except Exception as erro:

        print(
            "Erro avisando cliente:",
            numero,
            erro
        )


# ==========================
# VERIFICAR TESTES VENCIDOS
# ==========================

def verificar_testes_vencidos():

    clientes = carregar_clientes()

    agora = datetime.now()

    alterou = False

    for numero, dados in clientes.items():

        if dados.get(
            "status"
        ) != "teste":

            continue

        try:

            vencimento = datetime.strptime(
                dados["fim"],
                "%d/%m/%Y %H:%M:%S"
            )

        except Exception as erro:

            print(
                "Data inválida para:",
                numero,
                erro
            )

            continue

        if agora >= vencimento:

            print(
                "Teste vencido:",
                numero
            )

            dados["status"] = "expirado"

            alterou = True

            enviar_mensagem_para_contato(
                numero,
                f"""
⏰ *Seu teste grátis de 6 horas chegou ao fim.*

Esperamos que tenha aproveitado a qualidade dos nossos canais e conteúdos! 🍿✨

💎 Para continuar assistindo sem interrupções, confira nossos planos diretamente pelo nosso site:
🔗 {LINK_SITE}
"""
            )

    if alterou:

        salvar_clientes(
            clientes
        )


# ==========================
# MEMÓRIA DAS MENSAGENS E ESTADOS
# ==========================

ultima_mensagem_por_contato = {}
estado_cliente = {}


# ==========================
# PROCESSAR MENSAGEM
# ==========================

def processar_mensagem(contato, mensagem):

    if not mensagem:

        return

    texto = mensagem.lower().strip()

    print(
        "Recebido de",
        contato,
        ":",
        texto
    )

    # Tratamento automático para as mensagens rápidas do site
    if "tenho interesse no plano de 1 mês" in texto:
        estado_cliente[contato] = "comprar"
        enviar_mensagem(
f"""
🔥 *PLANO 1 MÊS — R$ 20,00*

Excelente escolha! Para realizar o pagamento via PIX e liberar seu acesso imediato, utilize a chave abaixo:

🔑 *Chave PIX (E-mail):*
`sua-chave-pix-aqui`

👤 *Titular:* Seu Nome / Empresa

⚠️ *Importante:* Após realizar a transferência, envie o comprovante aqui mesmo no chat para ativarmos sua conta na hora! 🚀
🌐 Veja mais detalhes em: {LINK_SITE}
"""
        )
        return

    if "tenho interesse no plano de 2 meses" in texto:
        estado_cliente[contato] = "comprar"
        enviar_mensagem(
f"""
🔥 *PLANO 2 MESES — R$ 38,00*

Excelente escolha! Para realizar o pagamento via PIX e liberar seu acesso imediato, utilize a chave abaixo:

🔑 *Chave PIX (E-mail):*
`sua-chave-pix-aqui`

👤 *Titular:* Seu Nome / Empresa

⚠️ *Importante:* Após realizar a transferência, envie o comprovante aqui mesmo no chat para ativarmos sua conta na hora! 🚀
🌐 Veja mais detalhes em: {LINK_SITE}
"""
        )
        return

    if "tenho interesse no plano de 3 meses" in texto:
        estado_cliente[contato] = "comprar"
        enviar_mensagem(
f"""
🔥 *PLANO 3 MESES — R$ 56,00*

Excelente escolha! Para realizar o pagamento via PIX e liberar seu acesso imediato, utilize a chave abaixo:

🔑 *Chave PIX (E-mail):*
`sua-chave-pix-aqui`

👤 *Titular:* Seu Nome / Empresa

⚠️ *Importante:* Após realizar a transferência, envie o comprovante aqui mesmo no chat para ativarmos sua conta na hora! 🚀
🌐 Veja mais detalhes em: {LINK_SITE}
"""
        )
        return

    if "tenho interesse em conhecer a phzin tv" in texto or "vim pelo site e gostaria de mais informações" in texto:
        estado_cliente[contato] = "menu"
        enviar_mensagem(
f"""
📺 *MENU PHZIN TV*

Olá! Seja muito bem-vindo(a) ao nosso atendimento automático. 😊
Escolha uma das opções abaixo digitando apenas o número:
━━━━━━━━━━━━━━━━━━
1️⃣ 📦 Ver planos e assinar
2️⃣ 🎁 Solicitar teste grátis
3️⃣ 💳 Comprar assinatura
4️⃣ 🔄 Renovar plano
5️⃣ 🛠️ Suporte
6️⃣ 👨‍💼 Falar com um atendente
━━━━━━━━━━━━━━━━━━
🌐 Acesse nosso site oficial:
{LINK_SITE}

✍️ Responda apenas com o número da opção desejada.
"""
        )
        return

    etapa_atual = estado_cliente.get(contato, "")

    if texto in [
        "oi",
        "ola",
        "olá",
        "menu"
    ]:
        estado_cliente[contato] = "menu"

        enviar_mensagem(
f"""
📺 *MENU PHZIN TV*

Olá! Seja bem-vindo(a). 😊
Escolha uma das opções abaixo digitando apenas o número:
━━━━━━━━━━━━━━━━━━
1️⃣ 📦 Ver planos e assinar
2️⃣ 🎁 Solicitar teste grátis
3️⃣ 💳 Comprar assinatura
4️⃣ 🔄 Renovar plano
5️⃣ 🛠️ Suporte
6️⃣ 👨‍💼 Falar com um atendente
━━━━━━━━━━━━━━━━━━
🌐 Conheça nosso site oficial:
{LINK_SITE}

✍️ Responda apenas com o número da opção desejada.
"""
        )

        return

    # Se o cliente está escolhendo o aparelho (veio da opção 2)
    if etapa_atual == "escolhendo_aparelho":

        if texto == "1":
            estado_cliente[contato] = "gerando_1"

            enviar_mensagem(
"""
🤖 *CONFIGURAÇÃO - ANDROID / TV BOX*

1️⃣ Acesse a *Google Play Store* do seu aparelho.
2️⃣ Baixe e instale o aplicativo recomendado:
   • *XCIPTV Player*

📥 *Aplicativo baixado e instalado com sucesso?*
Digite 👉 *1* para receber seu teste grátis instantaneamente! 🚀
🔙 Digite 👉 *0* para voltar e escolher outro aparelho.
"""
            )

            return

        elif texto == "2":
            estado_cliente[contato] = "gerando_2"

            enviar_mensagem(
"""
🍏 *CONFIGURAÇÃO - IPHONE / IPAD (iOS) / APPLE TV*

1️⃣ Acesse a *App Store* do seu dispositivo Apple.
2️⃣ Baixe e instale o aplicativo recomendado:
   • *Smarters Player Lite*

📥 *Aplicativo baixado e instalado com sucesso?*
Digite 👉 *1* para receber seu teste grátis instantaneamente! 🚀
🔙 Digite 👉 *0* para voltar e escolher outro aparelho.
"""
            )

            return

        elif texto == "3":
            estado_cliente[contato] = "gerando_3"

            enviar_mensagem(
"""
📺 *CONFIGURAÇÃO - SMART TV (SAMSUNG / LG / ROKU)*

1️⃣ Abra a loja de aplicativos da sua Smart TV.
2️⃣ Procure e instale um dos aplicativos abaixo:
   • *IBO Player (ou IBO Pro)*
   • *Smart IPTV*
   • *Duplex IPTV*

📥 *Aplicativo instalado na sua TV?*
Digite 👉 *1* para receber seu teste grátis instantaneamente! 🚀
🔙 Digite 👉 *0* para voltar e escolher outro aparelho.
"""
            )

            return

        elif texto == "4":
            estado_cliente[contato] = "gerando_4"

            enviar_mensagem(
"""
🔥 *CONFIGURAÇÃO - FIRE STICK TV*

📦 *1º Método*
1. Instale o Downloader by aftvNews (encontre na PlayStore)
2. Abra ele e digite `1264106` na barra de cima e clique em Go
3. Install → Instalar → Abrir

📦 *2º Método*
1. No aparelho que vai usar abra o navegador de internet (Chrome)
2. Digite `dl.ntdev.in/55296` na barra de cima e clique ok (não clica em pesquisar)
3. Install → Instalar → Abrir

📥 *Aplicativo aberto com sucesso?*
Digite 👉 *1* para receber seu teste grátis instantaneamente! 🚀
🔙 Digite 👉 *0* para voltar e escolher outro aparelho.
"""
            )

            return

    # Se o cliente já escolheu o aparelho e está na tela de confirmação do teste
    if etapa_atual in ["gerando_1", "gerando_2", "gerando_3", "gerando_4"]:

        if texto == "0":
            estado_cliente[contato] = "escolhendo_aparelho"

            enviar_mensagem(
"""
📱 *ESCOLHA SEU APARELHO PARA O PASSO A PASSO:*

Antes de gerar o seu teste, escolha em qual aparelho você vai assistir:

1️⃣ *Celular Android / TV Box*
2️⃣ *iPhone / iPad (iOS) / Apple TV*
3️⃣ *Smart TV (Samsung / LG / Roku)*
4️⃣ *Fire Stick TV*

✍️ Digite o número correspondente ao seu aparelho (1, 2, 3 ou 4).
"""
            )

            return

        elif texto == "1":

            clientes = carregar_clientes()

            if contato in clientes:
                return

            enviar_mensagem(
                "⏳ *Gerando seu acesso exclusivo, aguarde um instante...*"
            )

            acesso = criar_teste()

            if not acesso:

                enviar_mensagem(
                    "❌ Ocorreu uma instabilidade ao gerar o teste. Por favor, tente novamente em instantes ou digite *6* para falar com o suporte."
                )

                return

            agora = datetime.now()

            fim = agora + timedelta(
                hours=TEMPO_TESTE_HORAS
            )

            clientes[contato] = {

                "numero": contato,

                "data": agora.strftime(
                    "%d/%m/%Y"
                ),

                "hora": agora.strftime(
                    "%H:%M:%S"
                ),

                "inicio": agora.strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),

                "fim": fim.strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),

                "status": "teste"
            }

            salvar_clientes(
                clientes
            )

            estado_cliente[contato] = "ativo"

            enviar_mensagem(
                f"""
🎉 *TESTE GERADO COM SUCESSO!*

⏱️ Validade: *6 horas* a partir de agora.

Aqui estão os seus dados de acesso:
{acesso}

💡 *Dica:* Insira os dados exatamente como enviados no aplicativo escolhido. Bom divertimento! 🍿📺

🌐 Confira nossos planos e pacotes oficiais em nosso site:
{LINK_SITE}
"""
            )

            print(
                "Cliente salvo:",
                contato
            )

            return

    if texto == "1":
        estado_cliente[contato] = "planos"

        enviar_mensagem(
f"""
📦 *NOSSOS PLANOS E ASSINATURAS*

Para conferir todos os nossos planos detalhados, valores promocionais e assinar com total praticidade, acesse o nosso site oficial:

🔗 {LINK_SITE}

Após realizar a assinatura ou se tiver alguma dúvida, digite *3* para enviar o comprovante ou *6* para falar com um atendente. 🚀
"""
        )

        return

    if texto == "2":

        clientes = carregar_clientes()

        if contato in clientes:

            enviar_mensagem(
f"""
⚠️ *O seu período de teste grátis já foi utilizado anteriormente.*

💎 Para continuar desfrutando de toda a nossa programação sem limites por um preço super acessível, confira nossos planos e assine diretamente pelo site:
🔗 {LINK_SITE}
"""
            )

            return

        estado_cliente[contato] = "escolhendo_aparelho"

        enviar_mensagem(
"""
📱 *ESCOLHA SEU APARELHO PARA O PASSO A PASSO:*

Antes de gerar o seu teste, escolha em qual aparelho você vai assistir:

1️⃣ *Celular Android / TV Box*
2️⃣ *iPhone / iPad (iOS) / Apple TV*
3️⃣ *Smart TV (Samsung / LG / Roku)*
4️⃣ *Fire Stick TV*

✍️ Digite o número correspondente ao seu aparelho (1, 2, 3 ou 4).
"""
        )

        return

    if texto == "3":
        estado_cliente[contato] = "comprar"

        enviar_mensagem(
f"""
💳 *COMPRAR ASSINATURA*

Para efetuar sua compra com total segurança, ver as opções de pagamento e planos disponíveis, acesse:
🔗 {LINK_SITE}

⚠️ *Importante:* Após realizar o pagamento, envie o comprovante aqui mesmo no chat para ativarmos seu acesso na hora! 🚀
"""
        )

        return

    if texto == "4":
        estado_cliente[contato] = "renovar"

        enviar_mensagem(
f"""
🔄 *RENOVAÇÃO DE PLANO*

Para renovar o seu acesso e continuar assistindo sem interrupções, confira os valores e opções de renovação no site:
🔗 {LINK_SITE}

⚠️ *Importante:* Envie o comprovante do pagamento aqui no chat para renovarmos o seu acesso imediatamente! 🚀
"""
        )

        return

    if texto == "5":
        estado_cliente[contato] = "suporte"

        enviar_mensagem(
f"""
🛠️ *SUPORTE TÉCNICO*

Está tendo dificuldades com o aplicativo ou com o acesso? 

1. Verifique sua conexão com a internet.
2. Reinicie o aplicativo ou limpe o cache.
3. Se precisar de mais informações, acesse: {LINK_SITE}
4. Se o erro persistir, digite *6* para falar diretamente com um atendente. 🤝
"""
        )

        return

    if texto == "6":
        estado_cliente[contato] = "atendente"

        enviar_mensagem(
"""
👨‍💼 *ATENDIMENTO HUMANIZADO*

Sua solicitação foi registrada com sucesso. Um de nossos atendentes irá te responder em instantes. 

Por favor, aguarde só um momento! 🤝
"""
        )

        return


# ==========================
# LOOP PRINCIPAL
# ==========================

print(
    "Bot iniciado."
)

ultimo_check_vencidos = 0


while True:

    try:

        agora_timestamp = time.time()

        if (
            agora_timestamp
            - ultimo_check_vencidos
            >= 60
        ):

            verificar_testes_vencidos()

            ultimo_check_vencidos = (
                agora_timestamp
            )

        verificar_conversa_e_responder()

        time.sleep(2)

    except Exception as erro:

        print(
            "Erro no loop principal:",
            erro
        )

        time.sleep(3)