import re

from .. import constants

def capitalize_match(match):
        """Преобразует слово в нужный регистр."""
        word = match.group(0)
        if word.lower() in constants.LOWERCASE_EXCEPTIONS:
            return word.lower()
        return word.capitalize()

def normalize_address(value):
    """Нормализует адрес."""
    return re.sub(constants.PATTERN_ADDRESS, capitalize_match, value)
