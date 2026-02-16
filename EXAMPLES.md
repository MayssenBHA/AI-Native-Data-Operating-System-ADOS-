# Exemples et Cas d'Usage ADOS

## 📚 Table des Matières

1. [Requêtes Basiques](#requêtes-basiques)
2. [Analyses Avancées](#analyses-avancées)
3. [Cas d'Usage Métier](#cas-dusage-métier)
4. [Utilisation Programmatique](#utilisation-programmatique)

---

## Requêtes Basiques

### 1. Exploration Simple

```
"Montre-moi tous les clients"
"Combien de produits avons-nous ?"
"Liste les 20 dernières transactions"
```

**Exemple de sortie attendue:**
```
✓ Découverte: 1 fichiers identifiés
✓ Plan SQL généré
✓ Exécution réussie: 1000 lignes

Aperçu:
ID_Client    Nom              Score_Fidelite    Region
CUST_00001   Marie Dupont     87               Île-de-France
CUST_00002   Jean Martin      42               Provence-Alpes-Côte d'Azur
...
```

### 2. Top N / Classements

```
"Montre-moi les 10 meilleurs clients par montant total"
"Quels sont les 5 produits avec le plus de stock ?"
"Top 3 des régions par nombre de clients"
```

### 3. Filtres Simples

```
"Liste les produits avec un stock inférieur à 50"
"Montre les clients avec un score de fidélité supérieur à 80"
"Quels produits ont un délai de livraison supérieur à 10 jours ?"
```

---

## Analyses Avancées

### 4. Segmentation Clients

```
"Identifie les clients VIP (score > 80) avec leurs achats totaux"
```

**SQL Généré:**
```sql
SELECT 
    c.ID_Client,
    c.Nom,
    c.Score_Fidelite,
    c.Region,
    COUNT(s.ID_Transaction) as Nombre_Achats,
    SUM(s.Montant) as Montant_Total
FROM 'data/customer_domain.parquet' AS c
LEFT JOIN 'data/sales_domain.parquet' AS s 
    ON c.ID_Client = s.ID_Client
WHERE c.Score_Fidelite > 80
GROUP BY c.ID_Client, c.Nom, c.Score_Fidelite, c.Region
ORDER BY Montant_Total DESC
LIMIT 100
```

### 5. Analyse Multi-Domaines

```
"Analyse l'impact des stocks bas sur mes clients VIP"
```

**Logique:**
1. Identifie produits avec stock < 50 (logistics_domain)
2. Trouve les transactions sur ces produits (sales_domain)
3. Filtre les clients VIP (customer_domain, Score_Fidelite > 80)
4. Agrège les résultats

**SQL Généré:**
```sql
SELECT 
    c.Nom,
    c.Score_Fidelite,
    l.ID_Produit,
    l.Stock,
    COUNT(s.ID_Transaction) as Achats_Produits_Faible_Stock,
    SUM(s.Montant) as Montant_Impacte
FROM 'data/customer_domain.parquet' AS c
JOIN 'data/sales_domain.parquet' AS s 
    ON c.ID_Client = s.ID_Client
JOIN 'data/logistics_domain.parquet' AS l 
    ON s.ID_Produit = l.ID_Produit
WHERE l.Stock < 50 AND c.Score_Fidelite > 80
GROUP BY c.Nom, c.Score_Fidelite, l.ID_Produit, l.Stock
ORDER BY Montant_Impacte DESC
```

### 6. Analyses Temporelles

```
"Montre-moi l'évolution des ventes par mois"
"Identifie les clients inactifs depuis plus de 6 mois"
"Quelles sont les tendances d'achat par région ?"
```

### 7. Corrélations

```
"Y a-t-il une corrélation entre le délai de livraison et les achats ?"
"Les clients fidèles achètent-ils plus de produits en stock limité ?"
```

---

## Cas d'Usage Métier

### 8. Optimisation Logistique

**Requête:**
```
"Identifie les entrepôts avec des coûts de stockage élevés et faible rotation"
```

**Business Value:**
- Réduction des coûts
- Optimisation de l'espace
- Meilleure allocation des ressources

### 9. Rétention Client

**Requête:**
```
"Liste les clients fidèles qui n'ont pas acheté depuis 3 mois"
```

**Actions possibles:**
- Campagne de réengagement
- Offres personnalisées
- Analyse de churn

### 10. Analyse Régionale

**Requête:**
```
"Compare les performances des ventes par région avec les délais de livraison moyens"
```

**SQL Généré:**
```sql
SELECT 
    c.Region,
    COUNT(DISTINCT c.ID_Client) as Nombre_Clients,
    COUNT(s.ID_Transaction) as Nombre_Ventes,
    SUM(s.Montant) as CA_Total,
    AVG(l.Delai_Livraison) as Delai_Moyen,
    AVG(s.Montant) as Panier_Moyen
FROM 'data/customer_domain.parquet' AS c
LEFT JOIN 'data/sales_domain.parquet' AS s 
    ON c.ID_Client = s.ID_Client
LEFT JOIN 'data/logistics_domain.parquet' AS l 
    ON s.ID_Produit = l.ID_Produit
GROUP BY c.Region
ORDER BY CA_Total DESC
```

### 11. Détection d'Anomalies

**Requête:**
```
"Trouve les transactions avec un montant supérieur à 3 fois la moyenne"
```

**Trust Layer Detection:**
- Valide la logique statistique
- Vérifie l'absence de division par zéro
- S'assure de la cohérence des types

---

## Utilisation Programmatique

### 12. Intégration Python

```python
from ados_main import ADOS

# Initialiser le système
ados = ADOS(auto_generate=True)

# Traiter plusieurs intentions
intentions = [
    "Top 10 clients par CA",
    "Produits en rupture de stock",
    "Clients VIP d'Île-de-France"
]

results = []
for intent in intentions:
    result = ados.process_intent(intent, validate=True)
    results.append(result)
    
    # Extraire les données
    if result["execution"] and result["execution"].success:
        import pandas as pd
        df = pd.read_json(result["execution"].data)
        
        # Analyse personnalisée
        print(f"Intent: {intent}")
        print(f"Lignes: {len(df)}")
        print(df.head())
```

### 13. Pipeline d'Analyse Automatisé

```python
import schedule
import time

def daily_analysis():
    ados = ADOS()
    
    # Rapports quotidiens
    reports = {
        "top_customers": ados.process_intent(
            "Top 50 clients par CA des 7 derniers jours"
        ),
        "low_stock": ados.process_intent(
            "Produits avec stock critique (< 20)"
        ),
        "regional_performance": ados.process_intent(
            "Performance par région cette semaine"
        )
    }
    
    # Exporter en CSV/JSON
    for report_name, result in reports.items():
        if result["execution"].success:
            import pandas as pd
            df = pd.read_json(result["execution"].data)
            df.to_csv(f"reports/{report_name}_{date.today()}.csv")

# Planifier tous les jours à 8h
schedule.every().day.at("08:00").do(daily_analysis)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 14. API REST avec FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
ados = ADOS()

class QueryRequest(BaseModel):
    intent: str
    validate: bool = True

@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        result = ados.process_intent(
            request.intent, 
            validate=request.validate
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    return {
        "system": "ADOS",
        "status": "operational",
        "data_products": len(ados.knowledge_graph.metadata),
        "relationships": len(ados.knowledge_graph.relationships)
    }

# Lancer: uvicorn api:app --reload
```

### 15. Intégration avec Streamlit

```python
import streamlit as st
from ados_main import ADOS
import pandas as pd

st.set_page_config(page_title="ADOS Dashboard", layout="wide")

# Initialiser ADOS
@st.cache_resource
def init_ados():
    return ADOS()

ados = init_ados()

st.title("🚀 AI-Native Data Operating System")

# Sidebar
st.sidebar.header("System Status")
st.sidebar.metric("Data Products", len(ados.knowledge_graph.metadata))
st.sidebar.metric("Relationships", len(ados.knowledge_graph.relationships))

# Input utilisateur
user_query = st.text_input(
    "Posez votre question:",
    placeholder="Ex: Top 10 clients par CA"
)

if st.button("Analyser"):
    with st.spinner("Traitement en cours..."):
        result = ados.process_intent(user_query)
        
        # Afficher les étapes
        with st.expander("📋 Étapes de traitement"):
            for msg in result.get("messages", []):
                st.write(msg)
        
        # Afficher le SQL
        if result.get("plan"):
            st.code(result["plan"].sql_query, language="sql")
        
        # Afficher les résultats
        if result.get("execution") and result["execution"].success:
            df = pd.read_json(result["execution"].data)
            st.dataframe(df)
            
            # Visualisations automatiques
            if len(df.columns) >= 2:
                st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])
```

---

## 🎯 Exemples de Validation Trust Layer

### Exemple 1: Détection d'Incohérence de Types

**Requête:** "Compare les IDs clients avec les montants"

**Erreur détectée:**
```
🚨 [CRITICAL] type_compatibility: Jointure incompatible: 
   customer_domain.ID_Client (object) avec sales_domain.Montant (float64)
   
💡 Suggestion: Vérifiez la logique métier - impossible de joindre un ID avec un montant
```

### Exemple 2: Colonne Inexistante

**Requête:** "Montre-moi le profit par client"

**Erreur détectée:**
```
🚨 [CRITICAL] column_existence: Colonne 'Profit' introuvable dans 'sales_domain'

💡 Suggestion: Colonnes disponibles: ID_Transaction, ID_Client, ID_Produit, 
   Montant, Quantite, Date_Transaction, Statut
```

### Exemple 3: Opération Dangereuse

**Requête mal intentionnée:** "DELETE FROM customers"

**Erreur détectée:**
```
🚨 [CRITICAL] sql_safety: DELETE détecté - modification de données

💡 Suggestion: Seules les requêtes en lecture seule (SELECT) sont autorisées
```

---

## 📊 Métriques de Performance

### Temps de Réponse Moyen (sur données synthétiques)

| Opération | Temps |
|-----------|-------|
| Discovery | 1-2s |
| Planning (LLM) | 2-5s |
| Validation | 0.5s |
| Exécution DuckDB | 0.1-1s |
| **Total** | **4-9s** |

### Optimisations Possibles

- Cache des résultats LLM identiques
- Index DuckDB sur colonnes de jointure
- Batch processing pour requêtes multiples
- Utiliser gpt-3.5-turbo pour discovery (plus rapide)

---

## 🔧 Dépannage des Requêtes

### Problème: "Aucun résultat retourné"

**Solutions:**
1. Vérifier les filtres (peut-être trop restrictifs)
2. Reformuler la requête plus simplement
3. Vérifier les données sources

### Problème: "Timeout LLM"

**Solutions:**
1. Réduire la complexité de la requête
2. Augmenter le timeout dans le code
3. Utiliser un modèle plus rapide (gpt-3.5-turbo)

### Problème: "Jointure incorrecte"

**Solutions:**
1. Vérifier le Knowledge Graph: `ados.show_system_status()`
2. Ajouter manuellement une relation si manquante
3. Reformuler en précisant les liens entre entités
