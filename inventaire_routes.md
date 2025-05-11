Voici une **proposition exhaustive** des routes API nécessaires, classées par écran / fonctionnalité. Tous les chemins sont en anglais (to “monitoring” the French “surveillance”), et chacun indique la méthode HTTP, le chemin, ainsi que sa finalité et les principaux paramètres.

---

## 1. Dashboard

**Objectif** : récupérer tous les indicateurs et séries de données pour peupler le tableau de bord en temps réel.

| Méthode | Chemin                   | Description                                       | Query / Body                                 |
| ------- | ------------------------ | ------------------------------------------------- | -------------------------------------------- |
| GET     | `/status`                | État global du HIDS Engine et des sous-moteurs    | —                                            |
| GET     | `/metrics/entities`      | Nombre total d’éléments surveillés                | —                                            |
| GET     | `/metrics/alerts/active` | Nombre d’alertes actives                          | —                                            |
| GET     | `/metrics/alerts/latest` | Détails de la dernière alerte (timestamp, source) | —                                            |
| GET     | `/metrics/scans/next`    | Date/heure ou délai avant le prochain scan prévu  | —                                            |
| GET     | `/activity`              | Flux d’événements récents (démarrages, pauses…)   | `limit` (opt), `since` (opt)                 |
| GET     | `/alerts/by-type`        | Données pour histogramme « Alerts by Type »       | `from`, `to` (opt)                           |
| GET     | `/alerts/over-time`      | Série temporelle des alertes (courbe)             | `from`, `to`, `interval` (opt: `hour`,`day`) |

---

## 2. Monitoring (Files & Folders)

**Objectif** : CRUD sur les fichiers et dossiers à surveiller.

| Méthode | Chemin                       | Description                             | Body                                          |              |
| ------- | ---------------------------- | --------------------------------------- | --------------------------------------------- | ------------ |
| GET     | `/monitoring/files`          | Lister tous les fichiers surveillés     | —                                             |              |
| POST    | `/monitoring/files`          | Ajouter un fichier à surveiller         | `{ "path": string, "frequency": number }`     |              |
| PUT     | `/monitoring/files/{fileId}` | Mettre à jour fréquence ou statut       | \`{ "frequency"?: number, "status"?: "active" | "paused" }\` |
| DELETE  | `/monitoring/files/{fileId}` | Supprimer un fichier de la surveillance | —                                             |              |

---

## 3. Monitoring (IP Addresses)

**Objectif** : CRUD sur les adresses IP à surveiller.

| Méthode | Chemin                   | Description                         | Body                                                         |              |
| ------- | ------------------------ | ----------------------------------- | ------------------------------------------------------------ | ------------ |
| GET     | `/monitoring/ips`        | Lister toutes les IP surveillées    | —                                                            |              |
| POST    | `/monitoring/ips`        | Ajouter une IP à surveiller         | `{ "ip": string, "hostname"?: string, "frequency": number }` |              |
| PUT     | `/monitoring/ips/{ipId}` | Mettre à jour fréquence ou statut   | \`{ "frequency"?: number, "status"?: "active"                | "paused" }\` |
| DELETE  | `/monitoring/ips/{ipId}` | Supprimer une IP de la surveillance | —                                                            |              |

---

## 4. Alerts & Logs

**Objectif** : filtrer et paginer alertes + logs, et exporter si besoin.

| Méthode | Chemin              | Description                      | Query parameters                                                   |
| ------- | ------------------- | -------------------------------- | ------------------------------------------------------------------ |
| GET     | `/alerts`           | Liste des alertes                | `from`, `to`, `type`, `entityType`, `severity`, `page`, `pageSize` |
| GET     | `/alerts/{alertId}` | Détails d’une alerte             | —                                                                  |
| GET     | `/logs`             | Liste des logs (tous events)     | mêmes filtres que `/alerts` + `source`                             |
| GET     | `/logs/export`      | Export CSV/JSON des logs filtrés | mêmes filtres que `/logs`                                          |

---

## 5. Reports

**Objectif** : générer et télécharger des rapports summary / detailed.

| Méthode | Chemin                         | Description                  | Query / Body         |                                        |
| ------- | ------------------------------ | ---------------------------- | -------------------- | -------------------------------------- |
| POST    | `/reports`                     | Lancer génération de rapport | \`{ "type":"summary" | "detailed", "from"\:ISO, "to"\:ISO }\` |
| GET     | `/reports`                     | Lister rapports existants    | `page`, `pageSize`   |                                        |
| GET     | `/reports/{reportId}/download` | Récupérer le PDF/ZIP généré  | —                    |                                        |

---

## 6. Users & Auth (Settings)

**Objectif** : gérer comptes, rôles, mots de passe, et droits d’accès.

| Méthode | Chemin                     | Description                      | Body                                                    |                |
| ------- | -------------------------- | -------------------------------- | ------------------------------------------------------- | -------------- |
| POST    | `/auth/login`              | Connexion                        | `{ "email":string, "password":string }`                 |                |
| POST    | `/auth/logout`             | Déconnexion                      | —                                                       |                |
| GET     | `/users`                   | Lister utilisateurs (admin only) | —                                                       |                |
| GET     | `/users/{userId}`          | Détails d’un utilisateur         | —                                                       |                |
| POST    | `/users`                   | Créer un utilisateur (admin)     | \`{ "email"\:string, "password"\:string, "role":"admin" | "user" }\`     |
| PUT     | `/users/{userId}`          | Modifier rôle/status (admin)     | \`{ "role"?\:string, "status"?: "active"                | "inactive" }\` |
| PUT     | `/users/{userId}/password` | Changer mot de passe             | `{ "new_password":string }`                             |                |
| DELETE  | `/users/{userId}`          | Supprimer utilisateur (admin)    | —                                                       |                |

---

## 7. Integrations & Webhooks (Settings)

**Objectif** : configurer API keys et webhooks, activer/désactiver.

| Méthode | Chemin                     | Description                       | Body                                     |
| ------- | -------------------------- | --------------------------------- | ---------------------------------------- |
| GET     | `/integrations`            | Voir clés/API et webhooks         | —                                        |
| PUT     | `/integrations/virustotal` | Enregistrer clé VirusTotal (v2.1) | `{ "apiKey": string }`                   |
| POST    | `/webhooks`                | Ajouter un webhook                | `{ "url": string, "active": boolean }`   |
| PUT     | `/webhooks/{webhookId}`    | Modifier un webhook               | `{ "url"?: string, "active"?: boolean }` |
| DELETE  | `/webhooks/{webhookId}`    | Supprimer un webhook              | —                                        |

---

## 8. Application Settings (Admin toggles)

**Objectif** : restreindre Reports & Settings aux admins, gérer mise à jour.

| Méthode | Chemin           | Description                               | Body                                                            |
| ------- | ---------------- | ----------------------------------------- | --------------------------------------------------------------- |
| GET     | `/config/access` | Voir restrictions admin-only              | —                                                               |
| PUT     | `/config/access` | Mettre à jour toggles (reports, settings) | `{ "reportsAdminOnly": boolean, "settingsAdminOnly": boolean }` |
| GET     | `/updates`       | Version actuelle                          | —                                                               |
| POST    | `/updates/check` | Forcer recherche de nouvelle version      | —                                                               |

---

> 🗝️ **Prochaine étape** : valider cette liste ou la compléter (noms, regroupements, filtres) avant de formaliser les JSON schemas de chacun de ces objets (User, MonitoredItem, Alert, Report).
