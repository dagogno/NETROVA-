#!/bin/bash
# ============================================================
#  NETROVA – Script d'installation automatique
#  Usage : bash setup.sh
# ============================================================
set -e
echo ""
echo "=========================================="
echo "  🚀 Installation de NETROVA"
echo "=========================================="
echo ""

# 1. Copier le fichier .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅  Fichier .env créé depuis .env.example"
  echo "⚠️   Pensez à modifier la SECRET_KEY dans .env !"
else
  echo "✅  Fichier .env déjà présent"
fi

# 2. Installer les dépendances
echo ""
echo "📦  Installation des dépendances Python..."
pip install -r requirements.txt

# 3. Migrations
echo ""
echo "🗄️   Création de la base de données..."
python manage.py migrate

# 4. Charger les données initiales (packs)
echo ""
echo "📦  Chargement des packs NETROVA..."
python manage.py loaddata produits/fixtures/packs_initiaux.json

# 5. Créer le superutilisateur
echo ""
echo "👤  Création du compte administrateur..."
echo "    (vous pouvez appuyer sur Entrée pour les champs optionnels)"
python manage.py createsuperuser

# 6. Collecter les fichiers statiques
echo ""
echo "📁  Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "  ✅  Installation terminée !"
echo "=========================================="
echo ""
echo "  Pour lancer le site :"
echo "  → python manage.py runserver"
echo "  → Ouvrir http://127.0.0.1:8000 dans votre navigateur"
echo ""
echo "  Administration :"
echo "  → http://127.0.0.1:8000/admin"
echo "=========================================="

# Charger les catégories partenaires
echo "🏢 Création des catégories partenaires..."
python manage.py shell -c "
from partenaires.models import CategoriePartenaire
cats = [('alimentaire','Alimentation & Épicerie','🛒',1),('sante','Santé & Beauté','💊',2),('mode','Mode & Vêtements','👗',3),('tech','Technologie & Services','📱',4),('artisanat','Artisanat & Création','🎨',5),('restauration','Restauration & Traiteur','🍽️',6),('transport','Transport & Livraison','🛵',7),('education','Formation & Éducation','📚',8)]
for slug,nom,emoji,ordre in cats:
    CategoriePartenaire.objects.get_or_create(slug=slug, defaults={'nom':nom,'emoji':emoji,'ordre':ordre})
print(f'  {CategoriePartenaire.objects.count()} catégories OK')
"
