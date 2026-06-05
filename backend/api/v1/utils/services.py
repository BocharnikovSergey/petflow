import re
import requests
import logging

from django.conf import settings

from .. import constants


logger = logging.getLogger(__name__)


def capitalize_match(match):
        """Преобразует слово в нужный регистр."""
        word = match.group(0)
        if word.lower() in constants.LOWERCASE_EXCEPTIONS:
            return word.lower()
        return word.capitalize()

def normalize_address(value):
    """Нормализует адрес."""
    return re.sub(constants.PATTERN_ADDRESS, capitalize_match, value)


def get_coordinates(address_str):
        """Получает координаты через Яндекс Геокодер."""
        api_key = settings.YANDEX_GEOCODER_API_KEY
        url = 'https://geocode-maps.yandex.ru/1.x/'
        if not api_key:
            logger.error('Нет ключа API для геокодирования.')
            return None
        try:
            response = requests.get(
                url,
                params={
                    'apikey': api_key,
                    'geocode': address_str,
                    'format': 'json'
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            pos = data['response']['GeoObjectCollection']['featureMember'][0][
                'GeoObject'
            ]['Point']['pos']
            lon, lat = map(float, pos.split())
            return {'latitude': lat, 'longitude': lon}
        except (
            KeyError, IndexError, ValueError, requests.RequestException
        ) as e:
            logger.error(f'Ошибка геокодирования для адреса {address_str}: {e}')
            return None
