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
