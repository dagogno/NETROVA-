from django.shortcuts import render, get_object_or_404
from .models import Pack

def catalogue(request):
    packs = Pack.objects.filter(disponible=True).prefetch_related('composants')
    return render(request, 'produits/catalogue.html', {'packs': packs})

def detail_pack(request, code):
    pack = get_object_or_404(Pack, code=code.upper(), disponible=True)
    return render(request, 'produits/detail_pack.html', {'pack': pack})
