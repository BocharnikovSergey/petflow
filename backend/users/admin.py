from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ProjectUser, Role, UserRole, VetProfile
from clinics.models import Clinic
from .utils import constants


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    autocomplete_fields = ('role', 'clinic')


@admin.register(ProjectUser)
class ProjectUserAdmin(UserAdmin):
    """Админ-панель для пользователей системы."""

    inlines = (UserRoleInline,)

    list_display = ('id', 'email', 'full_name', 'phone')
    list_display_links = ('id', 'email', 'full_name')
    list_filter = ('is_active',)
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Личная информация', {
            'fields': (
                'first_name',
                'last_name',
                'phone',
                'bio',
                'avatar',
            )
        }),

        ('Даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Админ-панель для ролей пользователей"""

    list_display = ('id', 'name', 'short_description')
    list_display_links = ('id', 'name')
    search_fields = ('name',)

    def short_description(self, obj):
        return (
            '...' 
            if not obj.description
            else obj.description[:constants.LEN_SHORT_DESC]
            + '...' * (len(obj.description) > constants.LEN_SHORT_DESC)
        )

    short_description.short_description = (
        f'Описание ({constants.LEN_SHORT_DESC} символов)'
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Админ-панель для назначения ролей пользователям в рамках клиники."""

    list_display = ('id', 'user', 'role', 'clinic')
    list_display_links = ('id', 'user', 'role')
    list_filter = ('role', 'clinic')
    search_fields = ('user__email', 'user__fullname', 'clinic__name')
    autocomplete_fields = ('user', 'role', 'clinic')
    list_select_related = ('user', 'clinic')



@admin.register(VetProfile)
class DoctorAdmin(admin.ModelAdmin):
    """Админ-панель для ветеринаров"""

    list_display = (
        'id', 'first_name', 'last_name', 'specialization', 'clinic'
    )
    search_fields = ('first_name', 'last_name', 'specialization',) 
    list_filter = ( 'clinic', 'is_active')
