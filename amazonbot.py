import local

import json
import requests
import smtplib
import sys

from bs4 import BeautifulSoup
from email.mime.text import MIMEText


def main(usar_html_local=False):
    if usar_html_local:
        with open('wishlist.html', 'r', encoding='utf8') as wishlist_html:
            document = wishlist_html.read()
    else:
        #document = requests.get('https://www.amazon.com.br/gp/registry/wishlist/3I4247OZ2RR2W/ref=nav_wishlist_lists_1').text
        document = requests.get('https://www.amazon.com.br/hz/wishlist/ls/3I4247OZ2RR2W?filter=DEFAULT&sort=default&lek=11f37f9a-507e-44c3-92d6-46c339c97a3b&type=wishlist&ajax=false').text

    soup = BeautifulSoup(document, 'html.parser')

    # buscar o nome da lista de desejos
    print(soup.find('span', id='profile-list-name').text)

    dicionario = {}
    for div in soup.find_all('div', class_="a-text-left a-fixed-left-grid-col g-item-sortable-padding a-col-right"):
        titulo = div.find("a", class_="a-link-normal a-declarative").text
        valor = div.find("span", class_="a-offscreen")
        if valor is not None:
            valor = div.find("span", class_="a-offscreen").text
            novo_valor = valor.split('R$ ')[1]
            novo_valor = novo_valor.replace(',', '.')
            novo_valor = float(novo_valor)
            dicionario[titulo] = {}
            dicionario[titulo]={'string': valor}
            dicionario[titulo]['inteiro']= novo_valor
        else:
            novo_valor = None
            dicionario[titulo] = {}
            dicionario[titulo] = {'string': None}
            dicionario[titulo]['inteiro'] = novo_valor

    with open('dicionario.json','r', encoding='utf8') as f:
        leitura = f.read()
        dicionario_anterior = json.loads(leitura)
        
        for titulo, _ in dicionario.items():
            if titulo in dicionario_anterior:
                if dicionario[titulo]['inteiro'] is not None and dicionario_anterior[titulo]['inteiro'] is None:
                    email = MIMEText("O livro {} está disponível no estoque novamente.".format(titulo))
                    email['Subject'] = 'Amazon Bot'
                    email['From'] = 'Amazon Bot <carteiro@sitedoicaro.not.br>'
                    email['To'] = 'aledskywalker@gmail.com'

                    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
                    s.starttls()  # transforma em conexão segura
                    s.login(local.SMTP_USER,local.SMTP_PASSWORD)
                    s.send_message(email)
                    s.quit()

                elif dicionario[titulo]['inteiro'] is not None and dicionario_anterior[titulo]['inteiro'] is not None and dicionario[titulo]['inteiro'] < dicionario_anterior[titulo]['inteiro']:
                    email = MIMEText("Houve alteração de preço no livro {} de {} para {}".format(titulo, dicionario_anterior[titulo]['string'], dicionario[titulo]['string']))
                    email['Subject'] = 'Amazon Bot'
                    email['From'] = 'Amazon Bot <carteiro@sitedoicaro.not.br>'
                    email['To'] = 'aledskywalker@gmail.com'

                    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
                    s.starttls()  # transforma em conexão segura
                    s.login(local.SMTP_USER,local.SMTP_PASSWORD)
                    s.send_message(email)
                    s.quit()

    # Escreve o resultado da busca da Wishlist em um arquivo json local
    resultado_wishlist_json = json.dumps(dicionario, indent=2)
    with open('dicionario.json', 'w') as arquivo_wishlist_json:
        arquivo_wishlist_json.write(resultado_wishlist_json)


if __name__ == '__main__':
    usar_html_local = False
    if len(sys.argv) > 1:
        usar_html_local = bool(sys.argv[1])
    main(usar_html_local)
