from django.db import models
from django.conf import settings
from urllib.parse import quote


class Pack(models.Model):
    CODE_CHOICES = [
        ('1A', 'Pack 1A'),
        ('2A', 'Pack 2A'),
        ('2B', 'Pack 2B'),
        ('3A', 'Pack 3A'),
        ('3B', 'Pack 3B'),
        ('4A', 'Pack 4A'),
        ('4B', 'Pack 4B'),
    ]
    COULEUR_CHOICES = [
        ('blue',    'Bleu'),
        ('green',   'Vert'),
        ('orange',  'Orange'),
        ('navy',    'Marine'),
        ('purple',  'Violet'),
        ('red',     'Rouge'),
        ('darkgreen','Vert foncé'),
    ]

    code         = models.CharField(max_length=5, choices=CODE_CHOICES, unique=True)
    nom          = models.CharField(max_length=100)
    prix         = models.PositiveIntegerField(help_text='Prix en FCFA')
    description  = models.TextField(blank=True)
    note_quantite = models.CharField(
        max_length=100, blank=True,
        help_text='Ex: "EN QUANTITÉ PLUS ÉLEVÉE" ou "GRANDE QUANTITÉ"'
    )
    couleur      = models.CharField(max_length=15, choices=COULEUR_CHOICES, default='blue')
    disponible   = models.BooleanField(default=True)
    ordre        = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Pack'
        verbose_name_plural = 'Packs'
        ordering            = ['ordre', 'prix']

    def __str__(self):
        return f"Pack {self.code} – {self.prix:,} FCFA".replace(',', ' ')

    @property
    def prix_formate(self):
        return f"{self.prix:,}".replace(',', ' ')

    @property
    def acompte_estime(self):
        return f"{(self.prix // 2):,}".replace(',', ' ')

    @property
    def composants_liste(self):
        return self.composants.filter(actif=True).order_by('ordre')

    def lien_whatsapp(self):
        numero = getattr(settings, 'NETROVA_WHATSAPP', '22890491287')
        message = f"Bonjour NETROVA, je souhaite commander le Pack {self.code} à {self.prix_formate} FCFA."
        return f"https://wa.me/{numero}?text={quote(message)}"


class Composant(models.Model):
    pack    = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='composants')
    nom     = models.CharField(max_length=100, help_text='Ex: Riz, Huile végétale (1L), Milo')
    emoji   = models.CharField(max_length=5, blank=True, help_text='Emoji représentatif')
    ordre   = models.PositiveSmallIntegerField(default=0)
    actif   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Composant'
        verbose_name_plural = 'Composants'
        ordering            = ['ordre']

    def __str__(self):
        return f"{self.pack.code} – {self.nom}"
