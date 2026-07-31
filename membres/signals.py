"""
Signaux Django — App membres

Signal post_save sur User :
Quand un superuser/staff est créé via l'admin Django ou createsuperuser,
on lui crée automatiquement un profil Membre "admin" à compléter.
"""
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


@receiver(post_save, sender=User)
def creer_profil_membre_admin(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil Membre pour les staff/superusers.
    Les membres normaux créent leur profil via InscriptionForm.save()
    (qui appelle Membre.objects.create() directement).
    """
    if not created:
        return
    # Uniquement pour les comptes staff (admin Django)
    if not (instance.is_staff or instance.is_superuser):
        return
    # Ne pas créer si un profil existe déjà
    from membres.models import Membre
    if hasattr(instance, 'membre'):
        return
    Membre.objects.create(
        user=instance,
        telephone='À compléter',
        adresse='À compléter',
        zone='Lomé',
        personne_confiance_nom='Administrateur NETROVA',
        personne_confiance_tel='À compléter',
        contrat_accepte=True,
        kyc_statut='valide',   # Admin = vérifié d'office
        score_confiance=90,
        note_admin='Compte administrateur créé automatiquement.',
    )
