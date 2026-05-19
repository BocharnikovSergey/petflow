from django.contrib import admin

from .models import Appointment, Slot
from .utils import constants


class SlotEditClinicRolesMixin:
    """
    Миксин для фильтрации объектов
    в админ-панели по правам на редактирование слотов.
    """

    def get_queryset(self, request):
        """Возвращает отфильтрованный queryset с учётом прав пользователя."""
        qs = super().get_queryset(request)

        return qs if request.user.is_superuser else qs.filter(
            clinic__user_roles__user=request.user,
            clinic__user_roles__role__name__in=constants.SLOT_EDIT_ROLES
        ).distinct()


@admin.register(Slot)
class SlotAdmin(SlotEditClinicRolesMixin, admin.ModelAdmin):
    """
    Админ-панель для управления временными слотами записи.

    Доступ ограничен сотрудниками клиник.
    """

    list_display = ('id', 'clinic', 'start_time', 'end_time')
    list_display_links = ('id', 'clinic')
    list_filter = ('clinic',)
    search_fields = ('clinic__name',)
    autocomplete_fields = ('clinic',)
    list_select_related = ('clinic',)


@admin.register(Appointment)
class AppointmentAdmin(SlotEditClinicRolesMixin, admin.ModelAdmin):
    """
    Админ-панель для управления записями на приём.

    Доступ ограничен сотрудниками клиник.
    """

    list_display = ('id', 'user', 'pet', 'clinic', 'date', 'slot', 'status')
    list_display_links = ('id', 'user')
    list_filter = ('status', 'clinic', 'date')
    search_fields = ('user__full_name', 'clinic__name')
    autocomplete_fields = ('user', 'pet', 'clinic', 'slot')
    list_select_related = ('user', 'clinic')
