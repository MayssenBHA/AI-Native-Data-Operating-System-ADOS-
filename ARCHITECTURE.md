# Architecture ADOS - Documentation Technique

## 🏗️ Vue d'Ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌─────────────────────┐    ┌────────────────────────────┐ │
│  │  CLI Interface      │    │  Chainlit Web Interface    │ │
│  │  (ados_main.py)     │    │  (ados_interface.py)       │ │
│  └──────────┬──────────┘    └─────────────┬──────────────┘ │
└─────────────┼──────────────────────────────┼────────────────┘
              │                              │
              └───────────┬──────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                   ORCHESTRATION LAYER                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           LangGraph Agent Workflow                      │ │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────┐        │ │
│  │  │Discovery │─▶│ Planning  │─▶│  Execution   │        │ │
│  │  │  Node    │  │   Node    │  │    Node      │        │ │
│  │  └──────────┘  └───────────┘  └──────────────┘        │ │
│  │                                                         │ │
│  │  (modules/intent_compiler.py)                          │ │
│  └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                 │
        ▼                ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────┐
│   TRUST      │  │  KNOWLEDGE   │  │   QUERY     │
│   LAYER      │  │    GRAPH     │  │   ENGINE    │
│              │  │              │  │             │
│ Validation & │  │  NetworkX    │  │   DuckDB    │
│   Audit      │  │  Semantic    │  │  Analytics  │
│              │  │  Discovery   │  │             │
│ (trust_      │  │ (knowledge_  │  │             │
│  layer.py)   │  │  graph.py)   │  │             │
└──────────────┘  └──────┬───────┘  └─────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Data Mesh Simulator                      │   │
│  │                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │   │
│  │  │  Customer    │  │  Logistics   │  │  Sales   │  │   │
│  │  │   Domain     │  │   Domain     │  │  Domain  │  │   │
│  │  │  (Parquet)   │  │  (Parquet)   │  │(Parquet) │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │   │
│  │                                                      │   │
│  │  (modules/data_generator.py)                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Flux de Traitement d'une Intention

```
1. USER INPUT
   │ "Analyse l'impact des stocks bas sur mes clients VIP"
   │
   ▼
2. INTENT COMPILER (LangGraph)
   │
   ├─▶ [DISCOVERY NODE]
   │   ├─ Parse intention avec LLM
   │   ├─ Consulte Knowledge Graph
   │   └─▶ Identifie: [customer_domain, logistics_domain, sales_domain]
   │
   ├─▶ [PLANNING NODE]
   │   ├─ Analyse relations sémantiques
   │   ├─ Génère plan de jointure
   │   └─▶ Produit requête SQL DuckDB
   │
   └─▶ [EXECUTION NODE]
       ├─ Valide avec Trust Layer ────┐
       │                               │
       ├─ Exécute avec DuckDB         │
       └─▶ Retourne résultat           │
                                       │
3. TRUST LAYER VALIDATION  ◀──────────┘
   │
   ├─ Vérification existence fichiers/colonnes
   ├─ Validation syntaxe SQL
   ├─ Contrôle compatibilité types
   ├─ Détection opérations dangereuses
   └─▶ Rapport d'audit
   │
   ▼
4. OUTPUT
   └─ Données + Métadonnées + Audit
```

## 🔧 API des Modules

### 1. DataMeshSimulator

```python
from modules.data_generator import DataMeshSimulator

simulator = DataMeshSimulator(seed=42, output_dir="data")

# Générer tous les domaines
domains = simulator.generate_all_domains()
# Returns: {"customer": DataFrame, "logistics": DataFrame, "sales": DataFrame}

# Générer un seul domaine
customer_df = simulator.generate_customer_domain()

# Obtenir les métadonnées
metadata = simulator.get_metadata()
```

### 2. LivingKnowledgeGraph

```python
from modules.knowledge_graph import LivingKnowledgeGraph

kg = LivingKnowledgeGraph(data_dir="data")

# Scanner les fichiers
dataframes = kg.scan_data_products()

# Découvrir les relations
relationships = kg.discover_relationships(dataframes)

# Trouver un chemin de jointure
path = kg.get_join_path("customer_domain", "sales_domain")

# Obtenir les colonnes de jointure
join_cols = kg.get_join_columns_for_path(path)

# Visualiser le graphe
print(kg.visualize_graph())
```

### 3. IntentCompiler (LangGraph)

```python
from modules.intent_compiler import IntentCompiler

compiler = IntentCompiler(
    knowledge_graph=kg,
    data_dir="data",
    model_name="gpt-4-turbo-preview"
)

# Compiler une intention
result = compiler.compile_intent(
    "Montre-moi les 10 meilleurs clients"
)

# Structure du résultat:
# {
#     "intent": str,
#     "discovery": DataDiscovery,
#     "plan": JoinPlan,
#     "execution": ExecutionResult,
#     "messages": List[str],
#     "validation_passed": bool
# }
```

### 4. TrustLayer

```python
from modules.trust_layer import TrustLayer

trust_layer = TrustLayer(knowledge_graph=kg, llm=optional_llm)

# Valider un plan d'exécution
passed, issues = trust_layer.validate_execution_plan(
    sql_query="SELECT ...",
    required_files=["customer_domain"],
    required_columns={"customer_domain": ["ID_Client", "Nom"]}
)

# Générer un rapport d'audit
report = trust_layer.generate_audit_report(issues)
```

## 🧬 Modèles de Données

### DataDiscovery
```python
class DataDiscovery(BaseModel):
    required_files: List[str]
    required_columns: Dict[str, List[str]]
    reasoning: str
```

### JoinPlan
```python
class JoinPlan(BaseModel):
    sql_query: str
    join_path: List[str]
    explanation: str
```

### ExecutionResult
```python
class ExecutionResult(BaseModel):
    success: bool
    data: Optional[str]  # JSON
    error: Optional[str]
    rows_count: int
```

### ValidationIssue
```python
class ValidationIssue:
    severity: ValidationSeverity  # CRITICAL | WARNING | INFO
    rule: str
    message: str
    suggestion: Optional[str]
```

## 🔐 Règles de Validation (Trust Layer)

1. **file_existence**: Vérifie que les fichiers existent
2. **column_existence**: Vérifie que les colonnes existent
3. **sql_syntax**: Validation syntaxe SQL basique
4. **type_compatibility**: Cohérence des types dans les jointures
5. **sql_safety**: Détection opérations dangereuses (DROP, DELETE, etc.)
6. **semantic_coherence**: Validation LLM de la logique métier

## 🎯 Points d'Extension

### Ajouter un Nouveau Data Product

```python
# Dans data_generator.py
def generate_new_domain(self) -> pd.DataFrame:
    data = {
        "ID_New": [...],
        "Column1": [...],
        # ...
    }
    df = pd.DataFrame(data)
    output_path = self.output_dir / "new_domain.parquet"
    df.to_parquet(output_path, index=False)
    return df
```

### Ajouter une Règle de Validation

```python
# Dans trust_layer.py
def _validate_custom_rule(self, sql_query: str) -> List[ValidationIssue]:
    issues = []
    # Votre logique de validation
    if condition:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            rule="custom_rule",
            message="Description"
        ))
    return issues

# Puis l'ajouter dans validate_execution_plan()
issues.extend(self._validate_custom_rule(sql_query))
```

### Utiliser Neo4j au lieu de NetworkX

```python
# Installer neo4j
pip install neo4j

# Modifier knowledge_graph.py
from neo4j import GraphDatabase

class LivingKnowledgeGraph:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        # Adapter les méthodes pour utiliser Cypher queries
```

## 📈 Performance et Scalabilité

### Optimisations Actuelles
- DuckDB en mémoire pour requêtes rapides
- NetworkX pour graphes < 10k nœuds
- Cache des métadonnées

### Pour Passer à l'Échelle
- Utiliser Neo4j pour graphes > 100k nœuds
- DuckDB persistant pour datasets > 1GB
- Paralléliser discovery avec async/await
- Implémenter cache Redis pour résultats

## 🧪 Tests Recommandés

```bash
# Tests unitaires
python test_ados.py

# Test de chaque module
python -m modules.data_generator
python -m modules.knowledge_graph
python -m modules.trust_layer

# Test d'intégration
python ados_main.py --demo
```

## 📝 Logs et Monitoring

Les logs sont écrits dans:
- `ados.log` (fichier)
- Console (stdout)

Niveau de log configurable dans chaque module:
```python
logging.basicConfig(level=logging.DEBUG)  # Pour plus de détails
```
