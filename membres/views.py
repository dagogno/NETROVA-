from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, ProfilForm
from .models import Membre


def _get_membre_or_redirect(request):
    """
    Retourne le Membre lié au user connecté.
    Si aucun profil n'existe (ex : compte admin créé via createsuperuser),
    affiche un message clair et redirige vers la page d'accueil.
    Retourne (membre, None) ou (None, redirect_response).
    """
    try:
        return request.user.membre, None
    except Membre.DoesNotExist:
        messages.warning(
            request,
            "⚠️ Votre compte n'a pas encore de profil membre NETROVA. "
            "Si vous êtes administrateur, utilisez l'interface /admin/ pour gérer la plateforme. "
            "Pour créer un profil membre, inscrivez-vous normalement."
        )
        return None, redirect('accueil')


def inscription(request):
    if request.user.is_authenticated:
        return redirect('membres:tableau_de_bord')
    initial = {}
    ref = request.GET.get('ref', '')
    if ref:
        initial['code_parrain'] = ref.upper()
    form = InscriptionForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        membre = form.save()
        login(request, membre.user)
        messages.success(request, f"Bienvenue dans la famille NETROVA, {membre.nom_complet} ! 🎉")
        return redirect('membres:tableau_de_bord')
    from .forms import CONDITIONS_TEXT
    return render(request, 'membres/inscription.html', {'form': form, 'conditions': CONDITIONS_TEXT})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('membres:tableau_de_bord')
    form = ConnexionForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        next_url = request.GET.get('next', '')
        return redirect(next_url) if next_url else redirect('membres:tableau_de_bord')
    return render(request, 'membres/connexion.html', {'form': form})


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accueil')


@login_required
def tableau_de_bord(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir

    # Recalcul du score à chaque visite
    score = membre.calculer_score()
    if score != membre.score_confiance:
        membre.score_confiance = score
        membre.save(update_fields=['score_confiance'])

    commandes   = membre.commandes.select_related('pack').order_by('-date_commande')[:5]
    filleuls    = membre.filleuls.select_related('user').filter(statut='actif')[:8]
    commissions = membre.commissions.select_related('commande__pack').order_by('-date_calcul')[:5]
    score_label, score_color = membre.get_score_label()
    circonference = 245
    score_offset  = round(circonference - (circonference * membre.score_confiance / 100), 1)

    return render(request, 'membres/tableau_de_bord.html', {
        'membre':      membre,
        'commandes':   commandes,
        'filleuls':    filleuls,
        'commissions': commissions,
        'score_label': score_label,
        'score_color': score_color,
        'score_offset':        score_offset,
        'score_circumference': circonference,
        'stats': {
            'nb_commandes':      membre.commandes.count(),
            'nb_en_cours':       membre.commandes.filter(statut__in=['en_attente', 'acompte_paye']).count(),
            'nb_filleuls':       membre.nombre_filleuls,
            'solde_commissions': membre.solde_commissions,
        },
    })


@login_required
def profil(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir

    form = ProfilForm(request.POST or None, request.FILES or None, instance=membre)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('membres:profil')

    score_label, score_color = membre.get_score_label()
    circonference = 245
    score_offset  = round(circonference - (circonference * membre.score_confiance / 100), 1)

    return render(request, 'membres/profil.html', {
        'forme':               form,
        'membre':              membre,
        'score_label':         score_label,
        'score_color':         score_color,
        'score_offset':        score_offset,
        'score_circumference': circonference,
    })


@login_required
def mon_reseau(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir

    arbre = membre.get_arbre_filleuls(profondeur=3)
    lien  = request.build_absolute_uri(f"/membres/inscription/?ref={membre.code_parrainage}")

    nb_niveau2 = sum(
        f.filleuls.filter(statut='actif').count()
        for f in membre.filleuls.filter(statut='actif')
    )

    return render(request, 'membres/mon_reseau.html', {
        'membre':           membre,
        'arbre':            arbre,
        'lien_parrainage':  lien,
        'nb_niveau1':       membre.filleuls.filter(statut='actif').count(),
        'nb_niveau2':       nb_niveau2,
    })
