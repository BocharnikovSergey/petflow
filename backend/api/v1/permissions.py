from rest_framework.permissions import (
    BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly
)

from .mixins import ClinicAccessMixin


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает чтение всем пользователям,
    изменение - только администратору или суперпользователю.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in SAFE_METHODS or (
                user and user.is_authenticated and (
                    user.is_superuser or user.has_any_role('admin')
                )
            )
        )

class IsOwnerOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Чтение - доступно всем
    Изменение - только автор объекта
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.user == request.user


class IsOwner(BasePermission):
    """
    Разрешает доступ только владельцу объекта User.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsPetOwnerOrClinicReadOnly(BasePermission):
    """
    Владелец питомца имеет полный доступ.
    Сотрудник клиники имеет read-доступ (если связан через appointments)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            (user and user.is_authenticated and obj.owner == user)
            or (
                request.method in SAFE_METHODS
                and obj.appointments.filter(
                    clinic__user_roles__user=user
                ).exists()
            )
        )

class IsPetOwner(BasePermission):
    """
    Владелец питомца имеет полный доступ.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user and user.is_authenticated and obj.owner == user
  

class IsOwnerOrClinicStaff(BasePermission):
    """
    Пользователь или сотрудник клиники может редактировать запись
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (user and user.is_authenticated) and (
            obj.user == user
            or obj.clinic.user_roles.filter(user=user).exists()
        )
   

class IsClinicMemberOrAdminOrReadOnly(BasePermission, ClinicAccessMixin):
    """
    Персонал клиники или админ может редактировать,
    для всех остальный только чтение. Для слотов
    """

    def has_permission(self, request, view):
        user = request.user
        clinic = view.get_clinic()

        return (
            request.method in SAFE_METHODS
            or (
                user and user.is_authenticated
                and self.is_clinic_allowed(user, clinic)
            )
        )


class IsClinicStaffOrAdminOrReadOnly(BasePermission, ClinicAccessMixin):
    """
    Персонал клиники или админ может редактировать,
    для всех остальный только чтение. Для клиники.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or (
                user and user.is_authenticated
                and self.is_clinic_allowed(user, obj)
            )
        )
