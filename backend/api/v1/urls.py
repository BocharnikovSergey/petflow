from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.docs_urls import get_docs_urls
from .users.views import SignUpView, LoginView, UserViewSet
from .pets.views import SpeciesViewSet, BreedViewSet, PetViewSet
from .clinics.views import AddressViewSet, ClinicViewSet
from .reviews.views import ReviewViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users_v1')
router_v1.register('species', SpeciesViewSet, basename='species_v1')
router_v1.register('breeds', BreedViewSet, basename='breeds_v1')
router_v1.register('pets', PetViewSet, basename='pets_v1')
router_v1.register('address', AddressViewSet, basename='address_v1')
router_v1.register('clinics', ClinicViewSet, basename='clinics_v1')
router_v1.register(
    r'clinics/(?P<clinic_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews_v1'
)


urlpatterns = [
    *[path(url, view, name=name) for url, view, name in get_docs_urls('v1')],
    path('auth/signup/', SignUpView.as_view(), name='signup_v1'),
    path('auth/login/', LoginView.as_view(), name='login_v1'),
    path('', include(router_v1.urls)),
]
