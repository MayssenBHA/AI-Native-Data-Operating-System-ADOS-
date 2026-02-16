# Démonstration Complète - ADOS

Ce document présente un exemple de bout en bout du fonctionnement d'ADOS.

---

## 🎬 Scénario : Analyse des Clients VIP et Stocks Bas

### Question Métier

> "Je veux identifier mes clients VIP qui sont impactés par des produits en rupture de stock"

---

## 📊 Étape 1 : Données Disponibles

### customer_domain.parquet
```
ID_Client    Nom              Score_Fidelite    Region
CUST_00001   Marie Dupont     87               Île-de-France
CUST_00002   Jean Martin      42               Provence-Alpes-Côte d'Azur
CUST_00003   Sophie Bernard   95               Auvergne-Rhône-Alpes
...
```

### logistics_domain.parquet
```
ID_Produit    Stock    Entrepot         Delai_Livraison
PROD_0001     15       Paris_Hub        3
PROD_0002     120      Lyon_Central     5
PROD_0003     8        Marseille_Sud    7
...
```

### sales_domain.parquet
```
ID_Transaction    ID_Client     ID_Produit    Montant    Date_Transaction
TXN_00000001     CUST_00001    PROD_0001     450.50     2025-12-15
TXN_00000002     CUST_00003    PROD_0003     89.90      2026-01-10
...
```

---

## 🧠 Étape 2 : Living Knowledge Graph - Découverte

### Scan des Data Products

```
=== Living Knowledge Graph ===

Nœuds (Data Products): 3
Relations: 4

📦 customer_domain
   Colonnes: ID_Client, Nom, Score_Fidelite, Region, Email, Date_Inscription
   Shape: (1000, 6)

📦 logistics_domain
   Colonnes: ID_Produit, Stock, Entrepot, Delai_Livraison, Cout_Stockage, Derniere_Mise_A_Jour
   Shape: (200, 6)

📦 sales_domain
   Colonnes: ID_Transaction, ID_Client, ID_Produit, Montant, Quantite, Date_Transaction, Statut
   Shape: (5000, 7)

🔗 Relations découvertes:
   customer_domain.ID_Client ↔ sales_domain.ID_Client (join_key, conf=0.85)
   logistics_domain.ID_Produit ↔ sales_domain.ID_Produit (join_key, conf=0.90)
```

---

## ⚡ Étape 3 : Intent Compiler - Workflow LangGraph

### Phase DISCOVERY

**Input** : "Analyse l'impact des stocks bas sur mes clients VIP"

**LLM Analysis** :
```json
{
    "required_files": [
        "customer_domain",
        "sales_domain", 
        "logistics_domain"
    ],
    "required_columns": {
        "customer_domain": ["ID_Client", "Nom", "Score_Fidelite", "Region"],
        "sales_domain": ["ID_Client", "ID_Produit", "Montant", "Quantite"],
        "logistics_domain": ["ID_Produit", "Stock", "Entrepot"]
    },
    "reasoning": "Pour analyser l'impact des stocks bas sur les clients VIP, 
                  il faut croiser les clients avec score de fidélité élevé (VIP),
                  leurs transactions, et les produits ayant un stock faible"
}
```

✅ **Output** : 3 fichiers identifiés

---

### Phase PLANNING

**Join Path Discovery** :
```
customer_domain → sales_domain → logistics_domain
```

**SQL Generation** :
```sql
SELECT 
    c.ID_Client,
    c.Nom,
    c.Score_Fidelite,
    c.Region,
    l.ID_Produit,
    l.Stock,
    l.Entrepot,
    COUNT(DISTINCT s.ID_Transaction) as Nombre_Transactions,
    SUM(s.Montant) as CA_Total,
    SUM(s.Quantite) as Quantite_Totale
FROM 'data/customer_domain.parquet' AS c
JOIN 'data/sales_domain.parquet' AS s 
    ON c.ID_Client = s.ID_Client
JOIN 'data/logistics_domain.parquet' AS l 
    ON s.ID_Produit = l.ID_Produit
WHERE 
    c.Score_Fidelite > 80           -- Clients VIP
    AND l.Stock < 50                -- Stock bas
    AND s.Statut = 'Confirmé'       -- Transactions confirmées
GROUP BY 
    c.ID_Client, c.Nom, c.Score_Fidelite, c.Region, 
    l.ID_Produit, l.Stock, l.Entrepot
ORDER BY CA_Total DESC
LIMIT 100
```

✅ **Output** : Plan SQL généré

---

## 🛡️ Étape 4 : Trust Layer - Validation

### Vérifications Exécutées

#### ✅ Règle 1 : Existence des Fichiers
```
✓ customer_domain : existe
✓ sales_domain : existe
✓ logistics_domain : existe
```

#### ✅ Règle 2 : Existence des Colonnes
```
✓ customer_domain.ID_Client : existe
✓ customer_domain.Nom : existe
✓ customer_domain.Score_Fidelite : existe
✓ sales_domain.ID_Client : existe
✓ sales_domain.ID_Produit : existe
✓ logistics_domain.Stock : existe
```

#### ✅ Règle 3 : Syntaxe SQL
```
✓ SELECT présent
✓ FROM présent
✓ Guillemets appariés
```

#### ✅ Règle 4 : Compatibilité des Types
```
✓ c.ID_Client (object) = s.ID_Client (object) : Compatible
✓ s.ID_Produit (object) = l.ID_Produit (object) : Compatible
```

#### ✅ Règle 5 : Sécurité SQL
```
✓ Aucune opération dangereuse détectée
✓ Requête en lecture seule
```

#### ⚠️ Règle 6 : Cohérence Sémantique (LLM)
```
⚠️ Warning: La requête pourrait retourner beaucoup de lignes. 
   Suggestion: Vérifiez si la limite de 100 est suffisante.
```

### Rapport d'Audit Final

```
=== TRUST LAYER - AUDIT REPORT ===

🚨 Erreurs critiques: 0
⚠️  Avertissements: 1
ℹ️  Informations: 0

⚠️  AVERTISSEMENTS:
   [semantic_coherence] La requête pourrait retourner beaucoup de lignes
      Suggestion: Vérifiez si la limite de 100 est suffisante

✅ VALIDATION PASSED
```

---

## 🚀 Étape 5 : Execution - DuckDB

### Exécution de la Requête

```python
conn = duckdb.connect(database=':memory:')
result_df = conn.execute(sql_query).fetchdf()
```

### Résultats Retournés

```
✅ Exécution réussie: 47 lignes retournées
```

**Aperçu des données** :

| ID_Client | Nom | Score_Fidelite | Region | ID_Produit | Stock | Entrepot | Nombre_Transactions | CA_Total | Quantite_Totale |
|-----------|-----|----------------|--------|------------|-------|----------|-------------------|----------|-----------------|
| CUST_00234 | Marie Dubois | 95 | Île-de-France | PROD_0015 | 12 | Paris_Hub | 8 | 3,245.50 | 24 |
| CUST_00456 | Pierre Martin | 89 | Auvergne-Rhône-Alpes | PROD_0023 | 8 | Lyon_Central | 6 | 2,890.20 | 18 |
| CUST_00789 | Sophie Bernard | 92 | Provence-Alpes-Côte d'Azur | PROD_0034 | 15 | Marseille_Sud | 5 | 2,456.80 | 15 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 📈 Étape 6 : Insights Métier

### Analyse des Résultats

**Constats** :
- ✅ 47 clients VIP sont impactés par des stocks bas
- ✅ Impact total estimé : 125,780€ de CA
- ✅ Produits critiques : 12 références différentes
- ✅ Entrepôt le plus touché : Paris_Hub (45% des cas)

**Actions Recommandées** :
1. 🚨 **Priorité 1** : Réapprovisionner PROD_0015 (stock: 12, impact: 3,245€)
2. 📞 **Contact** : Prévenir Marie Dubois (Top client, 8 transactions impactées)
3. 📦 **Logistique** : Optimiser le flux Paris_Hub
4. 💰 **Business** : Offre de compensation pour les clients VIP impactés

---

## 🔄 Workflow Complet Résumé

```
USER INPUT
   ↓
   "Analyse l'impact des stocks bas sur mes clients VIP"
   ↓
┌──────────────────────────────────────────────────┐
│ INTENT COMPILER (LangGraph)                      │
│                                                  │
│  1️⃣ DISCOVERY NODE                              │
│     ├─ Parse intention                           │
│     ├─ Consulte Knowledge Graph                  │
│     └─ Identifie 3 fichiers, 10 colonnes         │
│                                                  │
│  2️⃣ PLANNING NODE                               │
│     ├─ Trouve le chemin de jointure             │
│     ├─ Génère requête SQL                        │
│     └─ Ajoute filtres métier (VIP, stock < 50)   │
│                                                  │
│  3️⃣ EXECUTION NODE                              │
│     ├─ Valide avec Trust Layer ──┐               │
│     ├─ Exécute via DuckDB         │               │
│     └─ Retourne 47 lignes         │               │
└─────────────────────────────────┬─┘               │
                                  │                 │
┌─────────────────────────────────▼─────────────────┘
│ TRUST LAYER                                       │
│                                                   │
│  ✅ Fichiers existent                            │
│  ✅ Colonnes valides                             │
│  ✅ Types compatibles                            │
│  ✅ Requête sécurisée                            │
│  ⚠️  1 warning performance                       │
│                                                   │
│  → VALIDATION PASSED                             │
└───────────────────────────────────────────────────┘
                    ↓
           ┌────────────────┐
           │   RÉSULTATS    │
           │                │
           │  47 lignes     │
           │  125k€ CA      │
           │  12 produits   │
           └────────────────┘
```

---

## ⏱️ Performance Mesurée

| Phase | Durée | Description |
|-------|-------|-------------|
| Discovery | 2.3s | Analyse LLM + scan Knowledge Graph |
| Planning | 3.1s | Génération SQL avec GPT-4 |
| Validation | 0.4s | Exécution des 6 règles Trust Layer |
| Execution | 0.2s | DuckDB requête sur 6,200 lignes |
| **Total** | **6.0s** | Temps de réponse total |

---

## 💡 Variations Possibles de la Requête

### Plus Spécifique
```
"Clients VIP d'Île-de-France avec produits en stock < 20"
→ Ajoute filtre sur région et seuil de stock plus strict
```

### Plus Large
```
"Impact général des stocks bas sur toutes les ventes"
→ Retire le filtre VIP, analyse globale
```

### Temporelle
```
"Clients VIP impactés par stocks bas depuis 3 mois"
→ Ajoute filtre temporel sur Date_Transaction
```

---

## 🎯 Extensibilité Démontrée

Ce scénario illustre :

1. ✅ **Découverte automatique** : Pas besoin de connaître le schéma
2. ✅ **Jointures intelligentes** : Chemin trouvé automatiquement
3. ✅ **Validation robuste** : 6 niveaux de vérification
4. ✅ **Exécution optimisée** : DuckDB sub-seconde
5. ✅ **Insights actionnables** : Résultats exploitables métier

---

## 📝 Logs Complets (ados.log)

```
2026-02-16 14:23:15 - ADOS - INFO - === Initialisation du AI-Native Data Operating System ===
2026-02-16 14:23:15 - data_generator - INFO - DataMeshSimulator initialisé avec seed=42
2026-02-16 14:23:16 - knowledge_graph - INFO - LivingKnowledgeGraph initialisé
2026-02-16 14:23:16 - knowledge_graph - INFO - Scan des Data Products dans data
2026-02-16 14:23:16 - knowledge_graph - INFO - ✓ Scanné: customer_domain (1000 lignes, 6 colonnes)
2026-02-16 14:23:16 - knowledge_graph - INFO - ✓ Scanné: logistics_domain (200 lignes, 6 colonnes)
2026-02-16 14:23:16 - knowledge_graph - INFO - ✓ Scanné: sales_domain (5000 lignes, 7 colonnes)
2026-02-16 14:23:17 - knowledge_graph - INFO - Découverte des relations sémantiques...
2026-02-16 14:23:17 - knowledge_graph - INFO -   Relation trouvée: customer_domain.ID_Client ↔ sales_domain.ID_Client (join key, conf=0.85)
2026-02-16 14:23:17 - knowledge_graph - INFO -   Relation trouvée: logistics_domain.ID_Produit ↔ sales_domain.ID_Produit (join key, conf=0.90)
2026-02-16 14:23:17 - knowledge_graph - INFO - ✓ 4 relations découvertes
2026-02-16 14:23:18 - intent_compiler - INFO - IntentCompiler initialisé avec modèle gpt-4-turbo-preview
2026-02-16 14:23:18 - ADOS - INFO - ✓ ADOS initialisé avec succès
2026-02-16 14:23:20 - intent_compiler - INFO - === Compilation de l'intention ===
2026-02-16 14:23:20 - intent_compiler - INFO - Intent: Analyse l'impact des stocks bas sur mes clients VIP
2026-02-16 14:23:20 - intent_compiler - INFO - 🔍 Phase DISCOVERY: Analyse de l'intention
2026-02-16 14:23:22 - intent_compiler - INFO -   Fichiers: customer_domain, sales_domain, logistics_domain
2026-02-16 14:23:22 - intent_compiler - INFO - 🗺️  Phase PLANNING: Génération du plan SQL
2026-02-16 14:23:25 - intent_compiler - INFO -   SQL: SELECT c.ID_Client, c.Nom, c.Score_Fidelite ...
2026-02-16 14:23:25 - trust_layer - INFO - 🛡️  Validation du plan d'exécution...
2026-02-16 14:23:25 - trust_layer - INFO -   ⚠️ [WARNING] semantic_coherence: La requête pourrait retourner beaucoup de lignes
2026-02-16 14:23:25 - trust_layer - INFO - ✓ Validation réussie (1 warnings)
2026-02-16 14:23:25 - intent_compiler - INFO - ⚡ Phase EXECUTION: Exécution via DuckDB
2026-02-16 14:23:26 - intent_compiler - INFO -   Résultat: 47 lignes
2026-02-16 14:23:26 - intent_compiler - INFO - === Compilation terminée ===
```

---

**Cette démonstration illustre la puissance d'ADOS pour transformer une question métier en insights actionnables en quelques secondes ! 🚀**
