# SenTrans - Système de Réservation de Transport

## Architecture du Projet

Le projet SenTrans est une application Django qui offre une API REST pour un système de réservation de transport au Sénégal. L'application permet aux utilisateurs de réserver des places sur des trajets proposés par différentes compagnies de transport.

### Structure des Dossiers

```
django/
├── api/                  # API REST
│   ├── serializers.py    # Sérialiseurs pour les modèles
│   ├── views.py          # Vues et ViewSets
│   ├── urls.py           # Configuration des routes d'API
│   └── permissions.py    # Gestion des permissions
├── apps/                 # Applications Django
│   ├── users/            # Gestion des utilisateurs
│   ├── compagnies/       # Compagnies de transport
│   ├── conducteurs/      # Conducteurs de véhicules
│   ├── vehicules/        # Gestion des véhicules
│   ├── trajets/          # Trajets disponibles
│   ├── reservations/     # Réservations des utilisateurs
│   ├── paiements/        # Gestion des paiements
│   └── core/             # Fonctionnalités communes
├── templates/            # Templates HTML
├── static/               # Fichiers statiques
├── media/                # Fichiers média uploadés
└── config/               # Configuration du projet
```

## Modèles de Données

### Utilisateurs (User)
- Système d'authentification personnalisé
- Rôles: Admin, Agent, Voyageur, Conducteur
- Informations personnelles: nom, prénom, sexe, téléphone, email, photo de profil

### Compagnies de Transport (CompagnieTransport)
- Informations de la compagnie: nom, adresse, téléphone, email, logo
- Responsable lié à un utilisateur
- Statut actif/inactif

### Agents de Compagnie (AgentCompagnie)
- Liés à un utilisateur et à une compagnie
- Gestion des trajets et réservations pour leur compagnie

### Conducteurs (Conducteur)
- Liés à un utilisateur et à une compagnie
- Responsables de la conduite des véhicules

### Véhicules (Vehicule)
- Appartiennent à une compagnie
- Informations: modèle, immatriculation, capacité, type, etc.

### Trajets (Trajet)
- Associés à un véhicule et un conducteur
- Informations: villes de départ/arrivée, dates, prix, nombre de places
- Statut: Programmé, En cours, Terminé, Annulé
- Suivi en temps réel (coordonnées GPS)

### Réservations (Reservation)
- Lient un utilisateur à un trajet
- Nombre de places réservées
- Code de réservation unique
- Statut: Confirmée, Annulée, En attente, Terminée

### Paiements (Paiement)
- Liés à une réservation
- Informations sur la transaction: montant, méthode, référence, etc.

## API REST

L'API suit l'architecture RESTful et utilise Django REST Framework.

### Points d'accès principaux:

- `/api/login/` - Authentification (email/téléphone + mot de passe)
- `/api/register/` - Inscription des utilisateurs
- `/api/token/` - Obtention de tokens JWT
- `/api/token/refresh/` - Rafraîchissement des tokens JWT
- `/api/users/` - Gestion des utilisateurs
- `/api/compagnies/` - Gestion des compagnies
- `/api/agents/` - Gestion des agents
- `/api/conducteurs/` - Gestion des conducteurs
- `/api/vehicules/` - Gestion des véhicules
- `/api/trajets/` - Gestion des trajets
- `/api/reservations/` - Gestion des réservations
- `/api/paiements/` - Gestion des paiements

### Fonctionnalités Spéciales:

- `/api/users/me/` - Profil de l'utilisateur connecté
- `/api/users/change_password/` - Changement de mot de passe
- `/api/compagnies/{id}/vehicules/` - Véhicules d'une compagnie
- `/api/compagnies/{id}/conducteurs/` - Conducteurs d'une compagnie
- `/api/compagnies/{id}/trajets/` - Trajets d'une compagnie
- `/api/trajets/{id}/reservations/` - Réservations pour un trajet
- `/api/trajets/{id}/update_position/` - Mise à jour de la position d'un trajet
- `/api/reservations/{id}/paiement/` - Paiement associé à une réservation

## Système de Permissions

L'API utilise un système de permissions basé sur les rôles:

- Administrateurs: accès complet au système
- Agents de compagnie: gestion des trajets et réservations de leur compagnie
- Conducteurs: mise à jour des informations de trajets
- Voyageurs: réservation de trajets et gestion de leurs propres réservations

python -m pip install --upgrade pip setuptools wheel


## Technologies Utilisées

- Django 4.x
- Django REST Framework
- JWT pour l'authentification
- Base de données SQLite (en développement)
