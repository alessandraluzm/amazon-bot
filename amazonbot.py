import local

import json
import requests
import smtplib
import sys

from bs4 import BeautifulSoup
from email.mime.text import MIMEText


WISHLIST_URL = 'https://www.amazon.com.br/gp/registry/wishlist/3I4247OZ2RR2W/'


def main(usar_html_local=False):
    # Abertura da wishlist de teste para carregamento mais rápido
    if usar_html_local:
        with open('wishlist.html', 'r', encoding='utf8') as wishlist_html:
            document = wishlist_html.read()
    # Carregamento da página de Wishlist direto do site da Amazon
    else:
        document = requests.get(WISHLIST_URL).text

    soup = BeautifulSoup(document, 'html.parser')

    # Criação do dicionário contendo os títulos e preços dos livros
    dicionario = {}
    for div in soup.find_all('div', class_="a-text-left a-fixed-left-grid-col g-item-sortable-padding a-col-right"):
        titulo = div.find("a", class_="a-link-normal a-declarative").text
        valor_string = div.find("span", class_="a-offscreen")
        # Se existir o livro em estoque armazena os preços
        if valor_string is not None:
            valor_string = div.find("span", class_="a-offscreen").text
            # Para converção do novo_valor para float, foi necessária a mudança de , para . e a remoção do R$
            valor_float = valor_string.split('R$ ')[1]
            valor_float = valor_float.replace(',', '.')
            valor_float = float(valor_float)
            dicionario[titulo] = {}
            dicionario[titulo] = {'string': valor_string}
            dicionario[titulo]['inteiro'] = valor_float
        # Se o livro não existir em estoque armazena como None
        else:
            dicionario[titulo] = {}
            dicionario[titulo] = {'string': None}
            dicionario[titulo]['inteiro'] = None

    # Comparação dos preços antigos do arquivo JSON com os novos que vêm da página da Wishlist
    # Após a comparação, envia um e-mail de acordo com a situação do produto
    with open('dicionario.json','r', encoding='utf8') as arquivo_wishlist_json:
        dicionario_anterior = json.loads(arquivo_wishlist_json.read()) # carrega o arquivo JSON e transforma no dicionário
        for titulo, _ in dicionario.items():
            if titulo in dicionario_anterior:
                # Se um produto retornar ao estoque, notifica por e-mail
                if dicionario[titulo]['inteiro'] is not None and dicionario_anterior[titulo]['inteiro'] is None:
                    email = MIMEText("O livro {} está disponível no estoque novamente.".format(titulo))
                # Se houver redução de preço, envia um e-mail notificando
                elif dicionario[titulo]['inteiro'] is not None and dicionario_anterior[titulo]['inteiro'] is not None and dicionario[titulo]['inteiro'] < dicionario_anterior[titulo]['inteiro']:
                    email = MIMEText("Houve alteração de preço no livro {} de {} para {}".format(titulo, dicionario_anterior[titulo]['string'], dicionario[titulo]['string']))
                else:
                    email = None
                if email is not None:
                    email['Subject'] = 'Amazon Bot'
                    email['From'] = 'Amazon Bot <carteiro@sitedoicaro.not.br>'
                    email['To'] = 'aledskywalker@gmail.com'
                    smtp = smtplib.SMTP(host='smtp.gmail.com', port=587)
                    smtp.starttls()  # transforma em conexão segura
                    smtp.login(local.SMTP_USER,local.SMTP_PASSWORD)  # login substituido por constantes para proteção dos dados
                    smtp.send_message(email)
                    smtp.quit()

    # Escreve o resultado da busca da Wishlist em um arquivo json local
    resultado_wishlist_json = json.dumps(dicionario, indent=2)
    with open('dicionario.json', 'w') as arquivo_wishlist_json:
        arquivo_wishlist_json.write(resultado_wishlist_json)


if __name__ == '__main__':
    usar_html_local = False
    if len(sys.argv) > 1:
        usar_html_local = bool(sys.argv[1])
    main(usar_html_local)
