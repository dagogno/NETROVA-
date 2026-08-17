from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def _get_membre_or_redirect(request):
    try:
        return request.user.membre, None
    except Exception:
        messages.warning(request, "⚠️ Votre compte n'a pas de profil membre NETROVA.")
        return None, redirect('accueil')


@login_required
def mes_commandes(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir
    commandes = membre.commandes.select_related('pack').prefetch_related('paiements').order_by('-date_commande')
    return render(request, 'commandes/mes_commandes.html', {'membre': membre, 'commandes': commandes})


@login_required
def detail_commande(request, pk):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir
    from .models import Commande
    commande = get_object_or_404(Commande, pk=pk, membre=membre)
    return render(request, 'commandes/detail_commande.html', {'commande': commande, 'membre': membre})
