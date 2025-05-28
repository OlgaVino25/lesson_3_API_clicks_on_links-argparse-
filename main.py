import argparse
import requests
import os
from dotenv import load_dotenv

VERSION = '5.199'
API_URL = 'https://api.vk.ru/method/utils.getShortLink'
VK_STATS_URL = 'https://api.vk.ru/method/utils.getLinkStats'


def shorten_url(url, token):
    """Сокращает URL-адрес с помощью VK API.
    
    Args:
        url (str): Исходный URL-адрес для сокращения
        token (str): Токен доступа VK API

    Returns:
        str: Сокращенный URL-адрес

    Raises:
        requests.exceptions.HTTPError: Если произошла ошибка при запросе к API.
    """
    payload = {
        'access_token': token,
        'v': VERSION,
        'url': url,
        'private': 0,
    }
    response = requests.get(API_URL, params=payload)
    response.raise_for_status()
    return response.json()['response']['short_url']


def count_clicks(short_url, token):
    """Возвращает количество переходов по сокращенной ссылке.
    
    Args:
        short_url (str): Сокращенный URL-адрес (полученный от VK API)
        token (str): Токен доступа VK API

    Returns:
        int: Количество переходов по ссылке

    Raises:
        requests.exceptions.HTTPError: Если произошла ошибка при запросе к API.
    """
    key = short_url.split('/')[-1]
    payload = {
        'access_token': token,
        'v': VERSION,
        'key': key,
        'interval': 'forever'
    }
    response = requests.get(VK_STATS_URL, params=payload)
    response.raise_for_status()
    return response.json()['response']['stats'][0]['views']


def is_shorten_link(url, token):
    """Проверяет, является ли ссылка сокращенной через VK API.
    
    Args:
        url (str): URL-адрес для проверки
        token (str): Токен доступа VK API

    Returns:
        bool: True если ссылка является сокращенной через VK, False в противном случае

    Raises:
        requests.exceptions.HTTPError: Если произошла ошибка при запросе к API.
    """
    key = url.split('/')[-1]
    payload = {
        'access_token': token,
        'v': VERSION,
        'key': key,
        'interval': 'forever'
    }
    response = requests.get(VK_STATS_URL, params=payload)
    response.raise_for_status()
    return 'error' not in response.json()


def main():
    load_dotenv()
    token = os.environ['VK_API_TOKEN']
    parser = argparse.ArgumentParser(description='Программа для сокращения ссылок и проверки кликов')
    parser.add_argument ('url', nargs='?', help='Введите ссылку')
    args = parser.parse_args()
    try:
        user_url = args.url
        if is_shorten_link(user_url, token):
            clicks_count = count_clicks(user_url, token)
            print('Количество кликов: ', clicks_count)
        else:
            short_url = shorten_url(user_url, token)
            print('Сокращенная ссылка: ', short_url)
    except requests.exceptions.HTTPError as e:
        print(f'Ошибка при работе с API: {e}')
    except KeyError as e:
        print(f'Ключ сопоставления не найден: {e}')
    except ValueError as e:
        print(f'Ошибка значения: {e}')

if __name__ == "__main__":
    main()