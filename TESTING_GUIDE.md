# Guide de Test - Competitor Intelligence & Corrections

## ⚠️ IMPORTANT

**Les modifications ne seront visibles que pour les NOUVELLES analyses!**

Les anciennes analyses dans la base de données n'ont pas les données de compétiteurs. Vous devez lancer une **nouvelle analyse** pour voir les changements.

---

## Étapes pour tester

### 1. Redémarrer les services ✅

```bash
make all-services
```

Cela va:
- Rebuild le frontend
- Copier les fichiers vers Django
- Démarrer API_Final_Agent (port 8001)
- Démarrer Django (port 8000)

### 2. Attendre que les services démarrent

Vérifier que les services sont actifs:

```bash
# Vérifier API_Final_Agent
curl http://localhost:8001/

# Vérifier Django
curl http://localhost:8000/
```

### 3. Lancer une NOUVELLE analyse

**Option A: Via l'interface web**
1. Aller sur http://localhost:8000/
2. Scanner ou entrer un barcode (ex: `3274080005003`)
3. Entrer un objectif business
4. Cliquer "Analyze"

**Option B: Via curl (pour debug)**
```bash
curl -X POST http://localhost:8001/run-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "3274080005003",
    "business_objective": "Launch new plant-based product in European market"
  }' | jq '.competitor_intelligence'
```

### 4. Vérifier les données dans la réponse

La réponse devrait contenir:

```json
{
  "competitor_intelligence": {
    "competitors": [...],
    "metrics": {
      "avg_price_per_kg": 25.45,
      "avg_co2_emission": 2.2,
      "competitor_count": 10
    },
    "visualizations": {
      "price_chart": {...},
      "co2_chart": {...},
      "scatter_chart": {...}
    }
  }
}
```

### 5. Vérifier l'affichage frontend

Dans l'onglet "Competitor Intelligence", vous devriez voir:

**Section ACE Analysis** (badge bleu)
- 📊 Real-Time Competitor Analysis
- 4 cartes métriques:
  - Avg Price/kg: €25.45
  - Avg CO₂/kg: 2.2 kg
  - Competitors: 10
  - Price Range: €20.0-€30.0
- Table avec 10 compétiteurs
- 3 graphiques Plotly interactifs

---

## Problèmes courants

### ❌ "No competitor intelligence data available"

**Cause:** Vous regardez une ancienne analyse

**Solution:** Lancer une NOUVELLE analyse (voir étape 3)

### ❌ Les graphiques ne s'affichent pas

**Cause:** Plotly.js n'est pas chargé

**Solution:** 
1. Vider le cache du navigateur (Ctrl+Shift+Del)
2. Rafraîchir la page (Ctrl+F5)
3. Vérifier la console du navigateur pour les erreurs

### ❌ L'API ne répond pas

**Cause:** Services non démarrés

**Solution:**
```bash
# Arrêter tous les services
make stop-services

# Redémarrer
make all-services
```

### ❌ Erreur "OPENAI_API_KEY not found"

**Cause:** Variable d'environnement manquante

**Solution:**
```bash
export OPENAI_API_KEY="votre-clé-api"
make all-services
```

---

## Vérification des logs

### Logs API_Final_Agent
```bash
tail -f logs/api_final_agent.log
```

Vous devriez voir:
```
✅ ACE pipeline initialized
   Looking up product from OpenFoodFacts...
   OpenFoodFacts lookup completed in 0.6s
   Downloading image from https://...
   ✅ Image downloaded successfully (11238 bytes)
   Running ACE pipeline...
   ✅ ACE pipeline completed
   Generating competitor intelligence...
   ✅ Competitor intelligence generated in 0.1s
```

### Logs Django
```bash
python manage.py runserver --noreload
```

---

## Checklist de test

- [ ] Services démarrés (API_Final_Agent + Django)
- [ ] Nouvelle analyse lancée
- [ ] Réponse API contient `competitor_intelligence`
- [ ] Frontend affiche l'onglet "Competitor Intelligence"
- [ ] Badge bleu "ACE Analysis" visible
- [ ] 4 cartes métriques affichées
- [ ] Table de 10 compétiteurs visible
- [ ] 3 graphiques Plotly interactifs
- [ ] Packaging Improvements formaté correctement
- [ ] Visualizations section fonctionne
- [ ] Complete Analysis Data humanisé

---

## Données de test

### Barcodes recommandés
- `3274080005003` - Produit Danone (testé)
- `3760020507350` - Beyond Burger
- `5410188031034` - Alpro Soja

### Objectifs business exemples
- "Launch new plant-based product in European market"
- "Improve packaging sustainability"
- "Increase market share in vegan segment"

---

## Debug avancé

### Inspecter la réponse complète
```bash
curl -X POST http://localhost:8001/run-analysis \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3274080005003", "business_objective": "Test"}' \
  > response.json

# Vérifier la structure
jq 'keys' response.json
jq '.competitor_intelligence.metrics' response.json
jq '.competitor_intelligence.competitors | length' response.json
```

### Tester le module directement
```bash
cd API_Final_Agent
python -c "
from api_final_agent.ace.competitor_data import get_competitor_intelligence
data = get_competitor_intelligence()
print(f'Competitors: {len(data[\"competitors\"])}')
print(f'Avg Price: €{data[\"metrics\"][\"avg_price_per_kg\"]:.2f}/kg')
"
```

---

## Support

Si les problèmes persistent:

1. Vérifier les versions:
```bash
python --version  # 3.8+
node --version    # 16+
npm --version     # 8+
```

2. Réinstaller les dépendances:
```bash
make fclean
make install
make all-services
```

3. Vérifier les fichiers modifiés:
```bash
git status
git diff API_Final_Agent/api_final_agent/ace/competitor_data.py
```

---

## Résultat attendu

Après avoir suivi ces étapes, vous devriez voir dans le frontend:

1. **Onglet Competitor Intelligence** avec données ACE
2. **Graphiques interactifs** (prix, CO2, scatter)
3. **Table de compétiteurs** avec 10 entrées
4. **Métriques** calculées automatiquement
5. **Packaging Improvements** bien formaté
6. **Visualizations** fonctionnelles

**Bonne chance! 🚀**
