# Guide de Contribution - ADOS

Merci de votre intérêt pour contribuer à ADOS ! Ce guide vous aidera à comprendre comment étendre et améliorer le système.

---

## 📋 Table des Matières

1. [Architecture du Code](#architecture-du-code)
2. [Ajouter un Data Product](#ajouter-un-data-product)
3. [Créer une Règle de Validation](#créer-une-règle-de-validation)
4. [Étendre le Knowledge Graph](#étendre-le-knowledge-graph)
5. [Ajouter un Nœud LangGraph](#ajouter-un-nœud-langgraph)
6. [Tests et Qualité](#tests-et-qualité)
7. [Standards de Code](#standards-de-code)

---

## 🏗️ Architecture du Code

### Principes de Design

1. **Modularité** : Chaque composant est indépendant
2. **Testabilité** : Chaque module peut être testé isolément
3. **Extensibilité** : Ajout facile de nouvelles fonctionnalités
4. **Documentation** : Code auto-documenté avec docstrings

### Diagramme de Dépendances

```
ados_main.py
    ├── modules/data_generator.py     (indépendant)
    ├── modules/knowledge_graph.py    (dépend de data_generator)
    ├── modules/intent_compiler.py    (dépend de knowledge_graph)
    └── modules/trust_layer.py        (dépend de knowledge_graph)

ados_interface.py → importe tous les modules
```

---

## 🆕 Ajouter un Data Product

### Étape 1 : Définir le Schéma

Éditez `modules/data_generator.py` :

```python
def generate_product_catalog_domain(self) -> pd.DataFrame:
    """
    Génère le Data Product: product_catalog_domain
    
    Returns:
        DataFrame avec colonnes: ID_Produit, Nom_Produit, Categorie, Prix_Unitaire
    """
    logger.info("Génération du domaine Product Catalog...")
    
    categories = ["Électronique", "Vêtements", "Alimentation", "Maison", "Sport"]
    
    data = {
        "ID_Produit": self.product_ids,  # Réutilise les IDs existants
        "Nom_Produit": [self.fake.catch_phrase() for _ in range(self.num_products)],
        "Categorie": np.random.choice(categories, self.num_products),
        "Prix_Unitaire": np.round(np.random.uniform(5, 500, self.num_products), 2),
        "Date_Creation": [self.fake.date_between(start_date='-5y', end_date='today') 
                          for _ in range(self.num_products)]
    }
    
    df = pd.DataFrame(data)
    output_path = self.output_dir / "product_catalog_domain.parquet"
    df.to_parquet(output_path, index=False)
    
    logger.info("✓ product_catalog_domain.parquet créé (%d lignes)", len(df))
    return df
```

### Étape 2 : Intégrer dans `generate_all_domains()`

```python
def generate_all_domains(self) -> Dict[str, pd.DataFrame]:
    logger.info("=== Génération de tous les Data Products ===")
    
    domains = {
        "customer": self.generate_customer_domain(),
        "logistics": self.generate_logistics_domain(),
        "sales": self.generate_sales_domain(),
        "product_catalog": self.generate_product_catalog_domain(),  # ⬅️ Ajout
    }
    
    logger.info("=== Génération terminée ===")
    return domains
```

### Étape 3 : Mettre à Jour les Métadonnées

Éditez la méthode `get_metadata()` :

```python
def get_metadata(self) -> Dict:
    return {
        "num_customers": self.num_customers,
        "num_products": self.num_products,
        "num_transactions": self.num_transactions,
        "output_directory": str(self.output_dir),
        "files": [
            "customer_domain.parquet",
            "logistics_domain.parquet",
            "sales_domain.parquet",
            "product_catalog_domain.parquet",  # ⬅️ Ajout
        ]
    }
```

### Étape 4 : Tester

```python
# Test du nouveau domaine
if __name__ == "__main__":
    simulator = DataMeshSimulator()
    product_catalog = simulator.generate_product_catalog_domain()
    print(product_catalog.head())
```

---

## ✅ Créer une Règle de Validation

### Étape 1 : Définir la Règle

Éditez `modules/trust_layer.py` et ajoutez une nouvelle méthode :

```python
def _validate_performance_risk(self, sql_query: str) -> List[ValidationIssue]:
    """Détecte les requêtes potentiellement lentes"""
    issues = []
    
    # Règle 1: Jointures multiples sans LIMIT
    join_count = sql_query.upper().count("JOIN")
    has_limit = "LIMIT" in sql_query.upper()
    
    if join_count >= 3 and not has_limit:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING,
            rule="performance_risk",
            message=f"Requête avec {join_count} jointures sans LIMIT - risque de performance",
            suggestion="Ajoutez une clause LIMIT pour limiter les résultats"
        ))
    
    # Règle 2: SELECT * sur fichiers volumineux
    if "SELECT *" in sql_query.upper() and not has_limit:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO,
            rule="performance_risk",
            message="SELECT * sans LIMIT - peut retourner beaucoup de données",
            suggestion="Sélectionnez uniquement les colonnes nécessaires"
        ))
    
    return issues
```

### Étape 2 : Intégrer dans le Pipeline de Validation

Dans la méthode `validate_execution_plan()`, ajoutez :

```python
def validate_execution_plan(self, ...):
    # ... code existant ...
    
    # Règle 7: Détection de risques de performance
    issues.extend(self._validate_performance_risk(sql_query))
    
    # ... reste du code ...
```

### Étape 3 : Tester la Règle

```python
# Test de la nouvelle règle
trust_layer = TrustLayer(knowledge_graph=kg)

risky_sql = """
SELECT *
FROM 'data/customer_domain.parquet' AS c
JOIN 'data/sales_domain.parquet' AS s ON c.ID_Client = s.ID_Client
JOIN 'data/logistics_domain.parquet' AS l ON s.ID_Produit = l.ID_Produit
"""

passed, issues = trust_layer.validate_execution_plan(
    sql_query=risky_sql,
    required_files=["customer_domain", "sales_domain", "logistics_domain"],
    required_columns={}
)

for issue in issues:
    if issue.rule == "performance_risk":
        print(f"✓ Règle détectée: {issue.message}")
```

---

## 🧠 Étendre le Knowledge Graph

### Ajouter une Méthode de Découverte

Éditez `modules/knowledge_graph.py` :

```python
def discover_semantic_similarities(self, dataframes: Dict[str, pd.DataFrame]) -> List[Relationship]:
    """
    Découvre des relations basées sur la similarité sémantique des noms de colonnes
    
    Uses:
        - Calcul de distance de Levenshtein
        - Embeddings de colonnes (optionnel)
    """
    relationships = []
    
    from difflib import SequenceMatcher
    
    files = list(dataframes.keys())
    
    for i, file1 in enumerate(files):
        for file2 in files[i+1:]:
            df1 = dataframes[file1]
            df2 = dataframes[file2]
            
            for col1 in df1.columns:
                for col2 in df2.columns:
                    # Calcul de similarité
                    similarity = SequenceMatcher(None, col1.lower(), col2.lower()).ratio()
                    
                    if similarity > 0.8 and similarity < 1.0:  # Presque identiques
                        rel = Relationship(
                            source_file=file1,
                            source_column=col1,
                            target_file=file2,
                            target_column=col2,
                            relationship_type="semantic_similarity",
                            confidence=similarity
                        )
                        relationships.append(rel)
                        logger.info("  Similarité trouvée: %s.%s ≈ %s.%s (conf=%.2f)", 
                                  file1, col1, file2, col2, similarity)
    
    return relationships
```

### Intégrer dans `discover_relationships()`

```python
def discover_relationships(self, dataframes: Dict[str, pd.DataFrame]) -> List[Relationship]:
    logger.info("Découverte des relations sémantiques...")
    
    self.relationships = []
    
    # Méthode 1: Correspondances exactes et ID
    # ... code existant ...
    
    # Méthode 2: Similarités sémantiques
    semantic_rels = self.discover_semantic_similarities(dataframes)
    self.relationships.extend(semantic_rels)
    
    logger.info("✓ %d relations découvertes", len(self.relationships))
    return self.relationships
```

---

## 🔄 Ajouter un Nœud LangGraph

### Étape 1 : Définir le Nœud

Éditez `modules/intent_compiler.py` :

```python
def _optimization_node(self, state: GraphState) -> GraphState:
    """
    Nœud 4: Optimisation de la requête SQL
    
    Rôle:
        - Analyser le plan SQL
        - Suggérer des optimisations (index, réorganisation)
        - Réécrire la requête si nécessaire
    """
    logger.info("⚡ Phase OPTIMIZATION: Analyse du plan")
    
    join_plan = state["join_plan"]
    if not join_plan:
        state["messages"].append("⚠️ Pas de plan à optimiser")
        return state
    
    sql_query = join_plan.sql_query
    
    # Analyse simple: détection de patterns non optimaux
    optimizations = []
    
    # Pattern 1: SELECT * → SELECT colonnes spécifiques
    if "SELECT *" in sql_query:
        optimizations.append("Remplacer SELECT * par sélection explicite de colonnes")
    
    # Pattern 2: Pas de LIMIT → ajouter LIMIT
    if "LIMIT" not in sql_query.upper():
        optimizations.append("Ajouter une clause LIMIT pour limiter les résultats")
    
    if optimizations:
        state["messages"].append(f"💡 Optimisations suggérées: {len(optimizations)}")
        for opt in optimizations:
            logger.info("  - %s", opt)
    else:
        state["messages"].append("✓ Requête déjà optimale")
    
    return state
```

### Étape 2 : Intégrer dans le Workflow

```python
def _build_workflow(self) -> StateGraph:
    workflow = StateGraph(GraphState)
    
    # Ajout des nœuds
    workflow.add_node("discovery", self._discovery_node)
    workflow.add_node("planning", self._planning_node)
    workflow.add_node("optimization", self._optimization_node)  # ⬅️ Nouveau
    workflow.add_node("execution", self._execution_node)
    
    # Définition des arêtes
    workflow.set_entry_point("discovery")
    workflow.add_edge("discovery", "planning")
    workflow.add_edge("planning", "optimization")  # ⬅️ Nouveau chemin
    workflow.add_edge("optimization", "execution")
    workflow.add_edge("execution", END)
    
    return workflow
```

### Étape 3 : Mettre à Jour l'État

Ajoutez le champ dans `GraphState` :

```python
class GraphState(TypedDict):
    user_intent: str
    knowledge_graph: LivingKnowledgeGraph
    data_dir: str
    
    discovery: Optional[DataDiscovery]
    join_plan: Optional[JoinPlan]
    optimizations: Optional[List[str]]  # ⬅️ Nouveau champ
    execution_result: Optional[ExecutionResult]
    
    validation_passed: bool
    validation_errors: List[str]
    messages: List[str]
```

---

## 🧪 Tests et Qualité

### Structure de Test

Créez un fichier `tests/test_nouveau_composant.py` :

```python
import unittest
from modules.nouveau_composant import NouveauComposant

class TestNouveauComposant(unittest.TestCase):
    
    def setUp(self):
        """Préparation avant chaque test"""
        self.composant = NouveauComposant()
    
    def test_fonctionnalite_basique(self):
        """Test de la fonctionnalité de base"""
        resultat = self.composant.execute()
        self.assertIsNotNone(resultat)
    
    def test_gestion_erreur(self):
        """Test de la gestion d'erreur"""
        with self.assertRaises(ValueError):
            self.composant.execute_avec_erreur()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        pass

if __name__ == '__main__':
    unittest.main()
```

### Ajouter au Test Global

Éditez `test_ados.py` et ajoutez :

```python
def test_nouveau_composant():
    """Test 7: Nouveau Composant"""
    print_section("TEST 7: Nouveau Composant")
    
    try:
        from modules.nouveau_composant import NouveauComposant
        
        composant = NouveauComposant()
        resultat = composant.execute()
        
        if resultat:
            print_success("Nouveau composant fonctionne")
            return True
        else:
            print_error("Résultat invalide")
            return False
            
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

# Ajouter au main
tests = [
    # ... tests existants ...
    ("Nouveau Composant", test_nouveau_composant),
]
```

---

## 📝 Standards de Code

### Style Python

- **PEP 8** : Respect des conventions Python
- **Type Hints** : Utiliser les annotations de type
- **Docstrings** : Format Google/NumPy

### Exemple de Fonction Bien Documentée

```python
def process_data(input_df: pd.DataFrame, 
                 column_name: str,
                 threshold: float = 0.5) -> pd.DataFrame:
    """
    Traite un DataFrame en filtrant selon un seuil.
    
    Args:
        input_df: DataFrame d'entrée à traiter
        column_name: Nom de la colonne à filtrer
        threshold: Valeur seuil pour le filtrage (default: 0.5)
    
    Returns:
        DataFrame filtré contenant uniquement les lignes supérieures au seuil
    
    Raises:
        ValueError: Si column_name n'existe pas dans input_df
        TypeError: Si threshold n'est pas numérique
    
    Example:
        >>> df = pd.DataFrame({'score': [0.3, 0.7, 0.9]})
        >>> result = process_data(df, 'score', threshold=0.5)
        >>> len(result)
        2
    """
    if column_name not in input_df.columns:
        raise ValueError(f"Colonne '{column_name}' introuvable")
    
    if not isinstance(threshold, (int, float)):
        raise TypeError("threshold doit être numérique")
    
    return input_df[input_df[column_name] > threshold]
```

### Logging

Utilisez le module logging de manière cohérente :

```python
import logging

logger = logging.getLogger(__name__)

# Niveaux recommandés
logger.debug("Information détaillée pour debug")
logger.info("Information générale sur le flux")
logger.warning("Avertissement - comportement inattendu mais géré")
logger.error("Erreur - échec d'une opération")
logger.critical("Erreur critique - arrêt du système")
```

---

## 🔀 Workflow de Contribution

1. **Fork** le repository
2. **Créer une branche** : `git checkout -b feature/nouvelle-fonctionnalite`
3. **Développer** avec tests
4. **Tester** : `python test_ados.py`
5. **Commit** : `git commit -m "feat: ajout de X"`
6. **Push** : `git push origin feature/nouvelle-fonctionnalite`
7. **Pull Request** avec description détaillée

### Convention de Commits

```
feat: nouvelle fonctionnalité
fix: correction de bug
docs: modification de documentation
test: ajout/modification de tests
refactor: refactorisation du code
style: formatage du code
perf: amélioration de performance
```

---

## 📚 Ressources

- **LangGraph** : https://langchain-ai.github.io/langgraph/
- **DuckDB** : https://duckdb.org/docs/
- **NetworkX** : https://networkx.org/documentation/
- **Chainlit** : https://docs.chainlit.io/

---

**Merci de contribuer à ADOS ! 🚀**
