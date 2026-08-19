from django.shortcuts import render, get_object_or_404
from .models import Partenaire, CategoriePartenaire


def liste_partenaires(request):
    categorie_slug = request.GET.get('categorie')
    categories     = CategoriePartenaire.objects.all()
    partenaires    = Partenaire.objects.filter(statut='actif').select_related('categorie').prefetch_related('produits')
    if categorie_slug:
        partenaires = partenaires.filter(categorie__slug=categorie_slug)
    categorie_active = CategoriePartenaire.objects.filter(slug=categorie_slug).first() if categorie_slug else None
    return render(request, 'partenaires/liste.html', {
        'partenaires':      partenaires,
        'categories':       categories,
        'categorie_active': categorie_active,
    })


def detail_partenaire(request, pk):
    partenaire = get_object_or_404(Partenaire, pk=pk, statut='actif')
    return render(request, 'partenaires/detail.html', {'partenaire': partenaire})
