from django.contrib import admin
from django.utils.html import format_html
from .models import CategoriePartenaire, Partenaire, ProduitPartenaire


class ProduitInline(admin.TabularInline):
    model  = ProduitPartenaire
    extra  = 2
    fields = ['nom', 'prix', 'description', 'image', 'disponible', 'ordre']


@admin.register(CategoriePartenaire)
class CategorieAdmin(admin.ModelAdmin):
    list_display  = ['emoji', 'nom', 'slug', 'ordre']
    list_editable = ['ordre']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display  = ['logo_mini', 'nom', 'categorie', 'zone', 'plan_badge',
                     'statut_badge', 'date_debut', 'ordre_affichage']
    list_editable = ['ordre_affichage']
    list_filter   = ['statut', 'plan', 'categorie']
    search_fields = ['nom', 'telephone', 'zone']
    readonly_fields = ['logo_mini']
    inlines = [ProduitInline]

    fieldsets = (
        ('Identité', {'fields': ('nom', 'slogan', 'description', 'categorie',
                                  'logo', 'logo_mini', 'image_couverture')}),
        ('Contact', {'fields': ('telephone', 'whatsapp', 'email', 'site_web', 'zone', 'adresse')}),
        ('Partenariat', {'fields': ('statut', 'plan', 'date_debut', 'date_fin', 'note_admin')}),
        ('Affichage', {'fields': ('ordre_affichage',)}),
    )

    def logo_mini(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;border-radius:6px"/>', obj.logo.url)
        return '—'
    logo_mini.short_description = 'Logo'

    def plan_badge(self, obj):
        colors = {'starter': '#1A4DB5', 'standard': '#16914E', 'premium': '#E8A12B'}
        c = colors.get(obj.plan, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_plan_display().split('—')[0].strip())
    plan_badge.short_description = 'Plan'

    def statut_badge(self, obj):
        colors = {'actif': '#16914E', 'inactif': '#888', 'en_attente': '#E8A12B'}
        c = colors.get(obj.statut, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_statut_display())
    statut_badge.short_description = 'Statut'


@admin.register(ProduitPartenaire)
class ProduitPartenaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'partenaire', 'prix', 'disponible']
    list_filter  = ['disponible', 'partenaire']
