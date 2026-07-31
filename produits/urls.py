from django.urls import path
from . import views

app_name = 'produits'

urlpatterns = [
    path('',          views.catalogue,   name='catalogue'),
    path('<str:code>/', views.detail_pack, name='detail'),
]
