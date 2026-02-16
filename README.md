# AI-Native Data Operating System (ADOS)

## 🎯 Objectif
Prototype d'un système autonome qui transforme une intention en langage naturel en plan d'exécution de données, basé sur une architecture 100% Open Source.

## 🏗️ Architecture

### Stack Technique
- **Kernel & Orchestration**: LangGraph
- **Moteur de Requêtes**: DuckDB
- **Knowledge Graph**: NetworkX (in-memory)
- **Génération de Données**: Faker + Pandas
- **Interface**: Chainlit

### Composants Principaux
1. **Data Mesh Simulator**: Génération de Data Products décentralisés
2. **Living Knowledge Graph**: Découverte automatique des relations sémantiques
3. **Compilateur d'Intention**: Agent LLM avec LangGraph
4. **Trust Layer**: Validation et audit des plans d'exécution

## 🚀 Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec votre clé OpenAI
```

## 📦 Utilisation

### Mode Script Autonome
```bash
python ados_main.py
```

### Mode Interface Chainlit
```bash
chainlit run ados_interface.py
```

## 📊 Data Products Générés
- `sales_domain.parquet`: Transactions commerciales
- `logistics_domain.parquet`: Données logistiques
- `customer_domain.parquet`: Profils clients

## 🧠 Exemples de Requêtes
- "Analyse l'impact des stocks bas sur mes clients VIP"
- "Montre-moi les ventes par région pour les produits en rupture"
- "Identifie les clients fidèles avec des délais de livraison élevés"

## 📁 Structure du Projet
```
.
├── ados_main.py              # Script principal auto-exécutable
├── modules/
│   ├── data_generator.py     # Génération de données synthétiques
│   ├── knowledge_graph.py    # Living Knowledge Graph
│   ├── intent_compiler.py    # Compilateur d'intention avec LangGraph
│   └── trust_layer.py        # Judge Agent & validation
├── data/                     # Dossier des Data Products
├── ados_interface.py         # Interface Chainlit
└── requirements.txt
```

## 🔍 Fonctionnalités Avancées
- Découverte automatique de schéma
- Jointures intelligentes basées sur la sémantique
- Validation de cohérence des types
- Audit des plans d'exécution
- Matérialisation dynamique de vues DuckDB
