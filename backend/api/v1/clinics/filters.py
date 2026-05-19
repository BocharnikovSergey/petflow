import django_filters

from clinics.models import Clinic


class ClinicFilter(django_filters.FilterSet):
    """Фильтр для поиска и сортировки ветеринарных клиник."""

    city = django_filters.CharFilter(
        field_name='address__city',
        lookup_expr='icontains'
    )
    street = django_filters.CharFilter(
        field_name='address__street',
        lookup_expr='icontains'
    )
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    min_rating = django_filters.NumberFilter(
        field_name='avg_rating',
        lookup_expr='gte'
    )

    max_rating = django_filters.NumberFilter(
        field_name='avg_rating',
        lookup_expr='lte'
    )
    species = django_filters.NumberFilter(field_name='species__id')

    class Meta:
        model = Clinic
        fields = (
            'city', 'street', 'name', 'min_rating', 'max_rating', 'species'
        )
