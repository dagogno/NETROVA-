from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Commission


def _get_membre_or_redirect(request):
    try:
        return request.user.membre, None
    except Exception:
        messages.warning(request, "⚠️ Votre compte n'a pas de profil membre NETROVA.")
        return None, redirect('accueil')


@login_required
def mes_commissions(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir
    commissions = membre.commissions.select_related('commande__pack').order_by('-date_calcul')
    return render(request, 'reseau/mes_commissions.html', {
        'membre': membre,
        'commissions': commissions,
    })
