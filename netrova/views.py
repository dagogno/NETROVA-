from django.shortcuts import render
from produits.models import Pack


def accueil(request):
    packs = Pack.objects.filter(disponible=True).prefetch_related('composants').order_by('prix')
    # Partenaires actifs en vedette (max 4 sur l'accueil)
    try:
        from partenaires.models import Partenaire
        partenaires = Partenaire.objects.filter(statut='actif').order_by('ordre_affichage')[:4]
    except Exception:
        partenaires = []
    return render(request, 'accueil.html', {'packs': packs, 'partenaires': partenaires})


def cgu(request):
    return render(request, 'cgu.html')
