from bs4 import BeautifulSoup
import requests

# URL do carrossel de ofertas do Mercado Livre
url = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-4&category=MLB1055&promotion_type=deal_of_the_day#deal_print_id=de8f40a0-1799-11ef-ae3e-8f8caf3e79ed&c_id=carouseldynamic-normal&c_element_order=undefined&c_campaign=VER-MAIS&c_uid=de8f40a0-1799-11ef-ae3e-8f8caf3e79ed'
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Lista para armazenar os produtos
produtos = []

# Iterar pelos itens do carrossel
for item in soup.find_all('div', class_='promotions_boxed-width'):
    nome = item.find('h2').text

    # Procurar pelo preço original dentro do span aninhado
    span_preco_original = item.find('span', class_='dynamic-carousel__oldprice')
    if span_preco_original:
        preco_original = float(span_preco_original.find('span').text.replace('R$', '').replace(',', '.'))
    else:
        preco_original = None  # Caso não haja preço original, definir como None

    # Procurar pelo preço com desconto
    span_preco_desconto = item.find('span', class_='dynamic-carousel__price')
    if span_preco_desconto:
        preco_desconto = float(span_preco_desconto.text.replace('R$', '').replace(',', '.'))
    else:
        preco_desconto = None  # Caso não haja preço com desconto, definir como None

    # Calcular o percentual de desconto se ambos os preços estão disponíveis
    if preco_original and preco_desconto:
        desconto = (preco_original - preco_desconto) / preco_original * 100
        if desconto > 15:
            produtos.append({
                'Nome': nome,
                'Preço Original': preco_original,
                'Preço com Desconto': preco_desconto,
                'Percentual de Desconto': desconto
            })

# Criar um DataFrame com os produtos
import pandas as pd
df = pd.DataFrame(produtos)

# Ordenar o DataFrame em ordem alfabética pelo nome do produto
df = df.sort_values(by='Nome')

# Salvar o DataFrame em um arquivo CSV
df.to_csv('produtos_mercado_livre.csv', index=False)

# Calcular estatísticas
media = df['Percentual de Desconto'].mean()
mediana = df['Percentual de Desconto'].median()
desvio_padrao = df['Percentual de Desconto'].std()

# Exibir estatísticas
print(f'Média: {media:.2f}%')
print(f'Mediana: {mediana:.2f}%')
print(f'Desvio Padrão: {desvio_padrao:.2f}%')

# Criar boxplot para visualizar a distribuição dos descontos
import matplotlib.pyplot as plt

plt.boxplot(df['Percentual de Desconto'])
plt.title('Distribuição dos Descontos')
plt.ylabel('Percentual de Desconto')
plt.show()

