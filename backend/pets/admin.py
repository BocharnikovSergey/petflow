from django.contrib import admin

from .models import (
    Breed, Species, Pet, MedicalCard, Vaccination, ChronicCondition
)


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


class ChronicConditionInline(admin.TabularInline):
    model = ChronicCondition
    extra = 1
    fields = ('name', 'status', 'description')
    show_change_link = True


class VaccinationInline(admin.TabularInline):
    model = Vaccination
    extra = 1
    fields = ('name', 'vaccinated_at', 'expires_at', 'visit', 'notes')
    show_change_link = True


@admin.register(MedicalCard)
class MedicalCardAdmin(admin.ModelAdmin):
    """Админ-панель для управления мед.книжкой питомца."""

    list_display = ('id', 'pet', 'notes_short')
    list_display_links = ('id', 'pet')
    search_fields = ('pet__name', 'pet__owner__full_name', 'notes', 'allergies')
    list_filter = ('pet__species',)
    inlines = [ChronicConditionInline, VaccinationInline]

    def notes_short(self, obj):
        return obj.notes[:20] + '...' if len(obj.notes) > 20 else obj.notes
    
    notes_short.short_description = 'Заметки'


@admin.register(ChronicCondition)
class ChronicConditionAdmin(admin.ModelAdmin):
    """Админ-панель для управления заболеваниями."""

    list_display = ('id', 'name', 'medical_card', 'status')
    list_display_links = ('id', 'name')
    list_filter = ('status',)
    search_fields = ('name', 'description', 'medical_card__pet__name')


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    """Админ-панель для управления вакцинациями."""

    list_display = (
        'id', 'medical_card', 'name', 'vaccinated_at', 'expires_at', 'visit'
    )
    list_filter = ('vaccinated_at', 'expires_at')
    search_fields = ('name', 'medical_card__pet__name', 'notes')
    date_hierarchy = 'vaccinated_at'
