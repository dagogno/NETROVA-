from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone
from .models import Commande, Paiement


class PaiementInline(admin.TabularInline):
    model  = Paiement
    extra  = 1
    fields = ['montant', 'mode_paiement', 'date_paiement', 'note']
    readonly_fields = ['date_paiement']


class RemisePenaliteForm(forms.Form):
    """Formulaire inline dans l'admin pour accorder une remise."""
    montant_remise = forms.IntegerField(min_value=0, label='Montant à remettre (FCFA)')
    note           = forms.CharField(required=False, label='Raison de la remise',
                                     widget=forms.TextInput(attrs={'placeholder': 'Ex: accord commercial, geste commercial...'}))


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display  = ['ref', 'membre_nom', 'pack', 'montant_fmt',
                     'verse_fmt', 'solde_fmt', 'penalite_fmt',
                     'statut_badge', 'penalite_status', 'date_commande']
    list_filter   = ['statut', 'penalite_activee', 'pack', 'date_commande']
    search_fields = ['membre__user__first_name', 'membre__user__last_name',
                     'membre__telephone', 'pk']
    readonly_fields = ['montant_total', 'acompte_requis', 'montant_verse',
                       'penalite_nette', 'solde_restant', 'penalite_totale',
                       'jours_retard', 'commission_calculee', 'date_commande']
    inlines = [PaiementInline]

    fieldsets = (
        ('📦 Commande', {
            'fields': ('membre', 'pack', 'quantite', 'statut', 'date_commande', 'date_limite_solde', 'note')
        }),
        ('💰 Finances', {
            'fields': ('montant_total', 'acompte_requis', 'montant_verse', 'solde_restant')
        }),
        ('⚠️ Pénalités — Contrôle Admin', {
            'fields': (
                'penalite_activee', 'penalite_taux',
                'penalite_totale', 'penalite_remisee', 'penalite_nette',
                'jours_retard', 'penalite_note_admin'
            ),
            'description': (
                '🔧 <strong>Contrôle total :</strong> '
                'Vous pouvez modifier le taux, accorder une remise partielle ou totale, '
                'ou désactiver complètement les pénalités pour cette commande. '
                'Utilisez les actions en bas de liste pour appliquer en masse.'
            ),
        }),
        ('🤝 Suivi', {'fields': ('commission_calculee',)}),
    )

    actions = [
        'action_calculer_penalites',
        'action_effacer_penalites',
        'action_suspendre_penalites',
        'action_reactiver_penalites',
        'action_marquer_annulee',
    ]

    # ── Display helpers ────────────────────────────────────────────────────
    def ref(self, obj):
        return f"CMD-{obj.pk:04d}"
    ref.short_description = 'Réf.'

    def membre_nom(self, obj):
        return obj.membre.nom_complet
    membre_nom.short_description = 'Membre'

    def montant_fmt(self, obj):
        return f"{obj.montant_total:,} F".replace(',', ' ')
    montant_fmt.short_description = 'Total'

    def verse_fmt(self, obj):
        return f"{obj.montant_verse:,} F".replace(',', ' ')
    verse_fmt.short_description = 'Versé'

    def solde_fmt(self, obj):
        s = obj.solde_restant
        c = 'red' if s > 0 else '#16914E'
        return format_html('<b style="color:{}">{:,} F</b>', c, s)
    solde_fmt.short_description = 'Solde dû'

    def penalite_fmt(self, obj):
        if obj.penalite_totale == 0:
            return '—'
        html = f'{obj.penalite_totale:,} F'.replace(',', ' ')
        if obj.penalite_remisee > 0:
            html += f' <small style="color:#16914E">(-{obj.penalite_remisee:,} F remis)</small>'.replace(',', ' ')
        return format_html(html)
    penalite_fmt.short_description = 'Pénalités'
    penalite_fmt.allow_tags = True

    def statut_badge(self, obj):
        colors = {
            'en_attente': '#888', 'acompte_paye': '#E8A12B',
            'soldee': '#16914E', 'annulee': '#999', 'en_retard': '#E74C3C',
        }
        c = colors.get(obj.statut, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            c, obj.get_statut_display())
    statut_badge.short_description = 'Statut'

    def penalite_status(self, obj):
        if not obj.penalite_activee:
            return format_html('<span style="color:#888;font-size:11px">⏸ Suspendue</span>')
        if obj.est_en_retard:
            return format_html('<span style="color:#E74C3C;font-size:11px;font-weight:700">🔴 En retard +{}j</span>', obj.jours_retard)
        return format_html('<span style="color:#16914E;font-size:11px">✅ OK</span>')
    penalite_status.short_description = 'Retard'

    # ── Actions en masse ───────────────────────────────────────────────────
    @admin.action(description='⚠️ Calculer / mettre à jour les pénalités de retard')
    def action_calculer_penalites(self, request, queryset):
        count = 0
        for cmd in queryset.filter(statut__in=['acompte_paye', 'en_retard'], penalite_activee=True):
            if cmd.est_en_retard:
                cmd.calculer_penalite()
                count += 1
        self.message_user(request, f"✅ {count} commande(s) mise(s) à jour.", messages.SUCCESS)

    @admin.action(description='🎁 Effacer toutes les pénalités (remise 100%)')
    def action_effacer_penalites(self, request, queryset):
        count = 0
        for cmd in queryset:
            if cmd.penalite_totale > 0:
                cmd.effacer_penalites(note=f'Remise accordée par {request.user} le {timezone.now().date()}')
                count += 1
        self.message_user(request, f"✅ Pénalités effacées sur {count} commande(s).", messages.SUCCESS)

    @admin.action(description='⏸ Suspendre les pénalités futures')
    def action_suspendre_penalites(self, request, queryset):
        n = queryset.update(penalite_activee=False)
        self.message_user(request, f"⏸ Pénalités suspendues sur {n} commande(s).", messages.WARNING)

    @admin.action(description='▶️ Réactiver les pénalités')
    def action_reactiver_penalites(self, request, queryset):
        n = queryset.update(penalite_activee=True)
        self.message_user(request, f"▶️ Pénalités réactivées sur {n} commande(s).", messages.SUCCESS)

    @admin.action(description='❌ Marquer comme annulée(s)')
    def action_marquer_annulee(self, request, queryset):
        n = queryset.filter(statut='en_attente').update(statut='annulee')
        self.message_user(request, f"❌ {n} commande(s) annulée(s).", messages.WARNING)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for paiement in instances:
            if not paiement.pk:
                paiement.enregistre_par = request.user
            paiement.save()
            # Met à jour la commande après chaque paiement
            cmd = paiement.commande
            cmd.montant_verse = sum(cmd.paiements.values_list('montant', flat=True))
            if cmd.montant_verse >= cmd.acompte_requis and cmd.statut == 'en_attente':
                cmd.statut = 'acompte_paye'
            if cmd.montant_verse >= (cmd.montant_total + cmd.penalite_nette):
                cmd.statut = 'soldee'
                cmd._declencher_commission()
            cmd.save(update_fields=['montant_verse', 'statut'])
        formset.save_m2m()


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display  = ['commande', 'montant_fmt', 'mode_paiement', 'date_paiement', 'enregistre_par']
    list_filter   = ['mode_paiement', 'date_paiement']
    search_fields = ['commande__membre__user__last_name', 'commande__pk']
    readonly_fields = ['date_paiement']

    def montant_fmt(self, obj):
        return f"{obj.montant:,} FCFA".replace(',', ' ')
    montant_fmt.short_description = 'Montant'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.enregistre_par = request.user
        super().save_model(request, obj, form, change)
        cmd = obj.commande
        cmd.montant_verse = sum(cmd.paiements.values_list('montant', flat=True))
        if cmd.montant_verse >= cmd.acompte_requis and cmd.statut == 'en_attente':
            cmd.statut = 'acompte_paye'
        if cmd.montant_verse >= (cmd.montant_total + cmd.penalite_nette):
            cmd.statut = 'soldee'
            cmd._declencher_commission()
        cmd.save(update_fields=['montant_verse', 'statut'])
