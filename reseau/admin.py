from django.contrib import admin
from django.utils.html import format_html
from .models import Commission


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display  = ['membre_nom', 'commande_ref', 'taux_pct', 'montant_fmt',
                     'statut_badge', 'date_calcul', 'date_versement']
    list_filter   = ['statut', 'date_calcul']
    search_fields = ['membre__user__last_name', 'membre__user__first_name',
                     'commande__pk']
    readonly_fields = ['membre', 'commande', 'taux', 'montant', 'date_calcul']
    actions = ['marquer_versees']

    def membre_nom(self, obj):
        return obj.membre.nom_complet
    membre_nom.short_description = 'Membre'

    def commande_ref(self, obj):
        return f"CMD-{obj.commande.pk:04d}"
    commande_ref.short_description = 'Commande'

    def taux_pct(self, obj):
        return f"{float(obj.taux)*100:.0f}%"
    taux_pct.short_description = 'Taux'

    def montant_fmt(self, obj):
        return f"{obj.montant:,} FCFA".replace(',', ' ')
    montant_fmt.short_description = 'Montant'

    def statut_badge(self, obj):
        colors = {'en_attente': '#F0A500', 'versee': '#16914E'}
        c = colors.get(obj.statut, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'

    @admin.action(description='Marquer comme versée(s)')
    def marquer_versees(self, request, queryset):
        count = 0
        for c in queryset.filter(statut='en_attente'):
            c.verser(note=f"Versement groupé par {request.user}")
            count += 1
        self.message_user(request, f"{count} commission(s) marquée(s) comme versée(s).")
