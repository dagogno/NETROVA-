import string, random
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


def generer_code_parrainage():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(chars, k=8))
        if not Membre.objects.filter(code_parrainage=code).exists():
            return code


class Membre(models.Model):
    STATUT_CHOICES = [
        ('actif',    'Actif'),
        ('inactif',  'Inactif'),
        ('suspendu', 'Suspendu'),
    ]
    KYC_CHOICES = [
        ('en_attente', 'En attente de vérification'),
        ('valide',     'Vérifié ✅'),
        ('rejete',     'Rejeté ❌'),
    ]

    user                   = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membre')
    telephone              = models.CharField(max_length=20)
    adresse                = models.CharField(max_length=200)
    zone                   = models.CharField(max_length=100, default='Lomé')
    parrain                = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='filleuls')
    personne_confiance_nom = models.CharField(max_length=100)
    personne_confiance_tel = models.CharField(max_length=20)
    code_parrainage        = models.CharField(max_length=10, unique=True, default=generer_code_parrainage)
    statut                 = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    contrat_accepte        = models.BooleanField(default=False)
    date_inscription       = models.DateTimeField(auto_now_add=True)
    # KYC
    photo_profil           = models.ImageField(upload_to='kyc/photos/', null=True, blank=True, verbose_name='Photo de profil')
    carte_identite_recto   = models.ImageField(upload_to='kyc/cni/', null=True, blank=True, verbose_name='CNI Recto')
    carte_identite_verso   = models.ImageField(upload_to='kyc/cni/', null=True, blank=True, verbose_name='CNI Verso (optionnel)')
    kyc_statut             = models.CharField(max_length=12, choices=KYC_CHOICES, default='en_attente', verbose_name='Statut KYC')
    kyc_note               = models.TextField(blank=True, verbose_name='Note KYC admin')
    # Score
    score_confiance        = models.PositiveSmallIntegerField(default=30, verbose_name='Score de confiance (/100)')
    note_admin             = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Membre'
        verbose_name_plural = 'Membres'
        ordering            = ['-date_inscription']

    def __str__(self):
        return f"{self.nom_complet} ({self.code_parrainage})"

    @property
    def nom_complet(self):
        return self.user.get_full_name() or self.user.username

    @property
    def nombre_filleuls(self):
        return self.filleuls.filter(statut='actif').count()

    @property
    def taille_equipe_totale(self):
        """Nombre total de descendants actifs (filleuls + filleuls de filleuls...)."""
        total = 0
        for f in self.filleuls.filter(statut='actif'):
            total += 1 + f.taille_equipe_totale
        return total

    @property
    def taux_commission(self):
        from django.conf import settings
        if self.nombre_filleuls >= getattr(settings, 'SEUIL_COMMISSION_SENIOR', 10):
            return getattr(settings, 'TAUX_COMMISSION_SENIOR', 0.03)
        return getattr(settings, 'TAUX_COMMISSION_BASE', 0.02)

    @property
    def solde_commissions(self):
        return self.commissions.filter(statut='en_attente').aggregate(
            total=models.Sum('montant'))['total'] or 0

    @property
    def commissions_versees(self):
        return self.commissions.filter(statut='versee').aggregate(
            total=models.Sum('montant'))['total'] or 0

    def calculer_score(self):
        """Recalcule le score de confiance dynamiquement."""
        score = 30  # Base

        # KYC
        if self.kyc_statut == 'valide':
            score += 25
        elif self.kyc_statut == 'rejete':
            score -= 10

        # Commandes soldées dans les délais
        cmds_soldees_temps = self.commandes.filter(statut='soldee', penalite_totale=0).count()
        score += min(cmds_soldees_temps * 8, 24)

        # Commandes en retard
        cmds_retard = self.commandes.filter(statut='en_retard').count()
        score -= cmds_retard * 8

        # Pénalités
        cmds_penalites = self.commandes.filter(penalite_totale__gt=0).count()
        score -= cmds_penalites * 5

        # Filleuls actifs
        score += min(self.nombre_filleuls * 3, 15)

        # Ancienneté
        jours = (timezone.now() - self.date_inscription).days
        if jours > 180:
            score += 6

        return max(0, min(100, score))

    def get_score_label(self):
        s = self.score_confiance
        if s >= 80: return ('Excellent', 'green')
        if s >= 60: return ('Bon', 'blue')
        if s >= 40: return ('Moyen', 'orange')
        return ('Faible', 'red')

    def get_arbre_filleuls(self, profondeur=3, niveau=0):
        """Retourne l'arbre récursif des filleuls jusqu'à la profondeur donnée."""
        if niveau >= profondeur:
            return []
        filleuls = []
        for f in self.filleuls.filter(statut='actif').select_related('user').order_by('-date_inscription'):
            filleuls.append({
                'membre':   f,
                'niveau':   niveau + 1,
                'filleuls': f.get_arbre_filleuls(profondeur, niveau + 1),
            })
        return filleuls
