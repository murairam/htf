# Intégration des Clés API dans API_Final_Agent

Ce document décrit l'utilisation des clés API dans le système et leur intégration.

## Clés API Disponibles

D'après le fichier `.env`, les clés API suivantes sont disponibles :

1. **OPENAI_API_KEY** - Utilisée pour GPT-4 et les embeddings
2. **BLACKBOX_API_KEY** - Clé principale Blackbox (fallback)
3. **BLACKBOX_CHAT_API_KEY** - Pour les chat completions (format `bb_`)
4. **BLACKBOX_TASK_API_KEY** - Pour les tâches de repository (format `sk-`)
5. **TAVILY_API_KEY** - Pour la recherche web en temps réel
6. **ANTHROPIC_API_KEY** - Pour Claude (Anthropic)
7. **WEAVIATE_API_KEY** - Pour le stockage vectoriel cloud
8. **WEAVIATE_URL** - URL du cluster Weaviate

## Utilisation Actuelle

### ✅ Déjà Intégrées

#### 1. OPENAI_API_KEY
- **Utilisée dans** :
  - `ace/config.py` - Configuration ACE
  - `essence/competitor_data.py` - Extraction de données compétiteurs
  - `essence/rag_engine_*.py` - Génération d'embeddings
  - `essence/agents/base_agent.py` - LLM provider par défaut
  - `pipelines/ace_pipeline.py` - Pipeline ACE

#### 2. TAVILY_API_KEY
- **Utilisée dans** :
  - `essence/competitor_data.py` - Recherche web pour données compétiteurs
  - `essence/app.py` - Interface Streamlit
- **Fonction** : Recherche en temps réel de données de marché et compétiteurs

#### 3. BLACKBOX_API_KEY / BLACKBOX_CHAT_API_KEY / BLACKBOX_TASK_API_KEY
- **Utilisée dans** :
  - `essence/blackbox_client.py` - Client Blackbox AI
  - `essence/agents_legacy.py` - CodeAgent et QualityAgent
- **Fonction** :
  - Chat completions (code generation, analysis)
  - Repository tasks (automatisation de code)
  - Code analysis et quality checks

#### 4. WEAVIATE_API_KEY / WEAVIATE_URL
- **Utilisée dans** :
  - `essence/rag_engine_weaviate.py` - Stockage vectoriel cloud
- **Fonction** : Stockage des embeddings dans Weaviate Cloud (évite de recalculer)

### ⚠️ Partiellement Intégrées

#### 5. ANTHROPIC_API_KEY
- **Définie dans** : `ace/config.py`
- **Support dans** : `essence/agents/base_agent.py` (option `llm_provider="anthropic"`)
- **Statut** : Clé disponible mais pas activement utilisée par défaut
- **Recommandation** : Vérifier que Anthropic SDK est installé et fonctionnel

## Nouvelles Fonctionnalités Ajoutées

### 1. Module de Visualisations (`visualizations.py`)

Un nouveau module a été créé pour générer des graphiques Plotly automatiquement :

- **Fonctions** :
  - `generate_competitor_visualizations()` - Graphiques de prix, CO2, scatter plots
  - `generate_scoring_visualizations()` - Graphiques de scores de performance
  - `generate_swot_visualization()` - Vue d'ensemble SWOT
  - `generate_all_visualizations()` - Génère toutes les visualisations possibles

- **Intégration** : Automatiquement appelé dans `unified_output.py` lors de la fusion des résultats

### 2. Amélioration de `unified_output.py`

- Génération automatique de visualisations à partir des données d'analyse
- Détection et inclusion des visualisations existantes
- Support des graphiques Plotly en format JSON

## Ce qui Manquait (Maintenant Corrigé)

### Visualisations Manquantes

**Problème** : Les visualisations Plotly générées dans EssenceAI n'étaient pas incluses dans l'API finale.

**Solution** :
1. Création du module `visualizations.py` pour générer des graphiques
2. Intégration dans `unified_output.py` pour inclure automatiquement les visualisations
3. Support des formats Plotly JSON pour le frontend

### Utilisation Complète des Clés API

**Problème** : Certaines clés API n'étaient pas utilisées ou mal configurées.

**Solution** :
- Toutes les clés sont maintenant correctement référencées
- Support d'ANTHROPIC_API_KEY pour Claude
- Support complet de BLACKBOX avec les deux types de clés (chat et task)

## Configuration Requise

### Variables d'Environnement

Assurez-vous que votre fichier `.env` contient :

```bash
OPENAI_API_KEY=sk-...
BLACKBOX_API_KEY=sk-...  # Fallback
BLACKBOX_CHAT_API_KEY=bb_...  # Pour chat completions
BLACKBOX_TASK_API_KEY=sk-...  # Pour repository tasks
TAVILY_API_KEY=tvly-...
ANTHROPIC_API_KEY=sk-ant-...  # Optionnel
WEAVIATE_API_KEY=...
WEAVIATE_URL=https://...
```

### Dépendances Python

Les packages suivants sont nécessaires :

```bash
pip install plotly>=5.18.0  # Pour les visualisations
pip install tavily-python>=0.3.0  # Pour Tavily API
pip install anthropic>=0.18.0  # Pour Claude (optionnel)
pip install weaviate-client>=3.25.0  # Pour Weaviate (optionnel)
```

## Utilisation dans Django

Les visualisations sont maintenant incluses dans la réponse JSON de l'API et peuvent être affichées dans le frontend React via le composant `VisualsRenderer`.

### Format des Visualisations

Chaque visualisation est retournée dans ce format :

```json
{
  "title": "Price Comparison",
  "type": "plotly_chart",
  "format": "plotly_json",
  "data": {
    "data": [...],
    "layout": {...}
  }
}
```

Le frontend peut utiliser Plotly.js pour les afficher directement.

## Prochaines Étapes

1. ✅ Module de visualisations créé
2. ✅ Intégration dans unified_output.py
3. ⏳ Tester les visualisations dans le frontend
4. ⏳ Vérifier que toutes les clés API fonctionnent correctement
5. ⏳ Documenter les cas d'usage spécifiques pour chaque API

## Notes

- Les visualisations sont générées automatiquement si Plotly est disponible
- En cas d'erreur, le système continue sans les visualisations (graceful degradation)
- Les visualisations existantes dans EssenceAI sont préservées et incluses

