from rest_framework import serializers
from django.contrib.auth.models import User
from membres.models import Membre
from commandes.models import Commande, Paiement
from produits.models import Pack, Composant
from reseau.models import Commission
from partenaires.models import Partenaire, CategoriePartenaire, ProduitPartenaire


# ── Membre / Auth ───────────────────────────────────────────────────────────
class MembreSerializer(serializers.ModelSerializer):
    nom_complet          = serializers.ReadOnlyField()
    prenom                = serializers.CharField(source='user.first_name', read_only=True)
    nom                    = serializers.CharField(source='user.last_name', read_only=True)
    email                = serializers.EmailField(source='user.email', read_only=True)
    nombre_filleuls       = serializers.ReadOnlyField()
    nb_commandes_soldees   = serializers.ReadOnlyField()
    kyc_documents_fournis  = serializers.ReadOnlyField()
    peut_commander_credit  = serializers.ReadOnlyField()
    programme_credit_en_attente = serializers.ReadOnlyField()
    taille_equipe_totale  = serializers.ReadOnlyField()
    taux_commission        = serializers.ReadOnlyField()
    solde_commissions      = serializers.ReadOnlyField()
    commissions_versees    = serializers.ReadOnlyField()
    kyc_statut_display     = serializers.CharField(source='get_kyc_statut_display', read_only=True)
    score_label             = serializers.SerializerMethodField()
    photo_profil            = serializers.SerializerMethodField()
    carte_identite_recto     = serializers.SerializerMethodField()
    carte_identite_verso     = serializers.SerializerMethodField()

    class Meta:
        model = Membre
        fields = [
            'id', 'nom_complet', 'prenom', 'nom', 'email', 'telephone', 'adresse', 'zone',
            'personne_confiance_nom', 'personne_confiance_tel',
            'code_parrainage', 'statut', 'date_inscription',
            'kyc_statut', 'kyc_statut_display', 'kyc_note', 'kyc_documents_fournis',
            'peut_commander_credit', 'programme_credit_en_attente',
            'photo_profil', 'carte_identite_recto', 'carte_identite_verso',
            'score_confiance', 'score_label',
            'nombre_filleuls', 'nb_commandes_soldees', 'taille_equipe_totale',
            'taux_commission', 'solde_commissions', 'commissions_versees',
        ]

    def get_score_label(self, obj):
        label, color = obj.get_score_label()
        return {'label': label, 'color': color}

    def _image_url(self, obj, field):
        f = getattr(obj, field)
        if not f:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(f.url) if request else f.url

    def get_photo_profil(self, obj):
        return self._image_url(obj, 'photo_profil')

    def get_carte_identite_recto(self, obj):
        return self._image_url(obj, 'carte_identite_recto')

    def get_carte_identite_verso(self, obj):
        return self._image_url(obj, 'carte_identite_verso')


class InscriptionSerializer(serializers.Serializer):
    """
    Inscription SANS KYC : seuls les champs d'identité, de contact et de
    parrainage sont demandés. Le KYC n'existe que via /programme-credit/.
    """
    prenom   = serializers.CharField(max_length=100)
    nom      = serializers.CharField(max_length=100)
    email    = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    telephone = serializers.CharField(max_length=20)
    adresse   = serializers.CharField(max_length=200)
    zone      = serializers.CharField(max_length=100, required=False, default='Lomé')
    personne_confiance_nom = serializers.CharField(max_length=100)
    personne_confiance_tel = serializers.CharField(max_length=20)
    code_parrain    = serializers.CharField(max_length=10, required=False, allow_blank=True)
    contrat_accepte = serializers.BooleanField()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_contrat_accepte(self, value):
        if not value:
            raise serializers.ValidationError("Vous devez accepter les conditions générales d'utilisation.")
        return value

    def validate_code_parrain(self, value):
        if value and not Membre.objects.filter(code_parrainage=value.upper()).exists():
            raise serializers.ValidationError("Code de parrainage invalide.")
        return value.upper() if value else value

    def create(self, validated_data):
        parrain = None
        code = validated_data.get('code_parrain')
        if code:
            parrain = Membre.objects.filter(code_parrainage=code).first()
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['prenom'],
            last_name=validated_data['nom'],
        )
        membre = Membre.objects.create(
            user=user, telephone=validated_data['telephone'],
            adresse=validated_data['adresse'], zone=validated_data.get('zone') or 'Lomé',
            parrain=parrain,
            personne_confiance_nom=validated_data['personne_confiance_nom'],
            personne_confiance_tel=validated_data['personne_confiance_tel'],
            contrat_accepte=True,
            # Pas de KYC ici — kyc_statut reste 'non_requis' (défaut du modèle).
        )
        return membre


class ProfilUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Membre
        fields = ['telephone', 'adresse', 'zone', 'personne_confiance_nom', 'personne_confiance_tel']


class ProgrammeCreditSerializer(serializers.ModelSerializer):
    """
    Seul point d'entrée du KYC dans l'API : soumission volontaire pour
    rejoindre le programme crédit (paiement par tranches).
    """
    class Meta:
        model  = Membre
        fields = ['photo_profil', 'carte_identite_recto', 'carte_identite_verso']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo_profil'].required = True
        self.fields['carte_identite_recto'].required = True
        self.fields['carte_identite_verso'].required = False

    def save(self, **kwargs):
        membre = super().save(**kwargs)
        membre.kyc_statut = 'en_attente'
        membre.save(update_fields=['kyc_statut'])
        return membre


# ── Produits ─────────────────────────────────────────────────────────────────
class ComposantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Composant
        fields = ['id', 'nom', 'emoji', 'ordre']


class PackSerializer(serializers.ModelSerializer):
    composants          = ComposantSerializer(source='composants_liste', many=True, read_only=True)
    prix_formate          = serializers.ReadOnlyField()
    acompte_estime         = serializers.ReadOnlyField()
    prix_comptant           = serializers.ReadOnlyField()
    prix_comptant_formate   = serializers.ReadOnlyField()
    lien_whatsapp_credit    = serializers.SerializerMethodField()
    lien_whatsapp_comptant  = serializers.SerializerMethodField()

    class Meta:
        model  = Pack
        fields = [
            'code', 'nom', 'prix', 'prix_formate', 'description', 'note_quantite',
            'couleur', 'disponible', 'acompte_estime', 'prix_comptant', 'prix_comptant_formate',
            'composants', 'lien_whatsapp_credit', 'lien_whatsapp_comptant',
        ]

    def get_lien_whatsapp_credit(self, obj):
        return obj.lien_whatsapp()

    def get_lien_whatsapp_comptant(self, obj):
        return obj.lien_whatsapp_comptant()


# ── Commandes ────────────────────────────────────────────────────────────────
class PaiementSerializer(serializers.ModelSerializer):
    mode_paiement_display = serializers.CharField(source='get_mode_paiement_display', read_only=True)

    class Meta:
        model  = Paiement
        fields = ['id', 'montant', 'date_paiement', 'mode_paiement', 'mode_paiement_display', 'note']


class CommandeSerializer(serializers.ModelSerializer):
    pack_code      = serializers.CharField(source='pack.code', read_only=True)
    pack_nom       = serializers.CharField(source='pack.nom', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    mode_commande_display = serializers.CharField(source='get_mode_commande_display', read_only=True)
    solde_restant   = serializers.ReadOnlyField()
    penalite_nette   = serializers.ReadOnlyField()
    est_en_retard     = serializers.ReadOnlyField()
    jours_retard       = serializers.ReadOnlyField()

    class Meta:
        model  = Commande
        fields = [
            'id', 'pack_code', 'pack_nom', 'quantite', 'montant_total', 'acompte_requis',
            'montant_verse', 'solde_restant', 'statut', 'statut_display',
            'mode_commande', 'mode_commande_display', 'date_commande', 'date_limite_solde',
            'penalite_nette', 'est_en_retard', 'jours_retard', 'note',
        ]


class CommandeDetailSerializer(CommandeSerializer):
    paiements = PaiementSerializer(many=True, read_only=True)

    class Meta(CommandeSerializer.Meta):
        fields = CommandeSerializer.Meta.fields + ['paiements']


# ── Réseau ───────────────────────────────────────────────────────────────────
class CommissionSerializer(serializers.ModelSerializer):
    pack_code      = serializers.CharField(source='commande.pack.code', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model  = Commission
        fields = ['id', 'montant', 'taux', 'statut', 'statut_display', 'date_calcul', 'date_versement', 'pack_code']


def serialize_arbre(node_list):
    """Sérialise récursivement la structure renvoyée par Membre.get_arbre_filleuls()."""
    result = []
    for node in node_list:
        m = node['membre']
        result.append({
            'id': m.id,
            'nom_complet': m.nom_complet,
            'code_parrainage': m.code_parrainage,
            'zone': m.zone,
            'date_inscription': m.date_inscription.isoformat(),
            'score_confiance': m.score_confiance,
            'kyc_statut': m.kyc_statut,
            'niveau': node['niveau'],
            'filleuls': serialize_arbre(node['filleuls']),
        })
    return result


# ── Partenaires ──────────────────────────────────────────────────────────────
class ProduitPartenaireSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model  = ProduitPartenaire
        fields = ['id', 'nom', 'description', 'prix', 'image', 'disponible']

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class CategoriePartenaireSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CategoriePartenaire
        fields = ['id', 'nom', 'slug', 'emoji']


class PartenaireSerializer(serializers.ModelSerializer):
    categorie   = CategoriePartenaireSerializer(read_only=True)
    logo         = serializers.SerializerMethodField()
    image_couverture = serializers.SerializerMethodField()
    whatsapp_url  = serializers.ReadOnlyField()

    class Meta:
        model  = Partenaire
        fields = [
            'id', 'nom', 'slogan', 'description', 'categorie', 'logo', 'image_couverture',
            'telephone', 'whatsapp', 'whatsapp_url', 'email', 'site_web', 'zone', 'adresse',
        ]

    def _image_url(self, obj, field):
        f = getattr(obj, field)
        if not f:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(f.url) if request else f.url

    def get_logo(self, obj):
        return self._image_url(obj, 'logo')

    def get_image_couverture(self, obj):
        return self._image_url(obj, 'image_couverture')


class PartenaireDetailSerializer(PartenaireSerializer):
    produits = ProduitPartenaireSerializer(many=True, read_only=True)

    class Meta(PartenaireSerializer.Meta):
        fields = PartenaireSerializer.Meta.fields + ['produits']
