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
    brandsCounter = Counter()

    itemsContainer = soup.find('ol', class_='items_container')

    if itemsContainer:
        for item in itemsContainer.find_all('li', class_='promotion-item'):
            nameTag = item.find('p', class_='promotion-item__title')
            if nameTag:
                name = nameTag.text.strip()
            else:
                continue

            # Determina a marca do produto
            productBrand = None
            for b in ['Motorola', 'Samsung', 'Apple']:
                if b.lower() in name.lower():
                    productBrand = b
                    brandsCounter[b] += 1
                    break

            # Se a escolha foi "Todas" ou se a marca do produto é a escolhida pelo usuário
            if brand == 'Todas' or (productBrand and productBrand.lower() in brand.lower()):
                # Extrai o URL do produto
                url = item.find('a', class_='promotion-item__link-container')['href']

                # Obtém os preços
                originalPrice = getPrice(item, 's', 'andes-money-amount andes-money-amount-combo__previous-value andes-money-amount--previous andes-money-amount--cents-superscript')
                discountPrice = getPrice(item, 'span', 'andes-money-amount__fraction')

                # Calcula o percentual de desconto, se ambos os preços estiverem disponíveis
                discountPercent = ((originalPrice - discountPrice) / originalPrice * 100) if originalPrice and discountPrice else None

                # Adiciona o produto à lista
                products.append({
                    'Nome': name,
                    'Marca': productBrand,
                    'Preço Original': originalPrice,
                    'Preço com Desconto': discountPrice,
                    'Percentual de Desconto': round(discountPercent, 2) if discountPercent is not None else None,
                    'Link': url,
                })

    return products, brandsCounter

# Função para obter o preço de um produto
def getPrice(item, tag, className):
    priceTag = item.find(tag, class_=className)
    if priceTag:
        priceText = priceTag.text.replace('R$', '').strip()
        try:
            return float(priceText.replace('.', '').replace(',', '.').strip())
        except ValueError:
            print(f'Erro ao converter o preço: {priceText}')
    return None

# Função para iniciar a busca e gerar relatórios
def startSearch(brand):
    urlPage1 = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779535-1&domain_id=MLB-CELLPHONES'
    urlPage2 = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779535-1&domain_id=MLB-CELLPHONES&page=2'
    headers = {"User-Agent": "Mozilla/5.0"}

    responsePage1 = requests.get(urlPage1, headers=headers)
    soupPage1 = BeautifulSoup(responsePage1.text, 'html.parser')
    productsPage1, brandsCounter1 = extractProducts(soupPage1, brand)

    responsePage2 = requests.get(urlPage2, headers=headers)
    soupPage2 = BeautifulSoup(responsePage2.text, 'html.parser')
    productsPage2, brandsCounter2 = extractProducts(soupPage2, brand)

    products = productsPage1 + productsPage2
    brandsCounter = brandsCounter1 + brandsCounter2

    df = pd.DataFrame(products)

    df = df.sort_values(by='Marca')  # Corrigindo a ordenação para a coluna 'Marca'

    df.to_csv('mercado_livre_products.csv', index=False)

    # Inicializando o writer do Excel com xlsxwriter
    with pd.ExcelWriter('mercado_livre_products.xlsx', engine='xlsxwriter') as writer:
        # Adicionando o DataFrame ao arquivo Excel
        df.to_excel(writer, index=False, sheet_name='Produtos')

    # Calculando e exibindo as estatísticas, e mostrando o gráfico de caixa
    meanDiscount = df['Percentual de Desconto'].mean()
    medianDiscount = df['Percentual de Desconto'].median()
    stdDevDiscount = df['Percentual de Desconto'].std()

    print(f'Média dos percentuais de desconto: {meanDiscount:.2f}%')
    print(f'Mediana dos percentuais de desconto: {medianDiscount:.2f}%')
    print(f'Desvio Padrão dos percentuais de desconto: {stdDevDiscount:.2f}%')

    modaDiscount = df['Percentual de Desconto'].mode()
    print(f'Desconto mais comum (moda): {modaDiscount.values[0]:.2f}%')

    print('Frequência de marcas em promoção:')
    for brand, count in brandsCounter.items():
        print(f'{brand}: {count}')

    # Plota e exibe o gráfico de caixa
    plt.boxplot(df['Percentual de Desconto'].dropna())
    plt.title('Distribuição dos Descontos')
    plt.ylabel('Percentual de Desconto (%)')

    plt.savefig('discount_boxplot.png')

    plt.show()

# Menu no terminal para o usuário escolher a marca
selectedBrand = getBrandChoice()
startSearch(selectedBrand)
