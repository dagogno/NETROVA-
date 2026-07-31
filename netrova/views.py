from django.shortcuts import render
from produits.models import Pack

def accueil(request):
    packs = Pack.objects.filter(disponible=True).order_by('prix')
    return render(request, 'accueil.html', {'packs': packs})

def cgu(request):
    return render(request, 'cgu.html')
