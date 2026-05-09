from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
)


def get_docs_urls(schema_name: str):
    return [
        ('schema/', SpectacularAPIView.as_view(), f'{schema_name}-schema'),
        (
            'swagger/',
            SpectacularSwaggerView.as_view(url_name=f'{schema_name}-schema'),
            f'{schema_name}-swagger'
        ),
        (
            'redoc/',
            SpectacularRedocView.as_view(url_name=f'{schema_name}-schema'),
            f'{schema_name}-redoc'
        ),
    ]
