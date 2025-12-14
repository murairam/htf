# Guide de Déploiement

Ce guide explique comment déployer l'application avec l'architecture unifiée.

## Architecture des Services

L'application se compose de **2 services** :

1. **Django** (port 8000) - Application principale avec interface React
2. **API_Final_Agent** (port 8001) - Service LLM unifié (fusionne ACE_Framework + EssenceAI)

## Option 1 : Tous les services ensemble (Recommandé)

Lance tous les services en une seule commande :

```bash
make all-services
```

Ou directement :

```bash
./run_all_services.sh
```

**Avantages :**
- ✅ Lance tous les services automatiquement
- ✅ Vérifie que les ports sont libres
- ✅ Attend que chaque service soit prêt avant de lancer le suivant
- ✅ Gère les logs dans `logs/`
- ✅ Arrêt propre avec Ctrl+C

**Ce qui se passe :**
1. Vérifie que les ports 8000 et 8001 sont libres
2. Lance API_Final_Agent en arrière-plan (port 8001)
3. Build le frontend React
4. Lance Django en premier plan (port 8000)

## Option 2 : Services individuels (Développement)

Pour un contrôle plus fin, lancez chaque service séparément :

**Terminal 1 - API_Final_Agent :**
```bash
cd API_Final_Agent
python main.py
```

**Terminal 2 - Django :**
```bash
make prod
# ou
./run_prod.sh
```

## Commandes Utiles

### Vérifier le statut des services

```bash
make check-services
# ou
./check_services.sh
```

### Arrêter tous les services

```bash
make stop-services
# ou
./stop_all_services.sh
```

### Voir les logs

```bash
# Logs API_Final_Agent
tail -f logs/api_final_agent.log
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# OpenAI API Key (requis pour API_Final_Agent)
OPENAI_API_KEY=sk-your-key-here

# URLs des services (optionnel, valeurs par défaut)
FINAL_AGENT_BASE_URL=http://localhost:8001
FINAL_AGENT_TIMEOUT=60
API_FINAL_AGENT_PORT=8001
```

### Ports par défaut

- **8000** : Django (application principale)
- **8001** : API_Final_Agent (service LLM unifié)

## Scénarios d'Usage

### Scénario 1 : Développement local complet

```bash
# Lancer tout
make all-services
```

Accès :
- Interface web : http://localhost:8000
- API_Final_Agent docs : http://localhost:8001/docs

### Scénario 2 : Production (services séparés)

Si vous déployez sur des serveurs différents :

1. **Serveur 1** : API_Final_Agent
   ```bash
   cd API_Final_Agent
   python main.py
   ```

2. **Serveur 2** : Django
   ```bash
   # Mettre à jour .env avec FINAL_AGENT_BASE_URL pointant vers le serveur 1
   make prod
   ```

## Dépannage

### Port déjà utilisé

```bash
# Voir quel processus utilise le port
lsof -i :8001

# Arrêter le processus
kill <PID>
```

### Service ne démarre pas

1. Vérifier les logs : `tail -f logs/api_final_agent.log`
2. Vérifier les variables d'environnement : `echo $OPENAI_API_KEY`
3. Vérifier les dépendances : `cd API_Final_Agent && pip install -r requirements.txt`

### Services ne communiquent pas

1. Vérifier que tous les services sont en cours d'exécution : `make check-services`
2. Vérifier les URLs dans `.env` et `config/settings.py`
3. Vérifier les logs pour les erreurs de connexion

## Recommandations

- **Développement** : Utilisez `make all-services` pour tout lancer facilement
- **Production** : Déployez chaque service séparément avec des processus managers (systemd, supervisor, etc.)
- **Tests** : Utilisez `make check-services` pour vérifier que tout fonctionne
