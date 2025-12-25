from django.contrib import admin
from api.crimes.models import CrimeCategory, SectorCrimeStat

@admin.register(CrimeCategory)
class CrimeCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(SectorCrimeStat)
class SectorCrimeStatAdmin(admin.ModelAdmin):
    list_display = ('sector', 'category', 'count')
    list_filter = ('category', 'sector')