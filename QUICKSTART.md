# Guide d'Installation & Utilisation Rapide - ADOS

## 🚀 Installation Express (5 minutes)

### Prérequis
- Python 3.9+
- Clé API OpenAI (https://platform.openai.com/api-keys)

### Installation

```bash
# 1. Créer un environnement virtuel
python -m venv venv

# 2. Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
# Créer le fichier .env à partir du template
cp .env.example .env

# 5. Éditer .env et ajouter votre clé OpenAI
# OPENAI_API_KEY=sk-your-key-here
```

## 🎯 Utilisation

### Mode 1: Script Autonome (Ligne de commande)

```bash
# Mode interactif
python ados_main.py

# Mode démo
python ados_main.py --demo
```

**Commandes disponibles:**
- Tapez votre requête en langage naturel
- `status` - Afficher l'état du système
- `examples` - Voir des exemples de requêtes
- `quit` ou `exit` - Quitter

### Mode 2: Interface Web Chainlit

```bash
chainlit run ados_interface.py
```

Ouvrez votre navigateur à l'adresse affichée (généralement http://localhost:8000)

## 📝 Exemples de Requêtes

```
Montre-moi les 10 meilleurs clients par montant total
Analyse l'impact des stocks bas sur mes clients VIP
Quels produits ont un délai de livraison supérieur à 10 jours ?
Liste les clients d'Île-de-France avec leurs transactions
Identifie les clients fidèles (score > 80) avec des achats récents
```

## 🔧 Test des Modules Individuels

```bash
# Tester le générateur de données
python -m modules.data_generator

# Tester le Knowledge Graph
python -m modules.knowledge_graph

# Tester la Trust Layer
python -m modules.trust_layer
```

## 📊 Structure des Données Générées

Le système génère automatiquement 3 Data Products:

1. **customer_domain.parquet** (1000 clients)
   - ID_Client, Nom, Score_Fidélité, Région, Email, Date_Inscription

2. **logistics_domain.parquet** (200 produits)
   - ID_Produit, Stock, Entrepôt, Délai_Livraison, Coût_Stockage

3. **sales_domain.parquet** (5000 transactions)
   - ID_Transaction, ID_Client, ID_Produit, Montant, Quantité, Date

## 🛠️ Dépannage

### Erreur: "OPENAI_API_KEY non définie"
➡️ Créez un fichier `.env` et ajoutez votre clé API OpenAI

### Erreur: "No module named 'langgraph'"
➡️ Installez toutes les dépendances: `pip install -r requirements.txt`

### Erreur: "Fichiers Parquet introuvables"
➡️ Le système génère automatiquement les données au premier lancement

### Performance lente
➡️ Utilisez `gpt-3.5-turbo` dans `.env` au lieu de `gpt-4-turbo-preview`

## 🏗️ Architecture Technique

```
ADOS
├── Data Mesh Simulator → Génère les Data Products
├── Living Knowledge Graph → Découvre les relations (NetworkX)
├── Intent Compiler → Agent LangGraph (Discovery → Planning → Execution)
├── Trust Layer → Validation & audit
└── Query Engine → DuckDB pour l'exécution
```

## 📚 Documentation Avancée

Voir le README.md principal pour plus de détails sur:
- Architecture complète
- Diagramme de flux
- API des modules
- Extension du système
