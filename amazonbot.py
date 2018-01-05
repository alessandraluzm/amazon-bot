from bs4 import BeautifulSoup


def exemplo():
    wishlist = [
        ("Guerra e Paz", 59.90),
        ("Ana Karerina", 80.00),
        ("Revolução dos Bichos", 25.59)
    ]
    print(wishlist)
    # percorrer a wishlist e fazer o print de cada item no formato: "Livro: Guerra e Paz - Preço: 25.90"
    for tupla_da_wishlist in wishlist:
        print("Livro:{}  Preço:{}".format(tupla_da_wishlist[0], tupla_da_wishlist[1]))

def main():
    with open('wishlist.html', 'r', encoding='utf8') as wishlist_html:
        document = wishlist_html.read()

    soup = BeautifulSoup(document, 'html.parser')

    # buscar o nome da lista de desejos
    print(soup.find('span', id='profile-list-name').text)

    dicionario = {} 
    for div in soup.find_all('div', class_="a-text-left a-fixed-left-grid-col g-item-sortable-padding a-col-right"):
        titulo = div.find("a", class_="a-link-normal a-declarative").text
        valor = div.find("span", class_="a-offscreen").text
        novo_valor = valor.split('R$ ')[1]
        novo_valor = novo_valor.replace(',', '.')
        novo_valor = float(novo_valor)
        print(novo_valor)
        dicionario[titulo] = {}
        dicionario[titulo]={'string': valor}
        dicionario[titulo]['inteiro']= novo_valor        
        
    print(dicionario)

    with open('dicionario.json','r', encoding='utf8') as f:
        leitura = f.read()
        import json
        dicionario_anterior = json.loads(leitura)
        
        for key, value in dicionario.items():
            if key in dicionario_anterior:
                if dicionario[key]['inteiro'] < dicionario_anterior[key]['inteiro']:
                    print('Value: {}'.format(dicionario[key]['inteiro']))
    # carregar o dicionario antigo do arquivo
    # iterar sobre os itens do dicionario antigo e comparar com o atual os preços
    # se o preço atual for menor que o antigo, printar o livro

    with open('dicionario.json', 'r', encoding='utf8') as f:
        a = f.read()
        #print(a)

        import json
        s = json.dumps(dicionario, indent=2)
        #with open('dicionario.json', 'w') as f:
          #  f.write(s)

def leitura():
    with open('dicionario.json', 'r') as f:
        s = f.read()

    import json 
    dicionario = json.loads(s)
    print(dicionario)
    # dictionary & json: salvar a lista de livros e seus valores em um arquivo com um dicionario serializado no formato json


if __name__ == '__main__':
    main()
