from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Membre

# ─── Conditions générales officielles NETROVA ────────────────────────────────
CONDITIONS_TEXT = """
CONDITIONS GÉNÉRALES D'UTILISATION DE NETROVA

1. PRÉSENTATION
NETROVA est un réseau communautaire qui facilite l'accès à des produits, services
et opportunités économiques pour ses membres.
L'inscription est gratuite et ouverte à toute personne respectant les présentes conditions.

2. ADHÉSION
Pour devenir membre, l'utilisateur doit :
  • Fournir des informations exactes
  • Disposer d'un numéro de téléphone valide
  • Accepter les règles de fonctionnement de NETROVA
  • Respecter les autres membres et partenaires
NETROVA se réserve le droit de refuser ou suspendre toute inscription en cas
d'informations inexactes ou de comportement inapproprié.

3. SERVICES DISPONIBLES
Selon les programmes disponibles, les membres peuvent bénéficier :
  • De packs alimentaires
  • De services de mise en relation
  • D'opportunités économiques
  • D'offres promotionnelles
  • De programmes de paiement comptant ou à crédit

4. RÈGLES DU PROGRAMME PACKS ALIMENTAIRES

  Paiement Comptant
  Le membre peut commander et payer intégralement son pack avant livraison.
  Les commandes payées comptant peuvent bénéficier d'avantages spécifiques.

  Paiement à Crédit
  Le paiement à crédit n'est pas automatique.
  NETROVA se réserve le droit d'accepter ou de refuser une demande de crédit.
  Pour bénéficier d'un crédit, le membre peut être invité à fournir :
    - Sa localisation
    - Un contact de confiance
    - Des informations complémentaires permettant d'évaluer sa fiabilité

  Conditions du Crédit
  Lorsque le crédit est accordé :
    - Le membre verse un acompte de 50%
    - NETROVA livre le pack
    - Le solde doit être payé dans le délai indiqué lors de la commande

  Retard de Paiement
  En cas de retard :
    - Des pénalités peuvent être appliquées
    - L'accès futur au crédit peut être suspendu
    - Le compte du membre peut être limité ou fermé

5. RESPONSABILITÉS DES MEMBRES
Chaque membre s'engage à :
  • Fournir des informations exactes
  • Respecter les délais de paiement
  • Utiliser les services de manière honnête
  • Ne pas nuire à l'image de NETROVA
  • Respecter les lois en vigueur
Toute tentative de fraude peut entraîner une exclusion définitive.

6. POLITIQUE DE CONFIDENTIALITÉ
NETROVA peut collecter : nom, prénom, téléphone, adresse/localisation,
historique des commandes et informations liées au paiement.
Ces informations servent uniquement à gérer les commandes, assurer les livraisons,
fournir les services demandés, améliorer le fonctionnement du réseau et sécuriser
les transactions. Elles ne sont ni vendues ni partagées à des tiers sans autorisation,
sauf obligation légale.

7. LIMITATION DE RESPONSABILITÉ
NETROVA met tout en œuvre pour fournir ses services dans les meilleures conditions.
Toutefois, NETROVA ne peut être tenue responsable des retards indépendants de sa volonté,
des problèmes liés aux réseaux téléphoniques, ni des informations inexactes fournies
par les utilisateurs.
"""
# ─────────────────────────────────────────────────────────────────────────────


class InscriptionForm(forms.Form):
    # Compte
    prenom    = forms.CharField(max_length=50, label='Prénom *')
    nom       = forms.CharField(max_length=50, label='Nom *')
    email     = forms.EmailField(label='Email *')
    username  = forms.CharField(max_length=30, label="Nom d'utilisateur *")
    password1 = forms.CharField(widget=forms.PasswordInput, label='Mot de passe *')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirmer *')
    # Coordonnées
    telephone = forms.CharField(max_length=20, label='Téléphone *')
    adresse   = forms.CharField(max_length=200, label='Adresse *')
    zone      = forms.CharField(max_length=100, initial='Lomé', label='Zone / Quartier *')
    # Parrainage
    code_parrain = forms.CharField(max_length=10, required=False, label='Code de parrainage')
    # Personne de confiance
    personne_confiance_nom = forms.CharField(max_length=100, label='Nom complet *')
    personne_confiance_tel = forms.CharField(max_length=20, label='Téléphone *')
    # KYC - obligatoire
    photo_profil         = forms.ImageField(label='Photo de profil * (selfie clair)', help_text='Photo nette de votre visage')
    carte_identite_recto = forms.ImageField(label="CNI / Passeport Recto *", help_text="Pièce d'identité officielle en cours de validité")
    carte_identite_verso = forms.ImageField(required=False, label='CNI Verso (optionnel)')
    # Contrat
    contrat_accepte = forms.BooleanField(required=True, label="J'ai lu et j'accepte les conditions d'adhésion NETROVA.")

    def clean_username(self):
        u = self.cleaned_data['username']
        if User.objects.filter(username=u).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return u

    def clean_email(self):
        e = self.cleaned_data['email']
        if User.objects.filter(email=e).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return e

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        if len(p1) < 8:
            raise forms.ValidationError("Minimum 8 caractères.")
        return p2

    def clean_code_parrain(self):
        code = self.cleaned_data.get('code_parrain', '').strip().upper()
        if code:
            if not Membre.objects.filter(code_parrainage=code, statut='actif').exists():
                raise forms.ValidationError("Code de parrainage invalide ou inactif.")
        return code

    def save(self):
        d = self.cleaned_data
        user = User.objects.create_user(
            username=d['username'], email=d['email'], password=d['password1'],
            first_name=d['prenom'], last_name=d['nom'])
        parrain = None
        if d.get('code_parrain'):
            parrain = Membre.objects.get(code_parrainage=d['code_parrain'])
        membre = Membre.objects.create(
            user=user, telephone=d['telephone'], adresse=d['adresse'], zone=d['zone'],
            parrain=parrain, personne_confiance_nom=d['personne_confiance_nom'],
            personne_confiance_tel=d['personne_confiance_tel'],
            photo_profil=d.get('photo_profil'), carte_identite_recto=d['carte_identite_recto'],
            carte_identite_verso=d.get('carte_identite_verso'), contrat_accepte=True,
        )
        return membre


class ConnexionForm(AuthenticationForm):
    pass


class ProfilForm(forms.ModelForm):
    prenom = forms.CharField(max_length=50, label='Prénom')
    nom    = forms.CharField(max_length=50, label='Nom')
    email  = forms.EmailField(label='Email')

    class Meta:
        model  = Membre
        fields = ['telephone', 'adresse', 'zone', 'personne_confiance_nom',
                  'personne_confiance_tel', 'photo_profil', 'carte_identite_recto', 'carte_identite_verso']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            u = self.instance.user
            self.fields['prenom'].initial = u.first_name
            self.fields['nom'].initial    = u.last_name
            self.fields['email'].initial  = u.email

    def save(self, commit=True):
        membre = super().save(commit=False)
        u = membre.user
        u.first_name = self.cleaned_data['prenom']
        u.last_name  = self.cleaned_data['nom']
        u.email      = self.cleaned_data['email']
        if commit:
            u.save(); membre.save()
        return membre
