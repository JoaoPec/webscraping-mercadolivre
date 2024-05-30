from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Função para obter a escolha da marca pelo usuário
def getBrandChoice():
    print("Escolha uma marca de celular para pesquisar:")
    print("1. Motorola")
    print("2. Samsung")
    print("3. Apple")
    print("4. Todas")

    choice = input("Digite o número da sua escolha: ")

    if choice == '1':
        return "Motorola"
    elif choice == '2':
        return "Samsung"
    elif choice == '3':
        return "Apple"
    elif choice == '4':
        return "Todas"
    else:
        print("Escolha inválida. Por favor, tente novamente.")
        return getBrandChoice()

def extractProducts(soup, brand):
    products = []
    brands_counter = Counter()

    itemsContainer = soup.find('ol', class_='items_container')

    if itemsContainer:
        for item in itemsContainer.find_all('li', class_='promotion-item'):
            nameTag = item.find('p', class_='promotion-item__title')
            if nameTag:
                name = nameTag.text.strip()
            else:
                continue

            # Determina a marca do produto
            product_brand = None
            for b in ['Motorola', 'Samsung', 'Apple']:
                if b.lower() in name.lower():
                    product_brand = b
                    brands_counter[b] += 1
                    break

            # Se a escolha foi "Todas" ou se a marca do produto é a escolhida pelo usuário
            if brand == 'Todas' or (product_brand and product_brand.lower() in brand.lower()):
                # Extrai o URL do produto
                url = item.find('a', class_='promotion-item__link-container')['href']

                # Adiciona o produto à lista
                products.append({
                    'Nome': name,
                    'Marca': product_brand,
                    'Preço Original': get_price(item, 's', 'andes-money-amount andes-money-amount-combo__previous-value andes-money-amount--previous andes-money-amount--cents-superscript'),
                    'Preço com Desconto': get_price(item, 'span', 'andes-money-amount__fraction'),
                    'Link': url,
                })

    return products, brands_counter

# Função para obter o preço de um produto
def get_price(item, tag, class_name):
    price_tag = item.find(tag, class_=class_name)
    if price_tag:
        price_text = price_tag.text.replace('R$', '').strip()
        try:
            return float(price_text.replace('.', '').replace(',', '.').strip())
        except ValueError:
            print(f'Erro ao converter o preço: {price_text}')
    return None

# Função para iniciar a busca e gerar relatórios
def startSearch(brand):
    urlPage1 = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779535-1&domain_id=MLB-CELLPHONES'
    urlPage2 = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779535-1&domain_id=MLB-CELLPHONES&page=2'
    headers = {"User-Agent": "Mozilla/5.0"}

    responsePage1 = requests.get(urlPage1, headers=headers)
    soupPage1 = BeautifulSoup(responsePage1.text, 'html.parser')
    productsPage1, brands_counter1 = extractProducts(soupPage1, brand)

    responsePage2 = requests.get(urlPage2, headers=headers)
    soupPage2 = BeautifulSoup(responsePage2.text, 'html.parser')
    productsPage2, brands_counter2 = extractProducts(soupPage2, brand)

    products = productsPage1 + productsPage2
    brands_counter = brands_counter1 + brands_counter2

    df = pd.DataFrame(products)

    df = df.sort_values(by='Marca')  # Corrigindo a ordenação para a coluna 'Marca'

    df.to_csv('mercado_livre_products.csv', index=False)

    # Inicializando o writer do Excel com xlsxwriter
    with pd.ExcelWriter('mercado_livre_products.xlsx', engine='xlsxwriter') as writer:
        # Adicionando o DataFrame ao arquivo Excel
        df.to_excel(writer, index=False, sheet_name='Produtos')

    # Calculando e exibindo as estatísticas, e mostrando o gráfico de caixa
    mean_discount = df['Preço com Desconto'].mean()
    median_discount = df['Preço com Desconto'].median()
    stdDev_discount = df['Preço com Desconto'].std()

    print(f'Média dos preços com desconto: R${mean_discount:.2f}')
    print(f'Mediana dos preços com desconto: R${median_discount:.2f}')
    print(f'Desvio Padrão dos preços com desconto: R${stdDev_discount:.2f}')

    moda_discount = df['Preço com Desconto'].mode()
    print(f'Desconto mais comum (moda): R${moda_discount.values[0]:.2f}')

    print('Frequência de marcas em promoção:')
    for brand, count in brands_counter.items():
        print(f'{brand}: {count}')

    # Plota e exibe o gráfico de caixa
    plt.boxplot(df['Preço com Desconto'])
    plt.title('Distribuição dos Descontos')
    plt.ylabel('Preço com Desconto (R$)')

    plt.savefig('discount_boxplot.png')

    plt.show()

# Menu no terminal para o usuário escolher a marca
selectedBrand = getBrandChoice()
startSearch(selectedBrand)
