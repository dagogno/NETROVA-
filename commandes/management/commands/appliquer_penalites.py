"""
Commande : python manage.py appliquer_penalites

À exécuter chaque jour (idéalement chaque matin) via cron ou un scheduler.

Cron Linux — exécution quotidienne à 8h00 :
    0 8 * * * /chemin/vers/venv/bin/python /chemin/vers/netrova_project/manage.py appliquer_penalites >> /var/log/netrova_penalites.log 2>&1

Windows Task Scheduler :
    Programme : C:\\chemin\\venv\\Scripts\\python.exe
    Arguments : C:\\chemin\\netrova_project\\manage.py appliquer_penalites
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from commandes.models import Commande


class Command(BaseCommand):
    help = "Calcule et applique les pénalités de retard sur toutes les commandes éligibles."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Simule l\'exécution sans modifier la base de données.')
        parser.add_argument('--membre', type=str,
                            help='Limiter à un membre spécifique (username).')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        maintenant = timezone.now()

        self.stdout.write(f"\n{'[DRY RUN] ' if dry_run else ''}=== Calcul des pénalités — {maintenant.strftime('%d/%m/%Y %H:%M')} ===\n")

        qs = Commande.objects.filter(
            statut__in=['acompte_paye', 'en_retard'],
            penalite_activee=True,
        ).select_related('membre__user', 'pack')

        if options.get('membre'):
            qs = qs.filter(membre__user__username=options['membre'])

        total_mises_a_jour = 0
        total_penalites    = 0

        for cmd in qs:
            if not cmd.est_en_retard:
                continue

            ancienne_penalite = cmd.penalite_totale
            nouvelle_penalite = int(
                max(0, cmd.montant_total - cmd.montant_verse)
                * float(cmd.penalite_taux)
                * cmd.jours_retard
            )

            if nouvelle_penalite == ancienne_penalite:
                continue

            self.stdout.write(
                f"  CMD-{cmd.pk:04d} | {cmd.membre.nom_complet:<25} | "
                f"+{cmd.jours_retard}j | {ancienne_penalite:,} F → {nouvelle_penalite:,} F"
                .replace(',', ' ')
            )

            if not dry_run:
                cmd.penalite_totale = nouvelle_penalite
                cmd.statut = 'en_retard'
                cmd.save(update_fields=['penalite_totale', 'statut'])

            total_mises_a_jour += 1
            total_penalites    += nouvelle_penalite

        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style(
            f"\n{'[DRY RUN] ' if dry_run else ''}"
            f"{total_mises_a_jour} commande(s) mise(s) à jour. "
            f"Total pénalités : {total_penalites:,} FCFA".replace(',', ' ')
        ))
