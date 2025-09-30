# HIDS-Web 2.0

**Host Intrusion Detection System – local-first avec interface web.**
Surveille **fichiers**, **dossiers** et **adresses IP**, planifie des scans, centralise les **logs** et expose une **API FastAPI**. Frontend React (Vite + Tailwind) pour piloter le tout.

---

## 🚀 Fonctionnalités (MVP)

* Authentification **JWT** (rôles *admin* / *user*)
* CRUD de surveillance : **files**, **folders**, **IPs**
  Fréquences : `minutely | hourly | daily | weekly` + statut `active | paused`
* **Scheduler** (jobs persistants) et **logs** applicatifs (fichier)
* **Reports** (base JSON, extension HTML/PDF prévue), métriques & statut
* Intégrations (ex. VirusTotal, webhooks) & réglages “admin-only”

---

## 🧱 Architecture

**Backend** (FastAPI, SQLAlchemy, Pydantic v1, SQLite)

```
backend/app/
  api/        # routes REST (auth, users, monitoring, ...)
  core/       # config .env, sécurité JWT, logging, scheduler
  db/         # ORM (models.py), session (SessionLocal)
  models/     # schémas Pydantic (I/O)
  services/   # logique métier (users, monitoring, reports, scans)
  main.py     # entrée FastAPI
```

**Frontend** (React + Vite + Tailwind)

```
hids-web/
  src/pages/        # Dashboard, Surveillance, AlertsLogs, Reports, Settings
  src/components/   # Sidebar, Topbar, Table, Modals, ...
  src/context/      # AuthProvider
  lib/api.js        # appels API
```

**Données & logs**

```
data/   -> SQLite (hids.db), jobstore (jobs.db)
logs/   -> hids.log (+ rotation)
```

---

## 🗂️ Arborescence (extrait)

```
README.md
docker-compose.yml
data/             hids.db, jobs.db
logs/             hids.log, alerts.log
backend/
  Dockerfile
  app/
    api/          activity.py, alerts.py, auth.py, ... , users.py, monitoring.py
    core/         config.py, logging.py, scheduler.py, security.py
    db/           base.py, models.py, session.py
    models/       auth.py, user.py, monitoring.py, alerts.py, report.py
    services/     auth_service.py, user_service.py, monitoring_service.py, ...
    scripts/      seed_demo.py
    main.py
  requirements.txt
hids-web/
  src/
    pages/        Dashboard.jsx, Surveillance.jsx, AlertsLogs.jsx, Reports.jsx, Settings.jsx
    components/   Sidebar.jsx, Topbar.jsx, Table.jsx, ...
    context/      AuthProvider.jsx
    lib/          api.js
  vite.config.js, tailwind.config.js
```

---

## ⚙️ Configuration

Crée un fichier **`.env`** à la racine (ou dans `backend/` selon ton usage Docker) :

```env
APP_NAME=HIDS-Web API
JWT_SECRET=change_me_strong_secret
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///data/hids.db
```

> Volumes montés par `docker-compose.yml` : `./data:/app/data` et `./logs:/app/logs`.

---

## ▶️ Démarrage rapide (Docker)

```bash
# build + run API
docker compose up -d --build
# logs temps réel
docker compose logs -f api
# Swagger UI
# -> http://localhost:8000/docs
```

### Créer un **admin initial** (inside container)

```bash
docker compose exec -it api python - <<'PY'
from app.services.user_service import create_user
from app.models.user import UserCreate
u = create_user(UserCreate(
    username="admin_Hids",
    email="admin@local",
    password="ChangeMe!42",
    is_admin=True
))
print("Admin created:", u.username, u.id)
PY
```

### Obtenir un **token JWT**

> L’endpoint suit le flux OAuth2 « password », donc **x-www-form-urlencoded**.

```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin_Hids&password=ChangeMe!42"
# {"access_token":"...","token_type":"bearer"}
```

Exporter le token :

```bash
export TOKEN="<colle_ici_le_access_token>"
```

---

## 🔌 API – commandes utiles (CLI)

### Profil

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/me
```

### Users (admin only)

```bash
# créer
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@x.y","password":"Pwd!1234","is_admin":false}'

# lister / détail / update / delete
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/2
curl -X PUT http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"alice2","email":"a2@x.y","is_admin":false}'
curl -X PUT http://localhost:8000/api/users/2/password \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"new_password":"NewPwd!1234"}'
curl -X DELETE http://localhost:8000/api/users/2 -H "Authorization: Bearer $TOKEN"
```

### Monitoring – Files / Folders / IPs

```bash
# Files
curl -X POST http://localhost:8000/api/monitoring/files \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"path":"/tmp/foo","frequency":"hourly"}'
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/monitoring/files
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/monitoring/files/1
curl -X PUT http://localhost:8000/api/monitoring/files/1 \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"path":"/tmp/bar","frequency":"daily"}'
curl -X DELETE http://localhost:8000/api/monitoring/files/1 -H "Authorization: Bearer $TOKEN"

# Folders
curl -X POST http://localhost:8000/api/monitoring/folders \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"path":"/var/log","frequency":"weekly"}'
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/monitoring/folders

# IPs
curl -X POST http://localhost:8000/api/monitoring/ips \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"ip":"8.8.4.4","hostname":"dns4","frequency":"hourly"}'
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/monitoring/ips
```

### Statut / métriques / reports

```bash
curl http://localhost:8000/api/status
curl http://localhost:8000/api/metrics
curl http://localhost:8000/api/reports
```

---

## 🌐 Frontend (dev local)

```bash
cd hids-web
npm install
npm run dev
# http://localhost:5173
# Ajuste src/lib/api.js si ton backend n'est pas sur 8000
```

---

## 🧪 Débogage rapide

```bash
docker compose logs -f api
tail -n 200 logs/hids.log
sqlite3 data/hids.db ".tables"
sqlite3 data/hids.db "pragma table_info('monitored_files');"
```

---

## 🗺️ Roadmap courte

* Génération **HTML/PDF** + email des reports
* Règles d’alerte, notifications, journal d’audit admin
* Scan “on-demand”, throttling, meilleur filtrage/pagination
* Migrations (Alembic), durcissement sécurité (2FA, rate-limit)

---

## 📄 Licence

MIT
