from django.urls import path
from . import views

app_name = 'reseau'

urlpatterns = [
    path('commissions/', views.mes_commissions, name='commissions'),
]
