from django.contrib import admin
from django.views.static import serve
from django.conf import settings
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from dashboard import views as dashboard_views

admin.site.site_header = 'NETROVA Administration'
admin.site.site_title = 'NETROVA Admin'
admin.site.index_title = ''

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('cgu/', views.cgu, name='cgu'),
    path('membres-hierarchie/', dashboard_views.hierarchie_reseau, name='hierarchie_reseau'),
    path('admin/', admin.site.urls),
    path('membres/', include('membres.urls')),
    path('packs/', include('produits.urls')),
    path('commandes/', include('commandes.urls')),
    path('reseau/', include('reseau.urls')),
    path('partenaires/', include('partenaires.urls')),
    path('api/v1/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    # PWA files served directly (needed for service worker scope)
    path('static/sw.js', serve, {'document_root': settings.BASE_DIR / 'static', 'path': 'sw.js'}),
    path('static/manifest.json', serve, {'document_root': settings.BASE_DIR / 'static', 'path': 'manifest.json'}),
]
