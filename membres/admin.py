from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Membre


class MembreInline(admin.StackedInline):
    model  = Membre
    extra  = 0
    fields = ['telephone', 'adresse', 'zone', 'statut', 'kyc_statut', 'score_confiance', 'code_parrainage']
    readonly_fields = ['code_parrainage', 'score_confiance']


class UserAdmin(BaseUserAdmin):
    inlines = [MembreInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display  = ['nom_complet', 'telephone', 'zone', 'parrain_nom',
                     'nombre_filleuls', 'statut_badge', 'kyc_badge',
                     'score_badge', 'date_inscription']
    list_filter   = ['statut', 'kyc_statut', 'zone', 'date_inscription']
    search_fields = ['user__first_name', 'user__last_name', 'telephone', 'code_parrainage']
    readonly_fields = ['code_parrainage', 'date_inscription', 'nombre_filleuls',
                       'score_confiance', 'taux_commission', 'solde_commissions',
                       'photo_kyc_preview', 'cni_recto_preview']
    actions = ['valider_kyc', 'rejeter_kyc', 'recalculer_scores']

    fieldsets = (
        ('Compte', {'fields': ('user', 'statut', 'contrat_accepte', 'date_inscription')}),
        ('Coordonnées', {'fields': ('telephone', 'adresse', 'zone')}),
        ('Réseau', {'fields': ('parrain', 'code_parrainage', 'nombre_filleuls', 'taux_commission')}),
        ('Personne de confiance', {'fields': ('personne_confiance_nom', 'personne_confiance_tel')}),
        ('KYC — Vérification identité', {'fields': (
            'photo_profil', 'photo_kyc_preview',
            'carte_identite_recto', 'cni_recto_preview',
            'carte_identite_verso', 'kyc_statut', 'kyc_note'
        )}),
        ('Score & Finances', {'fields': ('score_confiance', 'solde_commissions')}),
        ('Notes admin', {'fields': ('note_admin',)}),
    )

    def nom_complet(self, obj): return obj.nom_complet
    nom_complet.short_description = 'Nom'

    def parrain_nom(self, obj): return obj.parrain.nom_complet if obj.parrain else '—'
    parrain_nom.short_description = 'Parrain'

    def statut_badge(self, obj):
        c = {'actif': '#16914E', 'inactif': '#888', 'suspendu': '#E74C3C'}.get(obj.statut, '#888')
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>', c, obj.get_statut_display())
    statut_badge.short_description = 'Statut'

    def kyc_badge(self, obj):
        c = {'valide': '#16914E', 'rejete': '#E74C3C', 'en_attente': '#F0A500'}.get(obj.kyc_statut, '#888')
        icons = {'valide': '✅', 'rejete': '❌', 'en_attente': '⏳'}
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{} {}</span>',
            c, icons.get(obj.kyc_statut, ''), obj.get_kyc_statut_display())
    kyc_badge.short_description = 'KYC'

    def score_badge(self, obj):
        s = obj.score_confiance
        c = '#16914E' if s >= 80 else '#1A4DB5' if s >= 60 else '#F0A500' if s >= 40 else '#E74C3C'
        return format_html('<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">{}/100</span>', c, s)
    score_badge.short_description = 'Score'

    def photo_kyc_preview(self, obj):
        if obj.photo_profil:
            return format_html('<img src="{}" style="max-height:120px;border-radius:8px"/>', obj.photo_profil.url)
        return '—'
    photo_kyc_preview.short_description = 'Aperçu photo'

    def cni_recto_preview(self, obj):
        if obj.carte_identite_recto:
            return format_html('<img src="{}" style="max-height:120px;border-radius:8px"/>', obj.carte_identite_recto.url)
        return '—'
    cni_recto_preview.short_description = 'Aperçu CNI'

    @admin.action(description='✅ Valider le KYC des membres sélectionnés')
    def valider_kyc(self, request, queryset):
        n = queryset.update(kyc_statut='valide')
        for m in queryset:
            m.score_confiance = m.calculer_score(); m.save(update_fields=['score_confiance'])
        self.message_user(request, f"{n} membre(s) KYC validé(s).")

    @admin.action(description='❌ Rejeter le KYC des membres sélectionnés')
    def rejeter_kyc(self, request, queryset):
        n = queryset.update(kyc_statut='rejete')
        self.message_user(request, f"{n} membre(s) KYC rejeté(s).")

    @admin.action(description='🔄 Recalculer les scores de confiance')
    def recalculer_scores(self, request, queryset):
        for m in queryset:
            m.score_confiance = m.calculer_score()
            m.save(update_fields=['score_confiance'])
        self.message_user(request, f"{queryset.count()} score(s) recalculé(s).")
