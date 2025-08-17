# HIDS-Web

**HIDS-Web** est une interface web légère, packagée en Docker, pour piloter un système HIDS (Host-Based Intrusion Detection System).  
Il permet de configurer, lancer, arrêter et visualiser vos surveillances de fichiers, dossiers et adresses IP, le tout via un tableau de bord clair.

---

## 🚀 Fonctionnalités (MVP v2.0)

- Configuration des entités à surveiller (fichiers / dossiers / IP)  
- Statut en temps réel du moteur et de chaque type de monitoring  
- Dashboard graphique : cartes de statut, histogramme “Alerts by Type”, courbe “Alerts Over Time”  
- Flux d’activité et logs paginés  
- Génération de rapports (summary & detailed)  
- Authentification JWT avec rôles **admin** / **user**

---

## 📦 Architecture

- **Backend** : Python 3.10+, FastAPI, Celery (pour tâches asynchrones), JWT  
- **Base de données** : SQLite (pour le MVP) ou MongoDB  
- **Frontend** : React (Vite) + Tailwind CSS  
- **Packaging** : Docker Compose (backend, frontend, broker, DB)  

---

## ⚙️ Installation rapide

```bash
# Cloner le repo
git clone https://github.com/<ton-orga>/hids-web.git
cd hids-web

# Lancer les services
docker-compose up --build

# Le front est dispo sur http://localhost:3000
# L’API Swagger sur http://localhost:8000/docs
````

---

## 🔧 Configuration

* Copier `.env.example` en `.env` et renseigner :

  * `JWT_SECRET`
  * `DATABASE_URL`
  * (plus tard) `VIRUSTOTAL_API_KEY`

---

## 📅 Roadmap

| Version | Date cible | Feature principale                             |
| ------- | ---------- | ---------------------------------------------- |
| **2.0** | 2025-06-15 | MVP Web App (celui-ci)                         |
| **2.1** | 2025-07-15 | Intégration API VirusTotal                     |
| **2.2** | 2025-08-30 | Modèle ML de classification d’IP malveillantes |

---

## 🤝 Contribuer

1. Forker le projet
2. Créer une branche `feature/…`
3. Commit & PR en décrivant bien vos changements
4. Code review & merge

---

hello for Comit

## 📝 License

MIT © 2025 Ton Nom

# ---------------------------------
Parfait 👍 un **README complet** est essentiel pour ton projet.
Voici une version structurée, claire et adaptée à **HIDS 2.0**. Tu pourras l’ajouter directement à la racine du repo sous `README.md`.

---

# HIDS-Web 2.0

**Host Intrusion Detection System (HIDS) – Web API + Scheduler**
Un projet pédagogique de sécurité permettant de **surveiller fichiers, dossiers et adresses IP** avec une API web moderne basée sur **FastAPI**, **SQLAlchemy**, et **APScheduler**.

---

## 🚀 Fonctionnalités

* **Authentification JWT** (login avec admin/user)
* **CRUD Monitoring**

  * Fichiers
  * Dossiers
  * IPs
* **Planification automatique (scheduler)**

  * Fréquences configurables (`minutely`, `hourly`, `daily`)
  * Pause / reprise
  * Persistance au redémarrage
* **Tableau de bord API**

  * `/api/status` → état de l’application
  * `/api/metrics` → métriques (monitored, scheduler, events)
  * `/api/reports` → rapport JSON structuré
  * `/api/activity` → historique brut des exécutions
* **Sécurité**

  * Utilisateurs avec rôles (`admin`, `user`)
  * Hash des mots de passe avec `passlib[bcrypt]`
  * Protection des routes par `get_current_active_user`

---

## 📦 Prérequis

* Docker + Docker Compose
* Python 3.10+ (si exécution locale)
* PowerShell (scripts de test fournis)

---

## 🛠 Installation & Démarrage

### 1. Cloner le projet

```bash
git clone https://github.com/toncompte/HIDS2.0.git
cd HIDS2.0
```

### 2. Créer un fichier `.env`

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=supersecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Lancer avec Docker Compose

```bash
docker-compose up --build
```

API accessible sur [http://localhost:8000](http://localhost:8000)

---

## 🔑 Authentification

1. Crée un utilisateur admin via API `/users` ou migration initiale
2. Connecte-toi via :

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded
username=admin&password=secret
```

3. Récupère un `access_token` JWT pour accéder aux routes sécurisées.

---

## 📡 Endpoints principaux

### Status & Administration

* `GET /api/status` → état de l’application
* `GET /api/metrics` → métriques
* `GET /api/reports` → rapport JSON
* `GET /api/activity` → logs récents

### Monitoring (CRUD)

* `GET /api/monitoring/files`
* `POST /api/monitoring/files`
* `PUT /api/monitoring/files/{id}`
* `DELETE /api/monitoring/files/{id}`

Idem pour :

* `/api/monitoring/folders`
* `/api/monitoring/ips`

---

## 🧪 Tests (PowerShell)

Des scripts `.ps1` sont fournis pour tester étape par étape :

* `test1.ps1` → CRUD de base + auth
* `test-2-scheduler-wiring.ps1` → wiring scheduler
* `test-3-frequency-and-pause.ps1` → changement fréquence, pause/reprise
* `test-4-metrics.ps1` → endpoint `/api/metrics`
* `test-5-reports-json.ps1` → endpoint `/api/reports`
* `test-6-jobstore-persistence.ps1` → persistance jobs après redémarrage

Exemple :

```powershell
.\test1.ps1
```

---

## 📊 Exemple de sortie `/api/metrics`

```json
{
  "monitored": {
    "files": {"total":3,"active":3,"paused":0},
    "folders": {"total":0,"active":0,"paused":0},
    "ips": {"total":3,"active":3,"paused":0},
    "total": 6
  },
  "scheduler": {"file":3,"folder":0,"ip":3,"total":6},
  "events": {"count":12, "by_type":{"file_scan":7,"ip_scan":5}, "last":[]}
}
```

---

## 📂 Arborescence projet

```
HIDS2.0/
│   README.md
│   docker-compose.yml
│   requirements.txt
│
├── backend/
│   ├── app/
│   │   ├── api/              # routes FastAPI
│   │   ├── core/             # sécurité, scheduler
│   │   ├── db/               # modèles & session SQLAlchemy
│   │   ├── models/           # schémas Pydantic
│   │   └── services/         # logique CRUD & tâches scan
│   └── main.py               # entrée FastAPI
│
├── tests/
│   └── *.ps1                 # scripts PowerShell automatisés
```

---

## 🧑‍💻 Auteurs

Projet développé dans le cadre d’un apprentissage **EFREI – Cybersécurité & Cloud**.

---

👉 Voilà un **README professionnel, clair et exploitable**.
Veux-tu que je prépare aussi une **version courte (résumé 10 lignes)** pour GitHub (utile en description rapide), ou on garde la version complète uniquement ?
