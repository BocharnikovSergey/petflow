from django.contrib import admin

from .models import Breed, Species, Pet


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    """Админ-панель для управления видами животных."""

    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    """Админ-панель для управления породами животных."""

    list_display = ('id', 'name', 'species')
    list_display_links = ('id', 'name')
    list_filter = ('species',)
    search_fields = ('name',)
    autocomplete_fields = ('species',)


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """Админ-панель для управления питомцами пользователей."""

    list_display = ('id', 'name', 'owner', 'species', 'breed')
    list_display_links = ('id', 'name')
    list_filter = ('species', 'breed')
    search_fields = ('name', 'owner__full_name')
    autocomplete_fields = ('owner', 'species', 'breed')
    list_select_related = ('owner',)
