MIN_LEN_NAME= 2

ERROR_INVALID_NAME = 'Введите корректное значение'

IMAGE_FORMAT = {'jpg', 'png', 'jpeg'}
MAX_SIZE_IMAGE_MB = 5 


PATTERN_HOUSE = r'^[0-9А-Яа-яA-Za-z\-/]+$'
PATTERN_CITY_OR_STREET = r'^[A-Za-zА-Яа-я\-\'\s]+$'
LOWERCASE_EXCEPTIONS = {
    'на', 'в', 'под', 'за', 'у', 'и', 'де', 'ла', 'ле', 'да', 'до'
}

PATTERN_PHONE = r'^\+?\d[\d\s\-\(\)]{8,20}\d$'