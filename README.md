<<<<<<< HEAD
# NETROVA – Site Web Communautaire

> Réseau de confiance et d'opportunités · Lomé, Togo

---

## 📋 Ce que contient ce projet

| Fonctionnalité | Description |
|---|---|
| Page d'accueil | Présentation, valeurs, packs, contact WhatsApp |
| Catalogue des packs | 7 packs avec bouton "Commander via WhatsApp" |
| Inscription / Connexion | Formulaire d'adhésion avec code de parrainage |
| Tableau de bord membre | Statistiques, commandes, filleuls, code parrainage |
| Suivi des commandes | Acompte, solde restant, pénalités de retard |
| Réseau & commissions | Filleuls, taux 2%/3%, historique |
| Administration | Interface admin pour gérer tout manuellement |

---

## 🖥️ Installation en local (étape par étape)

### Prérequis

- **Python 3.10+** installé sur votre machine
- **Git** (optionnel, pour cloner)
- Un terminal (CMD, PowerShell, ou Terminal)

Vérifiez votre version de Python :
```
python --version
```
ou
```
python3 --version
```

---

### Étape 1 — Décompresser le projet

Décompressez l'archive `netrova_project.zip` dans le dossier de votre choix.

```
# Exemple : dans votre bureau
C:\Users\VotreNom\Desktop\netrova_project\
```

---

### Étape 2 — Ouvrir un terminal dans le dossier

**Windows :**
- Ouvrez l'explorateur de fichiers dans le dossier `netrova_project`
- Cliquez dans la barre d'adresse, tapez `cmd`, appuyez sur Entrée

**Mac / Linux :**
```bash
cd ~/Desktop/netrova_project
```

---

### Étape 3 — Créer l'environnement virtuel

```bash
# Windows
python -m venv venv

# Mac / Linux
python3 -m venv venv
```

---

### Étape 4 — Activer l'environnement virtuel

```bash
# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate
```

✅ Vous verrez `(venv)` au début de votre ligne de commande.

---

### Étape 5 — Installer les dépendances

```bash
pip install -r requirements.txt
```

Cela installe : Django, whitenoise, python-decouple, Pillow, gunicorn.

---

### Étape 6 — Configurer le fichier .env

Copiez le fichier exemple :
```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Ouvrez `.env` avec un éditeur de texte et modifiez :
```
SECRET_KEY=mettez-une-longue-chaine-aleatoire-ici-ex-abc123xyz789
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
NETROVA_WHATSAPP=22890491287
```

> 💡 Pour générer une SECRET_KEY sécurisée, vous pouvez utiliser :
> `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

### Étape 7 — Créer la base de données

```bash
python manage.py migrate
```

---

### Étape 8 — Charger les packs NETROVA

```bash
python manage.py loaddata produits/fixtures/packs_initiaux.json
```

---

### Étape 9 — Créer le compte administrateur

```bash
python manage.py createsuperuser
```

Entrez un nom d'utilisateur, email, et mot de passe. Mémorisez-les !

---

### Étape 10 — Lancer le serveur

```bash
python manage.py runserver
```

---

### Étape 11 — Ouvrir le site dans votre navigateur

Ouvrez votre navigateur et allez à :

| Page | URL |
|---|---|
| **Site principal** | http://127.0.0.1:8000 |
| **Catalogue des packs** | http://127.0.0.1:8000/packs/ |
| **Inscription** | http://127.0.0.1:8000/membres/inscription/ |
| **Connexion** | http://127.0.0.1:8000/membres/connexion/ |
| **Administration** | http://127.0.0.1:8000/admin |

---

## 🔧 Script automatique (raccourci)

Si vous préférez, exécutez tout en une seule commande après l'étape 4 :

```bash
# Mac / Linux
bash setup.sh

# Windows — exécutez les commandes une par une (le .sh ne fonctionne pas sur CMD)
```

---

## 📁 Structure du projet

```
netrova_project/
├── manage.py                  ← Point d'entrée Django
├── .env                       ← Variables d'environnement (à créer)
├── .env.example               ← Modèle pour le .env
├── requirements.txt           ← Dépendances Python
├── setup.sh                   ← Script d'installation automatique
│
├── netrova/                   ← Configuration principale Django
│   ├── settings.py            ← Paramètres (base de données, apps...)
│   ├── urls.py                ← URLs principales
│   └── views.py               ← Vue de la page d'accueil
│
├── membres/                   ← App : gestion des membres
│   ├── models.py              ← Modèle Membre (profil, parrainage)
│   ├── views.py               ← Inscription, connexion, tableau de bord
│   ├── forms.py               ← Formulaires d'inscription et profil
│   ├── admin.py               ← Interface admin pour les membres
│   └── templates/membres/     ← HTML des pages membres
│
├── produits/                  ← App : catalogue des packs
│   ├── models.py              ← Modèles Pack et Composant
│   ├── admin.py               ← Gestion des packs dans l'admin
│   ├── fixtures/              ← Données initiales (7 packs)
│   └── templates/produits/    ← HTML catalogue et détail pack
│
├── commandes/                 ← App : commandes et paiements
│   ├── models.py              ← Commande, Paiement, calcul pénalités
│   ├── admin.py               ← Interface admin pour les commandes
│   └── templates/commandes/   ← HTML suivi commandes membre
│
├── reseau/                    ← App : parrainage et commissions
│   ├── models.py              ← Modèle Commission
│   ├── admin.py               ← Versement des commissions
│   └── templates/reseau/      ← HTML commissions membre
│
├── templates/                 ← Templates globaux
│   ├── base.html              ← Template de base (navbar, footer)
│   └── accueil.html           ← Page d'accueil
│
└── static/
    └── css/netrova.css        ← Toute la feuille de style
```

---

## 🛠️ Utilisation de l'administration

Allez sur http://127.0.0.1:8000/admin et connectez-vous avec votre superuser.

### Flux de travail quotidien (admin)

**Quand un client commande via WhatsApp :**
1. Allez dans **Commandes > Ajouter une commande**
2. Sélectionnez le membre (ou créez-le d'abord dans Membres)
3. Choisissez le pack et la quantité
4. Sauvegardez → l'acompte requis et la date limite sont calculés automatiquement

**Quand le client paie :**
1. Ouvrez la commande concernée
2. Dans la section **Paiements**, ajoutez le montant reçu
3. Sauvegardez → le statut se met à jour automatiquement

**Calculer les pénalités de retard :**
1. Dans la liste des commandes, sélectionnez les commandes en retard
2. Action : **"Calculer les pénalités de retard"**

**Verser les commissions :**
1. Allez dans **Réseau > Commissions**
2. Sélectionnez les commissions "En attente"
3. Action : **"Marquer comme versée(s)"**

---

## 🚀 Déploiement en production (plus tard)

Options d'hébergement dans votre budget (5–20€/mois) :

| Hébergeur | Prix | Notes |
|---|---|---|
| **Render.com** | Gratuit (750h/mois) | Très simple, supporte Django |
| **PythonAnywhere** | Gratuit (limité) | Idéal pour débuter |
| **OVH VPS** | ~4€/mois | Plus de contrôle |
| **Hetzner Cloud** | ~4€/mois | Excellent rapport qualité/prix |

Pour la production, pensez à :
- Changer `DEBUG=False` dans `.env`
- Configurer PostgreSQL à la place de SQLite
- Ajouter votre domaine dans `ALLOWED_HOSTS`

---

## ❓ Problèmes fréquents

**"python n'est pas reconnu"**
→ Essayez `python3` à la place de `python`

**"No module named django"**
→ L'environnement virtuel n'est pas activé. Refaites l'étape 4.

**Page blanche ou erreur 500**
→ Vérifiez que `DEBUG=True` dans votre `.env`
→ Consultez le terminal : Django affiche l'erreur précise

**"That port is already in use"**
→ Utilisez un autre port : `python manage.py runserver 8080`
→ Puis ouvrez http://127.0.0.1:8080

---

*NETROVA – Plus qu'un réseau, une famille ! 🌍*

---

## 🆕 Nouveautés V2

### Nouvelles fonctionnalités
- **KYC obligatoire à l'inscription** : photo de profil + pièce d'identité (recto/verso)
- **Score de confiance (0–100)** : calculé automatiquement selon paiements, retards, KYC, ancienneté
- **Arbre des filleuls** : page "Mon réseau" affiche vos filleuls, leurs filleuls, taille d'équipe totale
- **Hiérarchie admin** : `/membres-hierarchie/` — arbre complet de tous les membres pour l'admin
- **Modale conditions avant commande** : rappel acompte/solde/pénalités avant tout bouton "Commander"
- **Interface admin redessinée** : dashboard avec stats en temps réel, actions rapides, KYC en attente

### Nouvelles commandes
```bash
# Après avoir activé le venv
python manage.py makemigrations  # si vous modifiez les modèles
python manage.py migrate
```

### URLs ajoutées
| Page | URL |
|---|---|
| Hiérarchie réseau (admin) | http://127.0.0.1:8000/membres-hierarchie/ |
| Tableau de bord | http://127.0.0.1:8000/membres/tableau-de-bord/ |
| Mon réseau (arbre) | http://127.0.0.1:8000/membres/mon-reseau/ |
=======
# NETROVA-
>>>>>>> c1a914da955ee5b686e1b82b4e9c15b092bb2fa8
