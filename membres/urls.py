from django.urls import path
from . import views

app_name = 'membres'

urlpatterns = [
    path('inscription/',     views.inscription,     name='inscription'),
    path('connexion/',       views.connexion,       name='connexion'),
    path('deconnexion/',     views.deconnexion,     name='deconnexion'),
    path('tableau-de-bord/', views.tableau_de_bord, name='tableau_de_bord'),
    path('profil/',          views.profil,          name='profil'),
    path('programme-credit/', views.programme_credit, name='programme_credit'),
    path('mon-reseau/',      views.mon_reseau,      name='mon_reseau'),
]
