from django.urls import path

from core.docs_urls import get_docs_urls


urlpatterns = [
    *[path(url, view, name=name) for url, view, name in get_docs_urls('v1')],
]
