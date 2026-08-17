from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from membres.models import Membre
from membres.forms import CONDITIONS_TEXT
from commandes.models import Commande
from produits.models import Pack
from reseau.models import Commission
from partenaires.models import Partenaire, CategoriePartenaire

from .serializers import (
    MembreSerializer, InscriptionSerializer, ProfilUpdateSerializer, ProgrammeCreditSerializer,
    PackSerializer, CommandeSerializer, CommandeDetailSerializer, CommissionSerializer,
    PartenaireSerializer, PartenaireDetailSerializer, CategoriePartenaireSerializer,
    serialize_arbre,
)


def _membre_or_404(request):
    return get_object_or_404(Membre, user=request.user)


# ── Auth ─────────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Inscription — sans KYC. Voir InscriptionSerializer."""
    serializer = InscriptionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    membre = serializer.save()
    token, _ = Token.objects.get_or_create(user=membre.user)
    return Response(
        {'token': token.key, 'membre': MembreSerializer(membre, context={'request': request}).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({'detail': "Identifiants incorrects."}, status=status.HTTP_401_UNAUTHORIZED)
    membre = Membre.objects.filter(user=user).first()
    if not membre:
        return Response({'detail': "Ce compte n'a pas de profil membre NETROVA."}, status=status.HTTP_403_FORBIDDEN)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'membre': MembreSerializer(membre, context={'request': request}).data})


@api_view(['POST'])
def logout_view(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Profil ───────────────────────────────────────────────────────────────────
@api_view(['GET', 'PATCH'])
def me(request):
    membre = _membre_or_404(request)
    if request.method == 'PATCH':
        serializer = ProfilUpdateSerializer(membre, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(MembreSerializer(membre, context={'request': request}).data)


# ── Programme crédit (seul point d'entrée du KYC) ────────────────────────────
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def programme_credit(request):
    membre = _membre_or_404(request)

    if request.method == 'POST':
        if membre.kyc_statut not in ('non_requis', 'rejete'):
            return Response(
                {'detail': "Une demande est déjà en cours ou déjà validée."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ProgrammeCreditSerializer(membre, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MembreSerializer(membre, context={'request': request}).data, status=status.HTTP_201_CREATED)

    return Response({
        'kyc_statut': membre.kyc_statut,
        'kyc_statut_display': membre.get_kyc_statut_display(),
        'kyc_note': membre.kyc_note,
        'peut_soumettre': membre.kyc_statut in ('non_requis', 'rejete'),
    })


# ── Tableau de bord ───────────────────────────────────────────────────────────
@api_view(['GET'])
def dashboard(request):
    membre = _membre_or_404(request)
    commandes   = membre.commandes.select_related('pack').order_by('-date_commande')[:5]
    filleuls    = membre.filleuls.select_related('user').filter(statut='actif')[:8]
    commissions = membre.commissions.select_related('commande__pack').order_by('-date_calcul')[:5]

    label, color = membre.get_score_label()
    circ = 245
    offset = round(circ - (circ * membre.score_confiance / 100), 1)

    return Response({
        'membre': MembreSerializer(membre, context={'request': request}).data,
        'score': {'label': label, 'color': color, 'circumference': circ, 'offset': offset},
        'commandes_recentes': CommandeSerializer(commandes, many=True).data,
        'filleuls_recents': MembreSerializer(filleuls, many=True, context={'request': request}).data,
        'commissions_recentes': CommissionSerializer(commissions, many=True).data,
    })


# ── Commandes ────────────────────────────────────────────────────────────────
@api_view(['GET'])
def commandes_list(request):
    membre = _membre_or_404(request)
    qs = membre.commandes.select_related('pack').order_by('-date_commande')
    return Response(CommandeSerializer(qs, many=True).data)


@api_view(['GET'])
def commande_detail(request, pk):
    membre = _membre_or_404(request)
    commande = get_object_or_404(Commande.objects.select_related('pack').prefetch_related('paiements'), pk=pk, membre=membre)
    return Response(CommandeDetailSerializer(commande).data)


# ── Réseau ───────────────────────────────────────────────────────────────────
@api_view(['GET'])
def reseau(request):
    membre = _membre_or_404(request)
    arbre = membre.get_arbre_filleuls(profondeur=3)
    lien  = request.build_absolute_uri(f"/membres/inscription/?ref={membre.code_parrainage}")
    nb_niveau2 = sum(
        f.filleuls.filter(statut='actif').count()
        for f in membre.filleuls.filter(statut='actif')
    )
    return Response({
        'lien_parrainage': lien,
        'code_parrainage': membre.code_parrainage,
        'nb_niveau1': membre.filleuls.filter(statut='actif').count(),
        'nb_niveau2': nb_niveau2,
        'taille_equipe_totale': membre.taille_equipe_totale,
        'arbre': serialize_arbre(arbre),
    })


@api_view(['GET'])
def commissions_list(request):
    membre = _membre_or_404(request)
    qs = membre.commissions.select_related('commande__pack').order_by('-date_calcul')
    return Response(CommissionSerializer(qs, many=True).data)


# ── Packs (public) ────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def packs_list(request):
    qs = Pack.objects.filter(disponible=True).prefetch_related('composants')
    return Response(PackSerializer(qs, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pack_detail(request, code):
    pack = get_object_or_404(Pack, code=code.upper(), disponible=True)
    return Response(PackSerializer(pack, context={'request': request}).data)


# ── Partenaires (public) ──────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def partenaires_list(request):
    categorie_slug = request.GET.get('categorie')
    qs = Partenaire.objects.filter(statut='actif').select_related('categorie').prefetch_related('produits')
    if categorie_slug:
        qs = qs.filter(categorie__slug=categorie_slug)
    return Response({
        'partenaires': PartenaireSerializer(qs, many=True, context={'request': request}).data,
        'categories': CategoriePartenaireSerializer(CategoriePartenaire.objects.all(), many=True).data,
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def partenaire_detail(request, pk):
    partenaire = get_object_or_404(Partenaire, pk=pk, statut='actif')
    return Response(PartenaireDetailSerializer(partenaire, context={'request': request}).data)


# ── CGU (public) ───────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cgu(request):
    return Response({'texte': CONDITIONS_TEXT})
