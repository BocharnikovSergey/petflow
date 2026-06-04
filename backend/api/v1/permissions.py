from rest_framework.permissions import (
    BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly, IsAuthenticated
)

from .mixins import ClinicAccessMixin
import logging 

logger = logging.getLogger(__name__)


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
        return obj.user == request.user


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


class IsOwnerClinic(BasePermission):
    """Владелец клиники может редкатировать."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user and user.is_authenticated and obj.clinic in user.clinics.all()
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

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user
            and request.user.is_authenticated
            or (
                request.user.is_superuser
                or request.user.roles.first().role in {'admin', 'owner'}
            )
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or (
                user and user.is_authenticated and obj.owner == user
                and self.is_clinic_allowed(user, obj)
            )
        )


class IsOwnerReadOrClinicCreatedVisit(IsAuthenticated):
    """Права доступа для визитов.
    
    Создание и редактирование доступно владельцу клиники,
    а чтение доступно владельцу питомца.
    """
    
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            hasattr(request.user, 'clinics')
            and request.user.clinic
            and request.user.clinic == obj.clinic
        )

class IsOwnerOrClinicCreated(IsAuthenticated):
    """Права доступа для визитов.
    
    Создание и редактирование доступно владельцу клиники,
    а чтение доступно владельцу питомца.
    """
    
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user.is_clinic_member(obj.visit.clinic)
        )


class IsOwnerAndClinicCreateMedCard(BasePermission):
    """
    Права доступа для медецинской карты.
    Владелец и Клиники могут просматривать и редактировать.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.owner == request.user
            or hasattr(request.user, 'clinics')
        )


class IsOwnerClinicAndAdminCreatedVetOrReadOnly(BasePermission):
    """
    Только владелец клиники и супрерпользователь может создавать ветеринаров,
    остальным только чтение
    """

    def has_permission(self, request, view):
        user = request.user
        clinic_id = view.kwargs.get('clinic_id')
        return request.method in SAFE_METHODS or (
            user and user.is_authenticated 
            and user.clinics.filter(id=clinic_id).exists()
        )
    
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.clinic.owner
            or request.user.is_superuser
        )
