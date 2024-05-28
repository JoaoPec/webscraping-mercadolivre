from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt

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

# Função para extrair produtos da página HTML
def extractProducts(soup, brand):
    products = []

    itemsContainer = soup.find('ol', class_='items_container')

    if itemsContainer:
        for item in itemsContainer.find_all('li', class_='promotion-item'):
            nameTag = item.find('p', class_='promotion-item__title')
            if nameTag:
                name = nameTag.text.strip()
            else:
                continue

            # Verifica se o produto pertence à marca escolhida
            if brand != "Todas" and brand not in name:
                continue

            spanDiscountPrice = item.find('s', class_='andes-money-amount andes-money-amount-combo__previous-value andes-money-amount--previous andes-money-amount--cents-superscript')
            if spanDiscountPrice:
                discountPriceText = spanDiscountPrice.text.replace('R$', '').strip()
                try:
                    discountPrice = float(discountPriceText.replace('.', '').replace(',', '.').strip())
                    print(f'Preço com desconto encontrado para o produto "{name}": R${discountPrice:.2f}')
                except ValueError:
                    discountPrice = None
                    print(f'Erro ao converter o preço com desconto para o produto "{name}": {discountPriceText}')
            else:
                discountPrice = None
                print(f'Preço com desconto não encontrado para o produto "{name}"')

            spanOriginalPrice = item.find('span', class_='andes-money-amount__fraction')
            if spanOriginalPrice:
                originalPriceText = spanOriginalPrice.text.replace('R$', '').strip()
                try:
                    originalPrice = float(originalPriceText.replace('.', '').replace(',', '.').strip())
                    print(f'Preço original encontrado para o produto "{name}": R${originalPrice:.2f}')
                except ValueError:
                    originalPrice = None
                    print(f'Erro ao converter o preço original para o produto "{name}": {originalPriceText}')
            else:
                originalPrice = None
                print(f'Preço original não encontrado para o produto "{name}"')

            if originalPrice and discountPrice:
                discountPercentage = round((originalPrice - discountPrice) / originalPrice * 100, 2)
                products.append({
                    'Name': name,
                    'Original Price': originalPrice,
                    'Discount Price': discountPrice,
                    'Discount Percentage': discountPercentage
                })
    return products

# Função para iniciar a busca e gerar relatórios
def startSearch(brand):
    urlPage1 = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779535-1&domain_id=MLB-CELLPHONES'
    urlPage2 = 'https://www.mercadolivre.com.br/ofertas?container_id=MLB779535-1&domain_id=MLB-CELLPHONES&page=2'
    headers = {"User-Agent": "Mozilla/5.0"}

    responsePage1 = requests.get(urlPage1, headers=headers)
    soupPage1 = BeautifulSoup(responsePage1.text, 'html.parser')
    productsPage1 = extractProducts(soupPage1, brand)

    responsePage2 = requests.get(urlPage2, headers=headers)
    soupPage2 = BeautifulSoup(responsePage2.text, 'html.parser')
    productsPage2 = extractProducts(soupPage2, brand)

    products = productsPage1 + productsPage2

    df = pd.DataFrame(products)

    df = df.sort_values(by='Name')

    df.to_csv('mercado_livre_products.csv', index=False)

    with pd.ExcelWriter('mercado_livre_products.xlsx') as writer:
        df.to_excel(writer, index=False, sheet_name='Products')

    mean = df['Discount Percentage'].mean()
    median = df['Discount Percentage'].median()
    stdDev = df['Discount Percentage'].std()

    print(f'Média: {mean:.2f}%')
    print(f'Mediana: {median:.2f}%')
    print(f'Desvio Padrão: {stdDev:.2f}%')

    plt.boxplot(df['Discount Percentage'])
    plt.title('Distribuição dos Descontos')
    plt.ylabel('Percentual de Desconto')

    plt.savefig('discount_boxplot.png')

    plt.show()

# Menu no terminal para o usuário escolher a marca
selectedBrand = getBrandChoice()
startSearch(selectedBrand)
