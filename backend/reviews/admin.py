from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ-панель для управления отзывами о клиниках."""

    list_display = ('id', 'author', 'clinic', 'score')
    list_display_links = ('id', 'author')
    list_filter = ('score', 'clinic')
    search_fields = ('aunthor__full_name', 'clinic__name',)
    autocomplete_fields = ('author', 'clinic')
    list_select_related = ('author', 'clinic')
