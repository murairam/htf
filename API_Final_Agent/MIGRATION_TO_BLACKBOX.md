# Migration vers BLACKBOX AI - Plan Complet

## Objectif
Migrer API_FINAL_AGENT pour utiliser BLACKBOX AI au lieu d'OpenAI, et intégrer tous les résultats dans Django/Frontend.

## Architecture Cible

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  - Affichage des résultats                                   │
│  - Graphiques Plotly interactifs                            │
│  - Toutes les visualisations d'essenceAI                    │
└─────────────────────────────────────────────────────────────┘
                            ↑
                            │ HTTP
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND                            │
│  - Gestion des requêtes utilisateur                         │
│  - Appel à API_FINAL_AGENT                                  │
│  - Stockage des résultats                                   │
└─────────────────────────────────────────────────────────────┘
                            ↑
                            │ HTTP
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  API_FINAL_AGENT (FastAPI)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ACE Pipeline (BLACKBOX AI)                         │   │
│  │  - Product analysis                                  │   │
│  │  - Scoring                                          │   │
│  │  - SWOT                                             │   │
│  │  - Image analysis (BLACKBOX Vision)                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Essence Pipeline (BLACKBOX AI)                     │   │
│  │  - RAG avec PDFs (BLACKBOX Embeddings)             │   │
│  │  - Competitor analysis (BLACKBOX + Tavily)         │   │
│  │  - Research insights (BLACKBOX)                     │   │
│  │  - Marketing strategy (BLACKBOX)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Unified Output                                      │   │
│  │  - Fusion ACE + Essence                             │   │
│  │  - Génération visualisations Plotly                │   │
│  │  - Format JSON complet                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Changements Nécessaires

### 1. Configuration BLACKBOX AI

**Fichier**: `.env`
```env
# BLACKBOX AI Keys (prioritaires)
BLACKBOX_API_KEY=sk-zJValC5qOR6n62aSOmoxNw
BLACKBOX_CHAT_API_KEY=bb_89eba5664e1b3f0a69b0552832967583699400d6e680729c03dfff3c53762ae8
BLACKBOX_TASK_API_KEY=sk-sZzuDnBmmta4jz3ZT6l2AQ

# OpenAI (fallback seulement)
OPENAI_API_KEY=sk-proj-...

# Autres
TAVILY_API_KEY=tvly-dev-...
```

### 2. Créer Client BLACKBOX AI

**Nouveau fichier**: `API_Final_Agent/api_final_agent/llm/blackbox_client.py`

```python
"""
BLACKBOX AI Client
Wrapper pour utiliser BLACKBOX AI au lieu d'OpenAI
"""

import os
import requests
from typing import List, Dict, Any, Optional


class BlackboxAIClient:
    """Client pour BLACKBOX AI API"""
    
    def __init__(self):
        self.api_key = os.getenv("BLACKBOX_API_KEY")
        self.chat_api_key = os.getenv("BLACKBOX_CHAT_API_KEY")
        self.task_api_key = os.getenv("BLACKBOX_TASK_API_KEY")
        
        if not self.api_key:
            raise ValueError("BLACKBOX_API_KEY not found")
        
        self.base_url = "https://api.blackbox.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "blackbox",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Chat completion avec BLACKBOX AI
        Compatible avec format OpenAI
        """
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    def embeddings(
        self,
        texts: List[str],
        model: str = "blackbox-embedding"
    ) -> List[List[float]]:
        """
        Génération d'embeddings avec BLACKBOX AI
        """
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=self.headers,
            json={
                "model": model,
                "input": texts
            }
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]
    
    def vision_analysis(
        self,
        image_url: str,
        prompt: str
    ) -> str:
        """
        Analyse d'image avec BLACKBOX Vision
        """
        response = requests.post(
            f"{self.base_url}/vision/analyze",
            headers=self.headers,
            json={
                "image_url": image_url,
                "prompt": prompt
            }
        )
        response.raise_for_status()
        return response.json()["analysis"]
```

### 3. Adapter RAG Engine pour BLACKBOX

**Fichier**: `API_Final_Agent/api_final_agent/essence/rag_engine_blackbox.py`

```python
"""
RAG Engine avec BLACKBOX AI Embeddings
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from ..llm.blackbox_client import BlackboxAIClient


class BlackboxRAGEngine:
    """RAG Engine utilisant BLACKBOX AI"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.client = BlackboxAIClient()
        self.index = None
    
    def initialize_index(self):
        """Initialiser l'index avec BLACKBOX embeddings"""
        documents = SimpleDirectoryReader(self.data_dir).load_data()
        
        # Utiliser BLACKBOX pour les embeddings
        self.index = VectorStoreIndex.from_documents(
            documents,
            embed_model=self._get_blackbox_embed_model()
        )
    
    def _get_blackbox_embed_model(self):
        """Créer un modèle d'embedding BLACKBOX compatible LlamaIndex"""
        # Wrapper pour adapter BLACKBOX à LlamaIndex
        pass
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """Requête avec BLACKBOX LLM"""
        query_engine = self.index.as_query_engine(
            llm=self._get_blackbox_llm()
        )
        response = query_engine.query(query_text)
        return {
            "answer": str(response),
            "citations": self._extract_citations(response)
        }
```

### 4. Adapter ACE Pipeline pour BLACKBOX

**Fichier**: `API_Final_Agent/api_final_agent/pipelines/ace_pipeline.py`

Remplacer:
```python
# Ancien (OpenAI)
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Nouveau (BLACKBOX)
from ..llm.blackbox_client import BlackboxAIClient
client = BlackboxAIClient()
```

### 5. Adapter Essence Pipeline pour BLACKBOX

**Fichier**: `API_Final_Agent/api_final_agent/pipelines/essence_pipeline.py`

Même changement que ACE Pipeline.

### 6. Frontend - Afficher Toutes les Visualisations

**Fichier**: `frontend/src/pages/ResultsPage.jsx`

Ajouter sections pour:
- Graphiques de prix (comme dans Streamlit essenceAI)
- Graphiques CO₂ (comme dans Streamlit essenceAI)
- Comparaisons de segments (comme dans Streamlit essenceAI)
- Insights de recherche avec citations
- Stratégies marketing par segment

### 7. Supprimer Dépendances Streamlit

- ❌ `essenceAI/src/app.py` (Streamlit) → Plus nécessaire
- ✅ Tout passe par Django + React Frontend

## Plan d'Implémentation

### Phase 1: Setup BLACKBOX (2h)
1. ✅ Créer `blackbox_client.py`
2. ✅ Tester connexion BLACKBOX API
3. ✅ Créer wrappers pour LlamaIndex
4. ✅ Tester embeddings BLACKBOX

### Phase 2: Migration RAG (2h)
1. ✅ Adapter `rag_engine_optimized.py` pour BLACKBOX
2. ✅ Tester indexation avec BLACKBOX embeddings
3. ✅ Tester requêtes avec BLACKBOX LLM
4. ✅ Vérifier citations des PDFs

### Phase 3: Migration ACE (1h)
1. ✅ Remplacer OpenAI par BLACKBOX dans ACE
2. ✅ Tester analyse de produit
3. ✅ Tester analyse d'image avec BLACKBOX Vision
4. ✅ Vérifier tous les outputs

### Phase 4: Migration Essence (1h)
1. ✅ Remplacer OpenAI par BLACKBOX dans Essence
2. ✅ Tester competitor analysis
3. ✅ Tester research insights
4. ✅ Tester marketing strategy

### Phase 5: Frontend Complet (3h)
1. ✅ Ajouter tous les graphiques d'essenceAI
2. ✅ Ajouter affichage des citations
3. ✅ Ajouter comparaisons de segments
4. ✅ Tester responsive design
5. ✅ Tester interactions

### Phase 6: Tests d'Intégration (2h)
1. ✅ Test complet Django → API_FINAL_AGENT → Frontend
2. ✅ Test avec différents produits
3. ✅ Test performance
4. ✅ Test gestion d'erreurs

## Avantages BLACKBOX AI

1. **Coût**: Potentiellement moins cher qu'OpenAI
2. **Performance**: Optimisé pour les tâches de développement
3. **Intégration**: API compatible avec OpenAI
4. **Support**: Meilleur support pour les cas d'usage B2B

## Checklist de Migration

- [ ] Client BLACKBOX AI créé et testé
- [ ] RAG Engine migré vers BLACKBOX
- [ ] ACE Pipeline migré vers BLACKBOX
- [ ] Essence Pipeline migré vers BLACKBOX
- [ ] Visualisations intégrées dans Frontend
- [ ] Tests complets passés
- [ ] Documentation mise à jour
- [ ] Streamlit essenceAI désactivé
- [ ] Tout fonctionne via Django/React

## Timeline Estimée

- **Setup + Migration Backend**: 6 heures
- **Frontend Complet**: 3 heures
- **Tests**: 2 heures
- **Total**: ~11 heures de travail

## Prochaine Étape Immédiate

Voulez-vous que je commence par:

**A. Créer le client BLACKBOX AI** (30 min)
- Implémenter `blackbox_client.py`
- Tester la connexion
- Vérifier les embeddings

**B. Migrer le RAG Engine** (1h)
- Adapter pour BLACKBOX embeddings
- Tester avec les PDFs
- Vérifier les citations

**C. Faire les tests critiques actuels d'abord** (20 min)
- Vérifier que les corrections JSON fonctionnent
- Puis migrer vers BLACKBOX

**Ma recommandation**: Option C → puis A → puis B
Cela permet de valider les corrections actuelles avant la migration BLACKBOX.

Quelle option préférez-vous?
