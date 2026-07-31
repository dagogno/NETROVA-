"""
Commande : python manage.py creer_profil_membre

Crée un profil Membre pour tout utilisateur Django qui n'en a pas encore
(typiquement le superuser créé via 'createsuperuser').

Usage :
    python manage.py creer_profil_membre                    # interactif
    python manage.py creer_profil_membre --username admin   # ciblé
    python manage.py creer_profil_membre --all              # tous les users sans profil
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from membres.models import Membre


class Command(BaseCommand):
    help = "Crée un profil Membre pour les utilisateurs qui n'en ont pas"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--username', type=str, help='Nom d\'utilisateur ciblé')
        group.add_argument('--all', action='store_true', help='Traiter tous les users sans profil')

    def handle(self, *args, **options):
        if options['all']:
            users_sans_profil = [u for u in User.objects.all() if not hasattr(u, 'membre')]
        else:
            try:
                u = User.objects.get(username=options['username'])
                users_sans_profil = [u] if not hasattr(u, 'membre') else []
                if not users_sans_profil:
                    self.stdout.write(self.style.WARNING(
                        f"L'utilisateur '{options['username']}' a déjà un profil Membre."
                    ))
                    return
            except User.DoesNotExist:
                self.stderr.write(f"Utilisateur '{options['username']}' introuvable.")
                return

        if not users_sans_profil:
            self.stdout.write(self.style.SUCCESS("✅ Tous les utilisateurs ont déjà un profil Membre."))
            return

        for user in users_sans_profil:
            self.stdout.write(f"\nCréation du profil pour : {user.username} ({user.email})")

            tel = input("  Téléphone (ex: +228 90 00 00 00) : ").strip() or "+228 00000000"
            adresse = input("  Adresse : ").strip() or "Lomé, Togo"
            zone = input("  Zone/Quartier [Lomé] : ").strip() or "Lomé"
            pc_nom = input("  Personne de confiance (nom) : ").strip() or "Administrateur"
            pc_tel = input("  Personne de confiance (téléphone) : ").strip() or tel

            membre = Membre.objects.create(
                user=user,
                telephone=tel,
                adresse=adresse,
                zone=zone,
                personne_confiance_nom=pc_nom,
                personne_confiance_tel=pc_tel,
                contrat_accepte=True,
                kyc_statut='valide',      # admin considéré vérifié d'office
                score_confiance=80,
            )

            self.stdout.write(self.style.SUCCESS(
                f"  ✅ Profil créé — Code parrainage : {membre.code_parrainage}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ {len(users_sans_profil)} profil(s) Membre créé(s)."
        ))
