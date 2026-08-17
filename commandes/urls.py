from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    path('',         views.mes_commandes,   name='mes_commandes'),
    path('<int:pk>/', views.detail_commande, name='detail'),
]
