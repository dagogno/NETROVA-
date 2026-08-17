"""
Calcule les statistiques affichées sur la page d'accueil de l'admin Django
(/admin/). Ne s'exécute que sur cette page précise pour ne pas alourdir
le reste du site.
"""
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone


def admin_dashboard_stats(request):
    if request.path.rstrip('/') != '/admin':
        return {}

    # Imports différés pour éviter les soucis de chargement d'apps
    from membres.models import Membre
    from commandes.models import Commande, Paiement
    from reseau.models import Commission
    from produits.models import Pack

    now = timezone.now()
    debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    il_y_a_7j = now - timedelta(days=7)

    membres_qs = Membre.objects.all()
    commandes_qs = Commande.objects.all()

    revenu_mois = Paiement.objects.filter(date_paiement__gte=debut_mois).aggregate(
        total=Sum('montant'))['total'] or 0

    stats = {
        'nb_membres_total':     membres_qs.count(),
        'nb_membres_actifs':    membres_qs.filter(statut='actif').count(),
        'nb_membres_7j':        membres_qs.filter(date_inscription__gte=il_y_a_7j).count(),
        'nb_kyc_attente':       membres_qs.filter(kyc_statut='en_attente').count(),
        'nb_kyc_valide':        membres_qs.filter(kyc_statut='valide').count(),

        'nb_commandes_total':   commandes_qs.count(),
        'nb_commandes_attente': commandes_qs.filter(statut='en_attente').count(),
        'nb_commandes_retard':  commandes_qs.filter(statut='en_retard').count(),
        'nb_commandes_soldees': commandes_qs.filter(statut='soldee').count(),

        'revenu_mois':            revenu_mois,
        'nb_commissions_attente': Commission.objects.filter(statut='en_attente').count(),
        'montant_commissions_attente': Commission.objects.filter(statut='en_attente').aggregate(
            total=Sum('montant'))['total'] or 0,

        'nb_packs': Pack.objects.filter(disponible=True).count(),

        'dernieres_commandes': commandes_qs.select_related('membre__user', 'pack').order_by('-date_commande')[:6],
        'derniers_membres':    membres_qs.select_related('user').order_by('-date_inscription')[:6],
        'membres_kyc_attente': membres_qs.filter(kyc_statut='en_attente').select_related('user').order_by('-date_inscription')[:6],
        'commandes_en_retard': commandes_qs.filter(statut='en_retard').select_related('membre__user', 'pack')[:6],
    }
    return {'netrova_stats': stats}
