from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/',    views.login_view, name='login'),
    path('auth/logout/',   views.logout_view, name='logout'),

    path('me/', views.me, name='me'),
    path('programme-credit/', views.programme_credit, name='programme_credit'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('commandes/', views.commandes_list, name='commandes_list'),
    path('commandes/<int:pk>/', views.commande_detail, name='commande_detail'),

    path('reseau/', views.reseau, name='reseau'),
    path('commissions/', views.commissions_list, name='commissions_list'),

    path('packs/', views.packs_list, name='packs_list'),
    path('packs/<str:code>/', views.pack_detail, name='pack_detail'),

    path('partenaires/', views.partenaires_list, name='partenaires_list'),
    path('partenaires/<int:pk>/', views.partenaire_detail, name='partenaire_detail'),

    path('cgu/', views.cgu, name='cgu'),
]
