from django.db import models
from django.utils import timezone
from decimal import Decimal


class Commission(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de versement'),
        ('versee',     'Versée'),
    ]

    membre        = models.ForeignKey(
        'membres.Membre', on_delete=models.PROTECT,
        related_name='commissions', verbose_name='Bénéficiaire'
    )
    commande      = models.OneToOneField(
        'commandes.Commande', on_delete=models.PROTECT,
        related_name='commission', verbose_name='Commande source'
    )
    taux          = models.DecimalField(max_digits=5, decimal_places=4, verbose_name='Taux')
    montant       = models.PositiveIntegerField(verbose_name='Montant (FCFA)')
    statut        = models.CharField(max_length=12, choices=STATUT_CHOICES, default='en_attente')
    date_calcul   = models.DateTimeField(default=timezone.now)
    date_versement = models.DateTimeField(null=True, blank=True)
    note          = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Commission'
        verbose_name_plural = 'Commissions'
        ordering            = ['-date_calcul']

    def __str__(self):
        return f"Commission {self.montant:,} FCFA → {self.membre.nom_complet}".replace(',', ' ')

    def verser(self, note=''):
        self.statut         = 'versee'
        self.date_versement = timezone.now()
        self.note           = note
        self.save(update_fields=['statut', 'date_versement', 'note'])
