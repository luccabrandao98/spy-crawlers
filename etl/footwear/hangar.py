import pandas as pd
import requests
from datetime import date
from bs4 import BeautifulSoup
import os
from etl.database.db_connection import AWSDatabase


def get_categories_dict(main_url):
    # Listando as categorias
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    categories_class = soup.find(class_='categories-list')
    categories_list = categories_class.find('ul')
    categories_elements = categories_list.find_all('a')

    # Criando dicionário de categorias
    categories_dict = {}
    for element in categories_elements:
        category_name = element.get_text(strip=True)
        category_href = element.get('href')

        categories_dict[category_name] = category_href
    
    return categories_dict

def get_product_data(main_url):
    categories = get_categories_dict(main_url)
    product_dict_list = []

    for category in categories:
        print('Categoria:', category)
        page_number = 1

        while True:
            print('Página:', page_number)
            response = requests.get(main_url+categories[category]+f'&page={page_number}')
            print('Status code:', response.status_code)
            print('------------------')
            soup = BeautifulSoup(response.text, 'html.parser')

            products_list = soup.find_all(class_='holder-info')

            for product in products_list:
                name = product.find(class_='product-name').get_text(strip=True)
                
                product_prices = product.find(class_='product-prices')
                old_price = float(
                    product_prices
                    .find(class_='product-old-price')
                    .get_text(strip=True)
                    .replace('R$ ', '')
                    .replace(',', '.')
                    )
                
                price = float(
                    product_prices
                    .find(class_='product-actual-price')
                    .get_text(strip=True)
                    .replace('R$ ', '')
                    .replace(',', '.')
                    )
                
                product_dict = {
                    'created_at': date.today()
                    , 'product': name
                    , 'store_name': 'Hangar Outlet'
                    , 'price': price
                    , 'total_discount': old_price - price
                    , 'percentage_discount': (old_price - price)/old_price
                }
                
                product_dict_list.append(product_dict)
            
            # Cada página apresenta 36 produtos, menos que isso é a última página
            if len(products_list) == 36:
                page_number = page_number + 1
            else:
                break

    return product_dict_list

if __name__ == '__main__':
    
    username = os.environ['AWS_RDS_USER']
    password = os.environ['AWS_RDS_KEY']
    database = 'spy'
    host = os.environ['AWS_RDS_HOST']

    db = AWSDatabase(username=username, password=password, database=database, host=host)
    # connection = db.connection()

    data = [{'id': 1, 'test': 'A'}, {'id': 2, 'test': 'B'}]

    db.insert(table_name='test', data=data)

    # query = 'select * from test'
    # df = pd.read_sql(query, con=connection)
    # print(df)
    # df = get_product_data(main_url='https://www.outlethangar.com.br')
    