from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import datetime


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente',   'En attente'),
        ('acompte_paye', 'Acompte payé'),
        ('soldee',       'Soldée'),
        ('annulee',      'Annulée'),
        ('en_retard',    'En retard'),
    ]
    MODE_PAIEMENT_CHOICES = [
        ('credit',  'À crédit (acompte 50%)'),
        ('cash',    'Comptant (paiement total)'),
    ]

    membre          = models.ForeignKey('membres.Membre', on_delete=models.PROTECT, related_name='commandes')
    pack            = models.ForeignKey('produits.Pack', on_delete=models.PROTECT, related_name='commandes')
    quantite        = models.PositiveSmallIntegerField(default=1)
    montant_total   = models.PositiveIntegerField()
    acompte_requis  = models.PositiveIntegerField()
    montant_verse   = models.PositiveIntegerField(default=0)
    statut          = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    mode_commande   = models.CharField(max_length=10, choices=MODE_PAIEMENT_CHOICES,
                                       default='credit', verbose_name='Mode de paiement')
    date_commande   = models.DateTimeField(default=timezone.now)
    date_limite_solde = models.DateField(null=True, blank=True)

    # ── Pénalités ──────────────────────────────────────────────────────────
    penalite_activee    = models.BooleanField(default=True,
        verbose_name='Pénalités activées',
        help_text='Décochez pour suspendre les pénalités sur cette commande.')
    penalite_taux       = models.DecimalField(max_digits=5, decimal_places=4,
        default=Decimal('0.0100'),
        verbose_name='Taux pénalité/jour',
        help_text='Ex: 0.01 = 1% par jour. Modifiable par commande.')
    penalite_totale     = models.PositiveIntegerField(default=0,
        verbose_name='Pénalités cumulées (FCFA)')
    penalite_remisee    = models.PositiveIntegerField(default=0,
        verbose_name='Remise accordée sur pénalités (FCFA)',
        help_text='Montant de pénalités effacé manuellement par l\'admin.')
    penalite_note_admin = models.TextField(blank=True,
        verbose_name='Note admin (pénalités)',
        help_text='Raison d\'une remise ou modification de pénalité.')
    # ───────────────────────────────────────────────────────────────────────

    commission_calculee = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering            = ['-date_commande']

    def __str__(self):
        return f"CMD-{self.pk:04d} | {self.membre.nom_complet} | {self.pack}"

    def save(self, *args, **kwargs):
        if not self.montant_total:
            self.montant_total = self.pack.prix * self.quantite
        if self.mode_commande == 'cash':
            # Achat comptant : acompte = 100%, pas de délai de solde
            self.acompte_requis = self.montant_total
        elif not self.acompte_requis:
            self.acompte_requis = self.montant_total // 2
        if not self.date_limite_solde and self.mode_commande == 'credit':
            d = self.date_commande.date() if hasattr(self.date_commande, 'date') else self.date_commande
            jours = getattr(settings, 'DELAI_SOLDE_JOURS', 30)
            self.date_limite_solde = d + datetime.timedelta(days=jours)
        super().save(*args, **kwargs)

    # ── Propriétés calculées ───────────────────────────────────────────────
    @property
    def penalite_nette(self):
        """Pénalité réelle due = cumulée - remise admin."""
        return max(0, self.penalite_totale - self.penalite_remisee)

    @property
    def solde_restant(self):
        return max(0, self.montant_total + self.penalite_nette - self.montant_verse)

    @property
    def est_en_retard(self):
        if self.statut in ('soldee', 'annulee'):
            return False
        if self.date_limite_solde:
            return timezone.now().date() > self.date_limite_solde
        return False

    @property
    def jours_retard(self):
        if self.est_en_retard:
            return (timezone.now().date() - self.date_limite_solde).days
        return 0

    # ── Actions pénalités ─────────────────────────────────────────────────
    def calculer_penalite(self, save=True):
        """
        Calcule et applique la pénalité de retard.
        Respecte penalite_activee et penalite_taux par commande.
        Appelé par le cron quotidien ET manuellement depuis l'admin.
        """
        if not self.penalite_activee:
            return 0
        if not self.est_en_retard:
            return 0
        solde_base = max(0, self.montant_total - self.montant_verse)
        penalite   = int(solde_base * float(self.penalite_taux) * self.jours_retard)
        self.penalite_totale = penalite
        self.statut = 'en_retard'
        if save:
            self.save(update_fields=['penalite_totale', 'statut'])
        return penalite

    def accorder_remise(self, montant, note='', save=True):
        """Admin accorde une remise (partielle ou totale) sur les pénalités."""
        self.penalite_remisee = min(montant, self.penalite_totale)
        if note:
            self.penalite_note_admin = note
        if save:
            self.save(update_fields=['penalite_remisee', 'penalite_note_admin'])

    def effacer_penalites(self, note='', save=True):
        """Admin efface toutes les pénalités (remise à 100%)."""
        self.penalite_remisee    = self.penalite_totale
        self.penalite_note_admin = note or 'Pénalités effacées par l\'administrateur.'
        if save:
            self.save(update_fields=['penalite_remisee', 'penalite_note_admin'])

    def suspendre_penalites(self, note='', save=True):
        """Admin désactive les futures pénalités sur cette commande."""
        self.penalite_activee    = False
        self.penalite_note_admin = note or 'Pénalités suspendues par l\'administrateur.'
        if save:
            self.save(update_fields=['penalite_activee', 'penalite_note_admin'])

    # ── Paiements ─────────────────────────────────────────────────────────
    def enregistrer_paiement(self, montant, mode='especes', note=''):
        paiement = Paiement.objects.create(commande=self, montant=montant,
                                           mode_paiement=mode, note=note)
        self.montant_verse = sum(self.paiements.values_list('montant', flat=True))
        if self.montant_verse >= self.acompte_requis and self.statut == 'en_attente':
            self.statut = 'acompte_paye'
        if self.montant_verse >= (self.montant_total + self.penalite_nette):
            self.statut = 'soldee'
            self._declencher_commission()
        self.save(update_fields=['montant_verse', 'statut'])
        return paiement

    def _declencher_commission(self):
        if self.commission_calculee:
            return
        parrain = self.membre.parrain
        if not parrain:
            return
        from reseau.models import Commission
        taux    = Decimal(str(parrain.taux_commission))
        montant = int(self.montant_total * taux)
        Commission.objects.create(membre=parrain, commande=self, taux=taux, montant=montant)
        self.commission_calculee = True
        self.save(update_fields=['commission_calculee'])


class Paiement(models.Model):
    MODE_CHOICES = [
        ('especes',      'Espèces'),
        ('mobile_money', 'Mobile Money (Flooz/TMoney)'),
        ('virement',     'Virement bancaire'),
    ]
    commande       = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='paiements')
    montant        = models.PositiveIntegerField()
    date_paiement  = models.DateTimeField(default=timezone.now)
    mode_paiement  = models.CharField(max_length=15, choices=MODE_CHOICES, default='especes')
    note           = models.TextField(blank=True)
    enregistre_par = models.ForeignKey('auth.User', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='paiements_enregistres')

    class Meta:
        verbose_name        = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering            = ['-date_paiement']

    def __str__(self):
        return f"Paiement {self.montant:,} FCFA — CMD-{self.commande.pk:04d}".replace(',', ' ')
