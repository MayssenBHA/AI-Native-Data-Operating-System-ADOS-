# Changelog - ADOS (AI-Native Data Operating System)

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [1.0.0] - 2026-02-16

### ✨ Ajouté

#### Core System
- **Data Mesh Simulator** : Génération de 3 Data Products synthétiques (Customer, Logistics, Sales)
  - Support de 1000 clients, 200 produits, 5000 transactions
  - Données cohérentes avec relations intégrées
  - Export au format Parquet optimisé

- **Living Knowledge Graph** : Découverte automatique des relations sémantiques
  - Scan automatique des fichiers Parquet
  - Détection de jointures basée sur les noms de colonnes
  - Calcul du chevauchement de valeurs pour validation
  - Représentation avec NetworkX
  - Support de Neo4j (optionnel)

- **Intent Compiler** : Agent LangGraph multi-étapes
  - Phase Discovery : Identification des fichiers et colonnes nécessaires
  - Phase Planning : Génération de requêtes SQL DuckDB
  - Phase Execution : Matérialisation et exécution
  - Support de GPT-4 et GPT-3.5-turbo

- **Trust Layer** : Validation et audit
  - 6 règles de validation implémentées :
    1. Existence des fichiers
    2. Existence des colonnes
    3. Syntaxe SQL basique
    4. Compatibilité des types dans les jointures
    5. Détection d'opérations dangereuses (DROP, DELETE, etc.)
    6. Cohérence sémantique via LLM (optionnel)
  - Niveaux de sévérité : CRITICAL, WARNING, INFO
  - Génération de rapports d'audit détaillés

#### Interfaces
- **CLI Interactive** ([ados_main.py](ados_main.py))
  - Mode interactif avec commandes (status, examples, quit)
  - Mode démo avec exemples pré-configurés
  - Affichage formaté des résultats
  - Logs complets dans ados.log

- **Interface Web Chainlit** ([ados_interface.py](ados_interface.py))
  - Chat conversationnel
  - Visualisation du Knowledge Graph
  - Export des résultats en JSON
  - Support du Markdown et code highlighting

#### Outils de Développement
- **Suite de Tests** ([test_ados.py](test_ados.py))
  - 6 catégories de tests
  - Validation de tous les composants
  - Rapport coloré avec colorama
  - Support Windows/Linux/Mac

- **Scripts de Démarrage**
  - [start.bat](start.bat) pour Windows
  - [start.sh](start.sh) pour Linux/Mac
  - Configuration automatique de l'environnement
  - Menu interactif

#### Documentation
- [README.md](README.md) : Vue d'ensemble et guide d'installation
- [QUICKSTART.md](QUICKSTART.md) : Guide d'installation en 5 minutes
- [ARCHITECTURE.md](ARCHITECTURE.md) : Documentation technique complète
- [EXAMPLES.md](EXAMPLES.md) : 15+ exemples d'utilisation
- [.env.example](.env.example) : Template de configuration

### 🔧 Technique

#### Stack Technologique
- **Orchestration** : LangGraph 0.0.20
- **Query Engine** : DuckDB 0.10.0
- **Knowledge Graph** : NetworkX 3.2.1
- **LLM Framework** : LangChain 0.1.6, LangChain-OpenAI 0.0.5
- **Data Generation** : Faker 22.6.0, Pandas 2.2.0
- **Interface** : Chainlit 1.0.200, Streamlit 1.31.0

#### Architecture
- Workflow cyclique avec LangGraph
- Séparation des préoccupations (modules découplés)
- Support de l'exécution en mémoire (DuckDB)
- Cache des métadonnées pour performance

### 📊 Capacités

- **Nombres de Data Products** : 3 (extensible)
- **Volumétrie de test** : 
  - 1000 clients
  - 200 produits
  - 5000 transactions
- **Temps de réponse moyen** : 4-9 secondes (incluant LLM)
- **Langages supportés** : Français (données et interface)

### 🔐 Sécurité

- Validation systématique des requêtes SQL
- Blocage des opérations d'écriture (DROP, DELETE, UPDATE)
- Vérification de la cohérence des types
- Audit trail complet
- Variables d'environnement pour clés API

### 📦 Packaging

- `requirements.txt` avec versions fixées
- `.gitignore` configuré pour Python
- Structure modulaire dans `modules/`
- Séparation données/code
- Support de l'environnement virtuel

### 🧪 Tests

- Tests unitaires pour chaque module
- Tests d'intégration end-to-end
- Génération de données de test isolées
- Nettoyage automatique après tests

### 📝 Logging

- Logs structurés avec timestamps
- Niveaux : DEBUG, INFO, WARNING, ERROR
- Sortie fichier (`ados.log`) + console
- Traçabilité complète du workflow

### 🌍 Internationalisation

- Interface en français
- Données synthétiques françaises (noms, régions)
- Documentation en français
- Support facile d'autres langues via Faker

---

## [Prévu] - Roadmap Future

### v1.1.0 (Q2 2026)
- [ ] Support de Neo4j natif
- [ ] Cache Redis pour résultats LLM
- [ ] API REST avec FastAPI
- [ ] Authentification utilisateur
- [ ] Export multi-formats (CSV, Excel, PDF)

### v1.2.0 (Q3 2026)
- [ ] Support de fichiers CSV/JSON en entrée
- [ ] Connexion à bases de données externes (PostgreSQL, MySQL)
- [ ] Visualisations interactives (Plotly)
- [ ] Scheduling de rapports automatiques
- [ ] Streaming de résultats pour gros datasets

### v2.0.0 (Q4 2026)
- [ ] Support multi-langage (Anglais, Espagnol)
- [ ] Fine-tuning du modèle LLM sur domaine métier
- [ ] Mode offline avec modèles locaux (Llama, Mistral)
- [ ] Optimisations pour Big Data (PySpark)
- [ ] Déploiement Cloud (Azure, AWS, GCP)

---

## Notes de Version

### Installation
```bash
pip install -r requirements.txt
```

### Migration depuis version précédente
N/A (première version)

### Breaking Changes
Aucun

### Dépréciations
Aucune

### Contributeurs
- Architecture : Senior Data Architect
- Développement : AI-Assisted Development
- Tests : Automated Testing Suite

---

## Support

Pour signaler un bug ou demander une fonctionnalité :
1. Ouvrir une issue sur le repository
2. Décrire le contexte et les étapes de reproduction
3. Inclure les logs (`ados.log`)

Pour des questions :
- Consulter [ARCHITECTURE.md](ARCHITECTURE.md)
- Voir les exemples dans [EXAMPLES.md](EXAMPLES.md)
- Check le [QUICKSTART.md](QUICKSTART.md)
