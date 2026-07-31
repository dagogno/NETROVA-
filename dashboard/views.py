from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from membres.models import Membre


@staff_member_required
def hierarchie_reseau(request):
    """
    Vue admin : affiche TOUS les membres de NETROVA organisés par hiérarchie
    (parrain → filleuls → filleuls de filleuls...).
    Seuls les membres sans parrain (racines) sont affichés au premier niveau ;
    chaque branche se déplie récursivement dans le template.
    """
    racines_qs = (
        Membre.objects
        .filter(parrain__isnull=True)
        .select_related('user')
        .order_by('-date_inscription')
    )

    arbre = [
        {
            'membre': m,
            'niveau': 0,
            'filleuls': m.get_arbre_filleuls(profondeur=15),
        }
        for m in racines_qs
    ]

    total_membres = Membre.objects.count()

    return render(request, 'admin/membres/hierarchie.html', {
        'arbre': arbre,
        'total_membres': total_membres,
        'title': 'Hiérarchie complète du réseau',
    })
