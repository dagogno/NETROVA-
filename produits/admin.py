from django.contrib import admin
from .models import Pack, Composant


class ComposantInline(admin.TabularInline):
    model  = Composant
    extra  = 3
    fields = ['nom', 'emoji', 'ordre', 'actif']


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display  = ['code', 'nom', 'prix_formate', 'couleur', 'disponible', 'ordre']
    list_editable = ['disponible', 'ordre']
    list_filter   = ['disponible', 'couleur']
    inlines       = [ComposantInline]

    def prix_formate(self, obj):
        return f"{obj.prix_formate} FCFA"
    prix_formate.short_description = 'Prix'


@admin.register(Composant)
class ComposantAdmin(admin.ModelAdmin):
    list_display = ['pack', 'nom', 'emoji', 'ordre', 'actif']
    list_filter  = ['pack', 'actif']
