from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import time
import re
import sys
import os

# =====================================
# CORREÇÃO UTF-8 NO WINDOWS
# =====================================
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except:
    pass

# =====================================
# CONFIGURAÇÕES
# =====================================
EMAIL = "davisantos108@gmail.com"
SENHA = "Jpestraga021."
URL = "http://cdnroxo.top"

# Nome exato do teste conforme aparece no painel
NOME_DO_TESTE = "TESTE COMPLETO IPTV 6H"

# =====================================
# INICIAR NAVEGADOR
# =====================================
options = webdriver.ChromeOptions()
# options.add_argument("--headless") # Descomente se quiser rodar sem abrir a janela do Chrome

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get("https://seventvpainel.top/#/sign-in")
    print("Site aberto")

    wait = WebDriverWait(driver, 15)

    # =====================================
    # LOGIN
    # =====================================
    campos = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
    print("Campos de login encontrados:", len(campos))

    campos[0].clear()
    campos[0].send_keys(EMAIL)
    campos[1].clear()
    campos[1].send_keys(SENHA)
    print("Login preenchido!")

    botoes = driver.find_elements(By.TAG_NAME, "button")
    botoes[0].click()
    print("Botão de login clicado!")

    # Aguarda redirecionar e entrar no painel
    time.sleep(8)
    print("Entrou no painel!")

    # =====================================
    # FECHAR AVISO/MODAL (SE HOUVER)
    # =====================================
    try:
        botoes = driver.find_elements(By.TAG_NAME, "button")
        for botao in botoes:
            texto_botao = botao.text.strip().lower()
            if "ok" in texto_botao or "fechar" in texto_botao or "ocultar" in texto_botao:
                botao.click()
                print("Aviso fechado!")
                break
    except:
        pass

    time.sleep(2)

    # =====================================
    # LOCALIZAR E CLICAR NO TESTE
    # =====================================
    print(f"Procurando o botão: '{NOME_DO_TESTE}'...")

    # XPath flexível que ignora maiúsculas/minúsculas e busca pelo texto do teste
    xpath_teste = f"//*[contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{NOME_DO_TESTE.upper()}')]"

    # Tenta achar o elemento diretamente
    elementos = driver.find_elements(By.XPATH, xpath_teste)

    # Se não achar de primeira, rola a página um pouco para baixo
    if not elementos:
        print("Rolando a página para carregar o bloco de testes...")
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(2)
        elementos = driver.find_elements(By.XPATH, xpath_teste)

    if elementos:
        elemento = elementos[0]

        # Centraliza o botão na visão do navegador
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        time.sleep(1)

        try:
            elemento.click()
            print("✅ Teste clicado via clique normal!")
        except:
            driver.execute_script("arguments[0].click();", elemento)
            print("✅ Teste clicado via JavaScript!")

    else:
        raise Exception(f"Não foi possível encontrar o botão com o texto '{NOME_DO_TESTE}'.")

    # =====================================
    # AGUARDAR E CAPTURAR O ACESSO GERADO
    # =====================================
    print("Aguardando criação do acesso...")
    time.sleep(6)

    texto_pagina = driver.find_element(By.TAG_NAME, "body").text

    # Procurar por marcadores comuns de sucesso ou pegar dados gerados
    inicio = texto_pagina.find("ACESSO CRIADO COM SUCESSO")
    if inicio == -1:
        inicio = texto_pagina.find("Usuário") # Caso não tenha a frase 'ACESSO CRIADO', tenta pelo 'Usuário'

    if inicio != -1:
        acesso_bruto = texto_pagina[inicio:inicio + 1500]
        print("Acesso capturado do painel!")

        # Extrair com Expressões Regulares (Regex)
        usuario_match = re.search(r"Usuário\s*:?\s*([^\n]+)", acesso_bruto, re.IGNORECASE)
        senha_match = re.search(r"Senha\s*:?\s*([^\n]+)", acesso_bruto, re.IGNORECASE)
        vencimento_match = re.search(r"Vencimento\s*:?\s*([^\n]+)", acesso_bruto, re.IGNORECASE)

        usuario_texto = usuario_match.group(1).strip() if usuario_match else "Não localizado"
        senha_texto = senha_match.group(1).strip() if senha_match else "Não localizada"
        vencimento_texto = vencimento_match.group(1).strip() if vencimento_match else "6 Horas"

        # Formatar Mensagem Final
        mensagem = (
            f"👤 Usuário: {usuario_texto}\n\n"
            f"🔑 Senha: {senha_texto}\n\n"
            f"🗓️ Vencimento: {vencimento_texto}\n\n"
            f"🌐 URL: {URL}"
        )

        print("\n================ TEXTO DO ACESSO ================")
        print(mensagem)
        print("==================================================\n")

        # Salvar no arquivo acesso.txt
        caminho_acesso = os.path.join(os.path.dirname(os.path.abspath(__file__)), "acesso.txt")
        with open(caminho_acesso, "w", encoding="utf-8") as arquivo:
            arquivo.write(mensagem)

        print("✅ Acesso gravado com sucesso no arquivo 'acesso.txt'!")

    else:
        print("❌ O acesso não foi encontrado na página.")
        print("Texto completo capturado:\n", texto_pagina)

except Exception as erro:
    print("\n====================")
    print("ERRO NO SEVENBOT.PY:")
    print(erro)
    print("====================\n")

finally:
    print("Finalizando execução do Python...")
    try:
        driver.quit() # Fecha o navegador para liberar memória
    except:
        pass