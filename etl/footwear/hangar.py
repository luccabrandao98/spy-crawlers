import pandas as pd
import requests
from datetime import date
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from etl.database.db_connection import AWSDatabase

def get_categories_dict(main_url):
    # Listando as categorias
    response = requests.get(main_url)
    if response.status_code != 200:
        raise Exception('Status code != 200')

    soup = BeautifulSoup(response.text, 'html.parser')

    categories_class = soup.find(class_='categories-list')
    categories_list = categories_class.find('ul')
    categories_elements = categories_list.find_all('a')

    # Criando dicionário de categorias
    categories_dict = {}
    for element in tqdm(categories_elements):
        category_name = element.get_text(strip=True)
        category_href = element.get('href')

        categories_dict[category_name] = category_href
    
    return categories_dict

def get_product_data(main_url):
    categories = get_categories_dict(main_url)
    product_dict_list = []

    for category in tqdm(categories):
        page_number = 1

        while True:
            response = requests.get(main_url+categories[category]+f'&page={page_number}')
            
            if response.status_code != 200:
                raise Exception('Status code != 200')

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
    connection = db.connection()

    df = pd.DataFrame(get_product_data(main_url='https://www.outlethangar.com.br'), index=None)

    # Insert no banco
    df.to_sql(
        'hangar',
        schema='footwear',
        con=connection,
        if_exists='append',
        index=None
    )