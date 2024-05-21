from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt

url = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-4&category=MLB1055&promotion_type=deal_of_the_day#deal_print_id=de8f40a0-1799-11ef-ae3e-8f8caf3e79ed&c_id=carouseldynamic-normal&c_element_order=undefined&c_campaign=VER-MAIS&c_uid=de8f40a0-1799-11ef-ae3e-8f8caf3e79ed'
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

produtos = []

items_container = soup.find('ol', class_='items_container')

if items_container:

    for item in items_container.find_all('li', class_='promotion-item'):

        nome_tag = item.find('p', class_='promotion-item__title')
        if nome_tag:
            nome = nome_tag.text.strip()
        else:
            continue

        span_preco_desconto = item.find('s', class_='andes-money-amount andes-money-amount-combo__previous-value andes-money-amount--previous andes-money-amount--cents-superscript')
        if span_preco_desconto:
            span_preco_desconto.string = span_preco_desconto.text.replace('R$', '').strip()
            preco_desconto = float(span_preco_desconto.text.replace('.', '').replace(',', '.').strip())
            print(f'Preço com desconto encontrado para o produto "{nome}": R${preco_desconto:.2f}')
        else:
            preco_desconto = None
            print(f'Preço com desconto não encontrado para o produto "{nome}"')

        span_preco_original = item.find('span', class_='andes-money-amount__fraction')
        if span_preco_original:
            preco_original = float(span_preco_original.text.replace('.', '').replace(',', '.').strip())
            print(f'Preço original encontrado para o produto "{nome}": R${preco_original:.2f}')
        else:
            preco_original = None
            print(f'Preço original não encontrado para o produto "{nome}"')

        if preco_original and preco_desconto:
            desconto = (preco_original - preco_desconto) / preco_original * 100
            produtos.append({
                'Nome': nome,
                'Preço Original': preco_original,
                'Preço com Desconto': preco_desconto,
                'Percentual de Desconto': desconto
            })

df = pd.DataFrame(produtos)

df = df.sort_values(by='Nome')

df.to_csv('produtos_mercado_livre.csv', index=False)

media = df['Percentual de Desconto'].mean()
mediana = df['Percentual de Desconto'].median()
desvio_padrao = df['Percentual de Desconto'].std()

print(f'Média: {media:.2f}%')
print(f'Mediana: {mediana:.2f}%')
print(f'Desvio Padrão: {desvio_padrao:.2f}%')

plt.boxplot(df['Percentual de Desconto'])
plt.title('Distribuição dos Descontos')
plt.ylabel('Percentual de Desconto')

plt.savefig('boxplot.png')
