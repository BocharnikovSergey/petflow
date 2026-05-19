from functools import wraps


def log_function_call(logger):
    """
    Декоратор для логирования вызова, успешного завершения и исключений функции.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f'Вызов функции: {func.__name__}.')
            try:
                result = func(*args, **kwargs)
                logger.debug(f'Функция {func.__name__} завершена.')
                return result
            except Exception as error:
                logger.error(
                    f'Функция {func.__name__} выбросило исключение: {error}'
                )
                raise
        return wrapper
    return decorator