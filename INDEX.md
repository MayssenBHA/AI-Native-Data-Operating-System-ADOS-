# 📚 Index de la Documentation ADOS

Bienvenue dans la documentation complète du projet **AI-Native Data Operating System (ADOS)**. Ce fichier vous guide vers les ressources appropriées selon vos besoins.

---

## 🚀 Par Niveau d'Expérience

### Débutant - Premier Contact
1. **[README.md](README.md)** ⭐ COMMENCEZ ICI
   - Vue d'ensemble du projet
   - Présentation des composants
   - Installation rapide
   
2. **[QUICKSTART.md](QUICKSTART.md)** ⚡ Installation en 5 minutes
   - Guide d'installation pas à pas
   - Configuration de l'environnement
   - Premiers exemples de requêtes

3. **[DEMO.md](DEMO.md)** 🎬 Démonstration complète
   - Scénario de bout en bout
   - Explication détaillée de chaque étape
   - Résultats attendus

### Intermédiaire - Utilisation
4. **[EXAMPLES.md](EXAMPLES.md)** 💡 15+ Cas d'Usage
   - Requêtes basiques, intermédiaires, avancées
   - Cas d'usage métier
   - Utilisation programmatique (API Python)
   - Intégration FastAPI et Streamlit

5. **[SUMMARY.md](SUMMARY.md)** 📋 Récapitulatif
   - Structure complète du projet
   - Démarrage en 3 étapes
   - Checklist de validation
   - Dépannage

### Avancé - Développement
6. **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️ Documentation Technique
   - Diagrammes d'architecture
   - API détaillée des modules
   - Modèles de données
   - Points d'extension
   - Performance et scalabilité

7. **[CONTRIBUTING.md](CONTRIBUTING.md)** 🔧 Guide du Contributeur
   - Ajouter un Data Product
   - Créer une règle de validation
   - Étendre le Knowledge Graph
   - Standards de code
   - Workflow de contribution

8. **[CHANGELOG.md](CHANGELOG.md)** 📝 Historique des Versions
   - Notes de version 1.0.0
   - Roadmap future
   - Breaking changes

---

## 📂 Par Type de Document

### Guides Utilisateur
- [QUICKSTART.md](QUICKSTART.md) - Installation express
- [EXAMPLES.md](EXAMPLES.md) - Exemples d'utilisation
- [DEMO.md](DEMO.md) - Démonstration interactive

### Documentation Technique
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture détaillée
- [README.md](README.md) - Vue d'ensemble technique

### Pour les Développeurs
- [CONTRIBUTING.md](CONTRIBUTING.md) - Comment contribuer
- [CHANGELOG.md](CHANGELOG.md) - Suivi des modifications

### Synthèse
- [SUMMARY.md](SUMMARY.md) - Récapitulatif global
- [INDEX.md](INDEX.md) - Ce fichier

---

## 🎯 Par Objectif

### "Je veux installer et tester rapidement"
1. [QUICKSTART.md](QUICKSTART.md) - Installation
2. `start.bat` (Windows) ou `start.sh` (Linux/Mac)
3. [DEMO.md](DEMO.md) - Test avec un exemple

### "Je veux comprendre comment ça marche"
1. [README.md](README.md) - Vue d'ensemble
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Détails techniques
3. [DEMO.md](DEMO.md) - Exemple commenté

### "Je veux l'utiliser dans mon projet"
1. [EXAMPLES.md](EXAMPLES.md) - Cas d'usage
2. [ARCHITECTURE.md](ARCHITECTURE.md) - API des modules
3. [CONTRIBUTING.md](CONTRIBUTING.md) - Extensions

### "Je veux contribuer au projet"
1. [CONTRIBUTING.md](CONTRIBUTING.md) - Guide complet
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture du code
3. [CHANGELOG.md](CHANGELOG.md) - Roadmap

### "J'ai un problème"
1. [SUMMARY.md](SUMMARY.md) - Section Dépannage
2. [QUICKSTART.md](QUICKSTART.md) - Section Dépannage
3. `ados.log` - Fichier de logs

---

## 📁 Structure des Fichiers du Projet

```
ADOS/
│
├── 📖 Documentation Principale
│   ├── README.md              ⭐ Commencez ici
│   ├── INDEX.md               🗂️ Ce fichier
│   └── SUMMARY.md             📋 Récapitulatif
│
├── 📚 Guides d'Utilisation
│   ├── QUICKSTART.md          ⚡ Installation 5 min
│   ├── EXAMPLES.md            💡 15+ cas d'usage
│   └── DEMO.md                🎬 Démo complète
│
├── 🔧 Documentation Technique
│   ├── ARCHITECTURE.md        🏗️ Architecture détaillée
│   ├── CONTRIBUTING.md        👥 Guide contributeur
│   └── CHANGELOG.md           📝 Historique versions
│
├── 🚀 Scripts Exécutables
│   ├── ados_main.py           🖥️ CLI principal
│   ├── ados_interface.py      🌐 Interface Web
│   ├── test_ados.py           🧪 Suite de tests
│   ├── start.bat              🪟 Launcher Windows
│   └── start.sh               🐧 Launcher Linux/Mac
│
├── 🧩 Modules Core (modules/)
│   ├── data_generator.py      📊 Génération données
│   ├── knowledge_graph.py     🧠 Graphe connaissances
│   ├── intent_compiler.py     ⚡ Compilateur LangGraph
│   └── trust_layer.py         🛡️ Validation & audit
│
├── ⚙️ Configuration
│   ├── requirements.txt       📦 Dépendances Python
│   ├── .env.example           🔑 Template config API
│   ├── .gitignore             🚫 Fichiers ignorés
│   └── .chainlit/config.toml  🌐 Config Chainlit
│
└── 📊 Données (data/)
    ├── customer_domain.parquet
    ├── logistics_domain.parquet
    └── sales_domain.parquet
```

---

## 🔍 Par Composant Technique

### Data Mesh Simulator
- **Code** : [modules/data_generator.py](modules/data_generator.py)
- **Documentation** : [ARCHITECTURE.md#DataMeshSimulator](ARCHITECTURE.md)
- **Exemples** : [EXAMPLES.md#Génération de Données](EXAMPLES.md)

### Living Knowledge Graph
- **Code** : [modules/knowledge_graph.py](modules/knowledge_graph.py)
- **Documentation** : [ARCHITECTURE.md#LivingKnowledgeGraph](ARCHITECTURE.md)
- **Démo** : [DEMO.md#Étape 2](DEMO.md)

### Intent Compiler (LangGraph)
- **Code** : [modules/intent_compiler.py](modules/intent_compiler.py)
- **Documentation** : [ARCHITECTURE.md#IntentCompiler](ARCHITECTURE.md)
- **Workflow** : [DEMO.md#Étape 3](DEMO.md)

### Trust Layer
- **Code** : [modules/trust_layer.py](modules/trust_layer.py)
- **Documentation** : [ARCHITECTURE.md#TrustLayer](ARCHITECTURE.md)
- **Validation** : [DEMO.md#Étape 4](DEMO.md)

---

## 📊 Diagrammes et Visualisations

### Architecture Globale
Voir : [ARCHITECTURE.md - Vue d'Ensemble](ARCHITECTURE.md)

### Flux de Données
Voir : [ARCHITECTURE.md - Flux de Traitement](ARCHITECTURE.md)

### Workflow LangGraph
Voir : [DEMO.md - Workflow Complet](DEMO.md)

### Diagramme de Relations
Voir : [DEMO.md - Knowledge Graph](DEMO.md)

---

## 🧪 Tests et Validation

### Suite de Tests Complète
- **Script** : [test_ados.py](test_ados.py)
- **Commande** : `python test_ados.py`
- **Documentation** : [CONTRIBUTING.md#Tests](CONTRIBUTING.md)

### Tests par Module
```bash
python -m modules.data_generator
python -m modules.knowledge_graph
python -m modules.trust_layer
```

---

## 🛠️ Commandes Rapides

### Installation
```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh && ./start.sh
```

### Lancement
```bash
# Mode CLI
python ados_main.py

# Mode Web
chainlit run ados_interface.py

# Mode Demo
python ados_main.py --demo
```

### Tests
```bash
python test_ados.py
```

---

## 📖 Glossaire des Termes

| Terme | Définition | Documentation |
|-------|------------|---------------|
| **ADOS** | AI-Native Data Operating System | [README.md](README.md) |
| **Data Product** | Fichier Parquet avec données thématiques | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Knowledge Graph** | Graphe des relations entre données | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Intent Compiler** | Agent LangGraph qui compile les intentions | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Trust Layer** | Couche de validation et audit | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **LangGraph** | Framework d'orchestration d'agents | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **DuckDB** | Moteur de requêtes analytiques | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## 🌐 Ressources Externes

### Technologies Utilisées
- **LangGraph** : https://langchain-ai.github.io/langgraph/
- **DuckDB** : https://duckdb.org/docs/
- **NetworkX** : https://networkx.org/
- **Chainlit** : https://docs.chainlit.io/
- **Faker** : https://faker.readthedocs.io/

### Concepts
- **Data Mesh** : https://www.datamesh-architecture.com/
- **Knowledge Graphs** : https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/
- **LLM Agents** : https://www.anthropic.com/research

---

## 📞 Obtenir de l'Aide

### Documentation
1. Consultez [QUICKSTART.md](QUICKSTART.md) pour les problèmes d'installation
2. Lisez [EXAMPLES.md](EXAMPLES.md) pour les exemples d'utilisation
3. Vérifiez [SUMMARY.md](SUMMARY.md) pour le dépannage

### Logs
- Fichier : `ados.log`
- Niveau : Configurable dans chaque module

### Tests
```bash
python test_ados.py
```

---

## 🗺️ Parcours Recommandés

### Parcours "Quick Start" (15 min)
1. [README.md](README.md) - 3 min
2. [QUICKSTART.md](QUICKSTART.md) - 5 min
3. Installation - 5 min
4. Premier test - 2 min

### Parcours "Utilisateur" (1h)
1. [README.md](README.md) - 5 min
2. [QUICKSTART.md](QUICKSTART.md) - 10 min
3. Installation et tests - 15 min
4. [EXAMPLES.md](EXAMPLES.md) - 20 min
5. Expérimentation - 10 min

### Parcours "Développeur" (3h)
1. [README.md](README.md) - 10 min
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 45 min
3. [DEMO.md](DEMO.md) - 30 min
4. [CONTRIBUTING.md](CONTRIBUTING.md) - 30 min
5. Code exploration - 45 min
6. Extensions - 30 min

---

## ✅ Checklist d'Onboarding

### Niveau 1 - Installation
- [ ] Lu [README.md](README.md)
- [ ] Suivi [QUICKSTART.md](QUICKSTART.md)
- [ ] Environnement configuré
- [ ] Tests passés avec succès
- [ ] Premier exemple testé

### Niveau 2 - Utilisation
- [ ] Exploré [EXAMPLES.md](EXAMPLES.md)
- [ ] Testé 5+ requêtes différentes
- [ ] Compris le workflow dans [DEMO.md](DEMO.md)
- [ ] Lancé l'interface Web

### Niveau 3 - Maîtrise
- [ ] Lu [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Compris chaque module
- [ ] Testé chaque module indépendamment
- [ ] Écrit une extension personnalisée

### Niveau 4 - Contribution
- [ ] Lu [CONTRIBUTING.md](CONTRIBUTING.md)
- [ ] Ajouté un Data Product
- [ ] Créé une règle de validation
- [ ] Soumis une pull request

---

**Navigation Rapide** : [README](README.md) | [Installation](QUICKSTART.md) | [Exemples](EXAMPLES.md) | [Architecture](ARCHITECTURE.md) | [Contribuer](CONTRIBUTING.md)

**Dernière mise à jour** : 2026-02-16
