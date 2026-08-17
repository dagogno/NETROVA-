from django.urls import path
from . import views

app_name = 'partenaires'

urlpatterns = [
    path('',         views.liste_partenaires, name='liste'),
    path('<int:pk>/', views.detail_partenaire, name='detail'),
]
