from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from core.docs_urls import get_docs_urls
from .users.views import SignUpView, LoginView, UserViewSet
from .pets.views import (
    SpeciesViewSet, BreedViewSet, PetViewSet, ChronicConditionViewSet,
    VaccinationViewSet
)
from .clinics.views import AddressViewSet, ClinicViewSet, VisitViewSet
from .reviews.views import ReviewViewSet
from .appointments.views import (
    SlotViewSet, ClinicAppointmentViewSet, MeAppointmentViewSet
)
from .notifications.views import SaveFCMTokenView, NotificationSettingsView

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
router_v1.register(
    r'clinics/(?P<clinic_id>\d+)/slots',
    SlotViewSet, basename='slots_v1'
)
router_v1.register(
    r'clinics/(?P<clinic_id>\d+)/appointments',
    ClinicAppointmentViewSet,
    basename='clinic_appointment_v1'
)
router_v1.register(
    r'users/me/appointments', MeAppointmentViewSet, basename='me_appointment_v1'
)

pets_router_v1 = NestedDefaultRouter(router_v1, r'pets', lookup='pet')
pets_router_v1.register(r'visits', VisitViewSet, basename='pet-visits')
pets_router_v1.register(
    r'conditions', ChronicConditionViewSet, basename='pet-conditions'
)
pets_router_v1.register(
    r'vaccinations', VaccinationViewSet, basename='pet-vaccinations'
)


urlpatterns = [
    *[path(url, view, name=name) for url, view, name in get_docs_urls('v1')],
    path('auth/signup/', SignUpView.as_view(), name='signup_v1'),
    path('auth/login/', LoginView.as_view(), name='login_v1'),
    path('fcm-token/', SaveFCMTokenView.as_view(), name='fcm_token_v1'),
    path(
        'notification_settings/',
        NotificationSettingsView.as_view(),
        name='notification_settings_v1'
    ),
    path('', include(router_v1.urls)),
    path('', include(pets_router_v1.urls)),
]
