MIN_LEN_NAME= 2

IMAGE_FORMAT = {'jpg', 'png', 'jpeg'}
MAX_SIZE_IMAGE_MB = 5 

PATTERN_ADDRESS = r'[0-9A-Za-zА-Яа-я]+'
PATTERN_HOUSE = r'^[0-9А-Яа-яA-Za-z\-/]+$'
PATTERN_CITY_OR_STREET = r'^[A-Za-zА-Яа-я\-\'\s]+$'
LOWERCASE_EXCEPTIONS = {
    'на', 'в', 'под', 'за', 'у', 'и', 'де', 'ла', 'ле', 'да', 'до'
}

PATTERT_DIGITS = r'[^\d+]'
PATTERN_PHONE = r'\+\d{7,15}'