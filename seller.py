import io
import logging.config
import os
import re
import zipfile
from environs import Env

import pandas as pd
import requests

logger = logging.getLogger(__file__)


def get_product_list(last_id, client_id, seller_token):
    """
    Получить список товаров из магазина Ozon.

    Аргументы:
        last_id (str): Идентификатор последнего полученного товара (пагинация).
        client_id (str): Идентификатор клиента для доступа к API Ozon.
        seller_token (str): Токен продавца для аутентификации.

    Возвращает:
        dict: Словарь, содержащий список товаров, полученных из магазина Ozon.

    Исключения:
        requests.HTTPError: Если запрос к API Ozon завершается ошибкой.

    Пример:
        >>> get_product_list("12345", "ваш_client_id", "ваш_токен_продавца")
        {'result': {...}}

    """
    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {
        "filter": {
            "visibility": "ALL",
        },
        "last_id": last_id,
        "limit": 1000,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def get_offer_ids(client_id, seller_token):
    """
    Получить идентификаторы предложений товаров из магазина Ozon.

    Аргументы:
        client_id (str): Идентификатор клиента для доступа к API Ozon.
        seller_token (str): Токен продавца для аутентификации.

    Возвращает:
        list: Список идентификаторов предложений товаров в магазине Ozon.

    Исключения:
        requests.HTTPError: Если запрос к API Ozon завершается ошибкой.

    Пример:
        >>> get_offer_ids("ваш_client_id", "ваш_токен_продавца")
        ['12345', '67890', ...]

    """
    last_id = ""
    product_list = []
    while True:
        some_prod = get_product_list(last_id, client_id, seller_token)
        product_list.extend(some_prod.get("items"))
        total = some_prod.get("total")
        last_id = some_prod.get("last_id")
        if total == len(product_list):
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer_id"))
    return offer_ids


def update_price(prices: list, client_id, seller_token):
    """
    Обновить цены товаров в магазине Ozon.

    Аргументы:
        prices (list): Список словарей, содержащих информацию об обновлении цен.
        client_id (str): Идентификатор клиента для доступа к API Ozon.
        seller_token (str): Токен продавца для аутентификации.

    Возвращает:
        dict: Словарь, содержащий ответ от API Ozon после обновления цен.

    Исключения:
        requests.HTTPError: Если запрос к API Ozon завершается ошибкой.

    Пример:
        >>> update_price(prices=[{"offer_id": "12345", "price": "5990"}], client_id="ваш_client_id", seller_token="ваш_токен_продавца")
        {'status': 'success'}

    """
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"prices": prices}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_stocks(stocks: list, client_id, seller_token):
    """
    Обновить остатки товаров в магазине Ozon.

    Аргументы:
        stocks (list): Список словарей, содержащих информацию об обновлении остатков.
        client_id (str): Идентификатор клиента для доступа к API Ozon.
        seller_token (str): Токен продавца для аутентификации.

    Возвращает:
        dict: Словарь, содержащий ответ от API Ozon после обновления остатков.

    Исключения:
        requests.HTTPError: Если запрос к API Ozon завершается ошибкой.

    Пример:
        >>> update_stocks(stocks=[{"offer_id": "12345", "stock": 100}], client_id="ваш_client_id", seller_token="ваш_токен_продавца")
        {'status': 'success'}

    """
    url = "https://api-seller.ozon.ru/v1/product/import/stocks"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"stocks": stocks}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def download_stock():
    """
    Скачать файл с остатками с веб-сайта Casio и преобразовать его в список словарей.

    Возвращает:
        list: Список словарей, содержащих информацию об остатках часов.

    Пример:
        >>> download_stock()
        [{'Код': '12345', 'Количество': '5', 'Цена': '5990.00 руб.'}, ...]

    """
    # Скачать остатки с сайта
    casio_url = "https://timeworld.ru/upload/files/ostatki.zip"
    session = requests.Session()
    response = session.get(casio_url)
    response.raise_for_status()
    with response, zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(".")
    # Создаем список остатков часов:
    excel_file = "ostatki.xls"
    watch_remnants = pd.read_excel(
        io=excel_file,
        na_values=None,
        keep_default_na=False,
        header=17,
    ).to_dict(orient="records")
    os.remove("./ostatki.xls")  # Удалить файл
    return watch_remnants


def create_stocks(watch_remnants, offer_ids):
    """
        Создать список обновлений остатков товаров в магазине Ozon.

        Аргументы:
            watch_remnants (list): Список словарей, содержащих информацию об остатках часов.
            offer_ids (list): Список идентификаторов предложений товаров в магазине Ozon.

        Возвращает:
            list: Список словарей, содержащих информацию об обновлении остатков.

        Пример:
            >>> create_stocks(watch_remnants=[{'Код': '12345', 'Количество': '5'}], offer_ids=['12345', '67890'])
            [{'offer_id': '12345', 'stock': 5}, ...]

        """
    stocks = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append({"offer_id": str(watch.get("Код")), "stock": stock})
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append({"offer_id": offer_id, "stock": 0})
    return stocks


def create_prices(watch_remnants, offer_ids):
    """
        Создать список обновлений цен товаров в магазине Ozon.

        Аргументы:
            watch_remnants (list): Список словарей, содержащих информацию о ценах на часы.
            offer_ids (list): Список идентификаторов предложений товаров в магазине Ozon.

        Возвращает:
            list: Список словарей, содержащих информацию об обновлении цен.

        Пример:
            >>> create_prices(watch_remnants=[{'Код': '12345', 'Цена': '5990.00 руб.'}], offer_ids=['12345', '67890'])
            [{'auto_action_enabled': 'UNKNOWN', 'currency_code': 'RUB', 'offer_id': '12345', 'old_price': '0', 'price': '5990'}, ...]

        """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": str(watch.get("Код")),
                "old_price": "0",
                "price": price_conversion(watch.get("Цена")),
            }
            prices.append(price)
    return prices


def price_conversion(price: str) -> str:
    """
        Преобразовать цену из формата '5'990.00 руб.' в формат '5990'.

        Аргументы:
            price (str): Строка с ценой в формате '5'990.00 руб.'.

        Возвращает:
            str: Строка с преобразованной ценой в формате '5990'.

        Пример:
            >>> price_conversion('5'990.00 руб.')
            '5990'

        """
    return re.sub("[^0-9]", "", price.split(".")[0])


def divide(lst: list, n: int):
    """
    Разделить список на части по заданному размеру.

    Аргументы:
        lst (list): Исходный список.
        n (int): Размер части списка.

    Возвращает:
        generator: Генератор, возвращающий части списка.

    Пример:
        >>> list(divide([1, 2, 3, 4, 5, 6], 2))
        [[1, 2], [3, 4], [5, 6]]

    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def upload_prices(watch_remnants, client_id, seller_token):
    """
        Выполнить загрузку обновлений цен товаров.

        Аргументы:
            watch_remnants (list): Список словарей с информацией о товарах.
            client_id (str): Идентификатор клиента.
            seller_token (str): Токен продавца.

        Возвращает:
            list: Список словарей с информацией об обновлении цен.

        Пример:
            >>> upload_prices([{}], "client_id", "seller_token")
            [{'auto_action_enabled': 'UNKNOWN', 'currency_code': 'RUB', 'offer_id': '12345', 'old_price': '0', 'price': '5990'}]

        """
    offer_ids = get_offer_ids(client_id, seller_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_price in list(divide(prices, 1000)):
        update_price(some_price, client_id, seller_token)
    return prices


async def upload_stocks(watch_remnants, client_id, seller_token):
    """
        Выполнить загрузку обновлений остатков товаров.

        Аргументы:
            watch_remnants (list): Список словарей с информацией о товарах.
            client_id (str): Идентификатор клиента.
            seller_token (str): Токен продавца.

        Возвращает:
            tuple: Кортеж с двумя списками словарей: список непустых остатков и общий список обновлений остатков.

        Пример:
            >>> upload_stocks([{}], "client_id", "seller_token")
            ([{'sku': '12345', 'stock': 0}], [{'sku': '12345', 'stock': 0}])

        """
    offer_ids = get_offer_ids(client_id, seller_token)
    stocks = create_stocks(watch_remnants, offer_ids)
    for some_stock in list(divide(stocks, 100)):
        update_stocks(some_stock, client_id, seller_token)
    not_empty = list(filter(lambda stock: (stock.get("stock") != 0), stocks))
    return not_empty, stocks


def main():
    """
        Основная функция для выполнения процесса обновления цен и остатков товаров в магазине Ozon.
    """
    env = Env()
    seller_token = env.str("SELLER_TOKEN")
    client_id = env.str("CLIENT_ID")
    try:
        offer_ids = get_offer_ids(client_id, seller_token)
        watch_remnants = download_stock()
        # Обновить остатки
        stocks = create_stocks(watch_remnants, offer_ids)
        for some_stock in list(divide(stocks, 100)):
            update_stocks(some_stock, client_id, seller_token)
        # Поменять цены
        prices = create_prices(watch_remnants, offer_ids)
        for some_price in list(divide(prices, 900)):
            update_price(some_price, client_id, seller_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
