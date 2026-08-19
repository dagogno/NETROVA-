from django.db import models
from django.utils import timezone


class CategoriePartenaire(models.Model):
    nom   = models.CharField(max_length=80)
    slug  = models.SlugField(unique=True)
    emoji = models.CharField(max_length=5, default='🏢')
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Catégorie partenaire'
        verbose_name_plural = 'Catégories partenaires'
        ordering            = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class Partenaire(models.Model):
    STATUT_CHOICES = [
        ('actif',      'Actif ✅'),
        ('inactif',    'Inactif'),
        ('en_attente', 'En attente de validation'),
    ]
    PLAN_CHOICES = [
        ('starter',  'Starter — 5 000 FCFA/mois'),
        ('standard', 'Standard — 10 000 FCFA/mois'),
        ('premium',  'Premium — 20 000 FCFA/mois'),
    ]

    nom              = models.CharField(max_length=120)
    slogan           = models.CharField(max_length=200, blank=True)
    description      = models.TextField()
    categorie        = models.ForeignKey(CategoriePartenaire, null=True, blank=True,
                                         on_delete=models.SET_NULL, related_name='partenaires')
    logo             = models.ImageField(upload_to='partenaires/logos/', null=True, blank=True)
    image_couverture = models.ImageField(upload_to='partenaires/covers/', null=True, blank=True)
    telephone        = models.CharField(max_length=25)
    whatsapp         = models.CharField(max_length=25, blank=True)
    email            = models.EmailField(blank=True)
    site_web         = models.URLField(blank=True)
    zone             = models.CharField(max_length=100, default='Lomé')
    adresse          = models.CharField(max_length=200, blank=True)
    statut           = models.CharField(max_length=12, choices=STATUT_CHOICES, default='en_attente')
    plan             = models.CharField(max_length=12, choices=PLAN_CHOICES, default='starter')
    date_debut       = models.DateField(default=timezone.now)
    date_fin         = models.DateField(null=True, blank=True)
    note_admin       = models.TextField(blank=True)
    ordre_affichage  = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Partenaire'
        verbose_name_plural = 'Partenaires'
        ordering            = ['ordre_affichage', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.get_plan_display()})"

    @property
    def whatsapp_url(self):
        if self.whatsapp:
            return f"https://wa.me/{self.whatsapp.replace(' ', '').replace('+', '')}"
        return ''

    @property
    def est_actif(self):
        if self.statut != 'actif':
            return False
        if self.date_fin and self.date_fin < timezone.now().date():
            return False
        return True

    @property
    def tarif_mensuel(self):
        return {'starter': 5000, 'standard': 10000, 'premium': 20000}.get(self.plan, 5000)


class ProduitPartenaire(models.Model):
    partenaire  = models.ForeignKey(Partenaire, on_delete=models.CASCADE, related_name='produits')
    nom         = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix        = models.CharField(max_length=50, blank=True)
    image       = models.ImageField(upload_to='partenaires/produits/', null=True, blank=True)
    disponible  = models.BooleanField(default=True)
    ordre       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Produit partenaire'
        verbose_name_plural = 'Produits partenaires'
        ordering            = ['ordre', 'nom']

    def __str__(self):
        return f"{self.partenaire.nom} — {self.nom}"
