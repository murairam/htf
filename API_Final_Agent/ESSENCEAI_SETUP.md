# EssenceAI Wrapper - Setup & Troubleshooting

## Problème : Erreur 500 "EssenceAI agents not available"

### Cause

Le wrapper EssenceAI nécessite le module `llama_index` et d'autres dépendances qui ne sont pas installées dans l'environnement virtuel de `API_Final_Agent`.

### Solution 1 : Mode Mock (Recommandé pour les tests)

Le wrapper a été modifié pour retourner une **réponse mock** quand les agents ne sont pas disponibles. Cela permet de tester l'intégration complète même sans installer toutes les dépendances EssenceAI.

**Redémarrer le serveur EssenceAI pour activer le mode mock :**

```bash
# Arrêter le serveur actuel
make stop-services
# ou
./stop_all_services.sh

# Redémarrer
make all-services
# ou
./run_all_services.sh
```

Le wrapper retournera maintenant une réponse mock au lieu d'une erreur 500.

### Solution 2 : Installer les dépendances EssenceAI

Si vous voulez utiliser les vrais agents EssenceAI :

```bash
cd API_Final_Agent
source venv/bin/activate
pip install -r ../essenceAI/requirements.txt
```

**Note:** Cela peut prendre du temps et nécessiter beaucoup d'espace disque.

### Vérification

Testez le wrapper après redémarrage :

```bash
curl -X POST http://localhost:8002/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "test",
    "product_description": "test product"
  }'
```

Vous devriez recevoir une réponse mock au lieu d'une erreur 500.

## Impact sur API_Final_Agent

Le normalizer EssenceAI a été mis à jour pour gérer les réponses mock. L'orchestrateur fonctionnera avec :
- **ACE seulement** : Si seulement barcode est fourni
- **EssenceAI mock** : Si product_link ou product_description est fourni (sans dépendances)
- **Les deux** : Si barcode + link/description sont fournis

Le statut sera `partial` si EssenceAI retourne un mock, mais l'analyse fonctionnera quand même.

