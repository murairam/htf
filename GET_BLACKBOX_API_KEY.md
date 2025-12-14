# Comment obtenir une clé API BLACKBOX (Gratuit)

## Option 1: Via le site BLACKBOX AI (Recommandé)

1. **Aller sur**: https://www.blackbox.ai/
2. **S'inscrire/Se connecter** avec votre compte
3. **Aller dans Settings** → **API Keys**
4. **Créer une nouvelle clé API**
5. **Copier la clé**

## Option 2: Utiliser un modèle gratuit sans authentification

BLACKBOX offre certains modèles sans clé API. Modifions la configuration pour utiliser ces modèles.

## Configuration actuelle

Votre configuration utilise:
- `blackboxai/deepseek/deepseek-chat` - Nécessite une clé API
- `blackboxai/openai/gpt-4o` - Nécessite une clé API

## Solution temporaire: Utiliser des modèles gratuits

Certains modèles BLACKBOX sont disponibles sans authentification:
- `gpt-3.5-turbo` (via proxy BLACKBOX)
- `claude-instant-1` (via proxy BLACKBOX)

## Instructions

### Étape 1: Obtenir une clé BLACKBOX (5 minutes)

1. Visitez: https://www.blackbox.ai/
2. Créez un compte (gratuit)
3. Allez dans Settings → API
4. Générez une clé API
5. Copiez la clé

### Étape 2: Configurer la clé

```bash
# Ajouter à votre .env ou .bashrc
export BLACKBOX_API_KEY="votre-clé-ici"

# Ou créer un fichier .env dans le projet
echo 'BLACKBOX_API_KEY=votre-clé-ici' >> .env
```

### Étape 3: Redémarrer le service

```bash
# Arrêter le service actuel
pkill -f "API_Final_Agent/main.py"

# Redémarrer avec la nouvelle clé
cd API_Final_Agent
source venv/bin/activate
export BLACKBOX_API_KEY="votre-clé-ici"
python main.py
```

## Alternative: Revenir à un modèle mock pour les tests

Si vous voulez juste tester sans API:
- Utiliser `provider: "mock"` dans la configuration
- Cela génère des données de test sans appeler d'API

## Besoin d'aide?

Si vous avez des difficultés à obtenir la clé BLACKBOX, je peux:
1. Configurer un mode mock pour les tests
2. Vous aider à configurer une autre API gratuite
3. Optimiser l'utilisation de votre quota OpenAI existant
