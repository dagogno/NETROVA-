from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, ProfilForm, ProgrammeCreditForm
from .models import Membre


# ── helper ────────────────────────────────────────────────────────────────────
def _get_membre_or_redirect(request):
    """Retourne (membre, None) ou (None, redirect) si le profil est absent."""
    try:
        return request.user.membre, None
    except Membre.DoesNotExist:
        messages.warning(
            request,
            "⚠️ Votre compte n'a pas encore de profil membre NETROVA. "
            "Si vous êtes administrateur, utilisez l'interface /admin/. "
            "Pour un profil membre, inscrivez-vous normalement."
        )
        return None, redirect('accueil')


def _score_context(membre):
    """Renvoie le contexte du score (jauge SVG)."""
    score_label, score_color = membre.get_score_label()
    circ   = 245
    offset = round(circ - (circ * membre.score_confiance / 100), 1)
    return {'score_label': score_label, 'score_color': score_color,
            'score_offset': offset, 'score_circumference': circ}


# ── Inscription ────────────────────────────────────────────────────────────────
def inscription(request):
    if request.user.is_authenticated:
        return redirect('membres:tableau_de_bord')
    initial = {}
    ref = request.GET.get('ref', '').upper()
    if ref:
        initial['code_parrain'] = ref
    form = InscriptionForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        membre = form.save()
        login(request, membre.user)
        messages.success(request, f"Bienvenue dans la famille NETROVA, {membre.nom_complet} ! 🎉")
        return redirect('membres:tableau_de_bord')
    from .forms import CONDITIONS_TEXT
    return render(request, 'membres/inscription.html', {'form': form, 'conditions': CONDITIONS_TEXT})


# ── Connexion / déconnexion ───────────────────────────────────────────────────
def connexion(request):
    if request.user.is_authenticated:
        return redirect('membres:tableau_de_bord')
    form = ConnexionForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'membres:tableau_de_bord'))
    return render(request, 'membres/connexion.html', {'form': form})


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accueil')


# ── Tableau de bord ────────────────────────────────────────────────────────────
@login_required
def tableau_de_bord(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir

    # Recalcul score
    score = membre.calculer_score()
    if score != membre.score_confiance:
        membre.score_confiance = score
        membre.save(update_fields=['score_confiance'])

    commandes   = membre.commandes.select_related('pack').order_by('-date_commande')[:5]
    filleuls    = membre.filleuls.select_related('user').filter(statut='actif')[:8]
    commissions = membre.commissions.select_related('commande__pack').order_by('-date_calcul')[:5]

    ctx = {
        'membre': membre,
        'commandes': commandes,
        'filleuls': filleuls,
        'commissions': commissions,
        'stats': {
            'nb_commandes':      membre.commandes.count(),
            'nb_en_cours':       membre.commandes.filter(statut__in=['en_attente', 'acompte_paye']).count(),
            'nb_filleuls':       membre.nombre_filleuls,
            'solde_commissions': membre.solde_commissions,
        },
    }
    ctx.update(_score_context(membre))
    return render(request, 'membres/tableau_de_bord.html', ctx)


# ── Profil ────────────────────────────────────────────────────────────────────
@login_required
def profil(request):
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir

    form = ProfilForm(request.POST or None, instance=membre)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour avec succès. ✅")
        return redirect('membres:profil')

    ctx = {'forme': form, 'membre': membre}
    ctx.update(_score_context(membre))
    return render(request, 'membres/profil.html', ctx)


# ── Programme crédit (KYC) ─────────────────────────────────────────────────────
@login_required
def programme_credit(request):
    """
    Seul point d'entrée du KYC dans toute l'application : un membre qui souhaite
    pouvoir commander à crédit (paiement par tranches, acompte 50%) doit
    volontairement soumettre ses documents d'identité ici.
    """
    membre, redir = _get_membre_or_redirect(request)
    if redir:
        return redir

    form = None
    if membre.kyc_statut in ('non_requis', 'rejete'):
        form = ProgrammeCreditForm(request.POST or None, request.FILES or None, instance=membre)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, "✅ Votre demande de participation au programme crédit a été envoyée.")
            messages.info(request, "📋 L'équipe NETROVA vérifie vos documents sous peu. Vous pourrez alors commander à crédit.")
            return redirect('membres:programme_credit')

    return render(request, 'membres/programme_credit.html', {'membre': membre, 'form': form})


# ── Mon réseau ────────────────────────────────────────────────────────────────
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
        'membre':          membre,
        'arbre':           arbre,
        'lien_parrainage': lien,
        'nb_niveau1':      membre.filleuls.filter(statut='actif').count(),
        'nb_niveau2':      nb_niveau2,
    })
