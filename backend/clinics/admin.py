from django.contrib import admin

from .models import Address, Clinic
from .utils import constants


class ClinicEditRolesMixin:
    """
    Миксин для фильтрации объектов
    в админ-панели по права на редактирование клиники.
    """

    def get_queryset(self, request):
        """Возвращает отфильтрованный queryset с учётом прав пользователя."""
        qs = super().get_queryset(request)

        return qs if request.user.is_superuser else qs.filter(
            user_roles__user=request.user,
            user_roles__role__name__in=constants.CLINIC_EDIT_ROLES
        ).distinct()



@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Админ-панель для управления адресами клиник."""

    list_display = ('id', 'full_address')
    list_display_links = ('id', 'full_address')
    list_filter = ('city',)
    search_fields = ('city', 'street', 'house')


@admin.register(Clinic)
class ClinicAdmin(ClinicEditRolesMixin, admin.ModelAdmin):
    """
    Админ-панель для управления ветеринарными клиниками.

    Доступ к данным может быть ограничен
    по принадлежности пользователя к клинике.
    """

    list_display = ('id', 'name', 'address', 'email', 'phone')
    list_display_links = ('id', 'name')
    list_filter = ('address__city', 'name')
    search_fields = ('name', 'address')
    autocomplete_fields = ('address',)
    list_select_related = ('address',)

    def get_queryset(self, request):
        """Возвращает отфильтрованный queryset с учётом прав пользователя."""
        qs = super().get_queryset(request)

        return qs if request.user.is_superuser else qs.filter(
            user_roles__user=request.user,
            user_roles__role__name__in=constants.CLINIC_EDIT_ROLES
        ).distinct()
