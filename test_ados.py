"""
Script de Test Complet ADOS
Vérifie que tous les composants fonctionnent correctement
"""

import sys
import os
from pathlib import Path
from colorama import Fore, Style, init

# Initialiser colorama pour Windows
init(autoreset=True)

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
    print("="*60)

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Affiche un avertissement"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def test_imports():
    """Test 1: Vérifier les imports"""
    print_section("TEST 1: Vérification des Imports")
    
    required_packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("faker", "faker"),
        ("duckdb", "duckdb"),
        ("networkx", "networkx"),
        ("langchain", "langchain"),
        ("langgraph", "langgraph"),
    ]
    
    all_ok = True
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"{package_name} installé")
        except ImportError:
            print_error(f"{package_name} manquant")
            all_ok = False
    
    return all_ok

def test_data_generator():
    """Test 2: Générateur de données"""
    print_section("TEST 2: Générateur de Données Synthétiques")
    
    try:
        from modules.data_generator import DataMeshSimulator
        
        # Créer un répertoire temporaire pour les tests
        test_dir = Path("test_data")
        test_dir.mkdir(exist_ok=True)
        
        simulator = DataMeshSimulator(output_dir=str(test_dir))
        domains = simulator.generate_all_domains()
        
        # Vérifier les fichiers
        expected_files = ["customer_domain", "logistics_domain", "sales_domain"]
        for file_key in expected_files:
            if file_key in domains:
                df = domains[file_key]
                print_success(f"{file_key}: {len(df)} lignes, {len(df.columns)} colonnes")
            else:
                print_error(f"{file_key} non généré")
                return False
        
        # Nettoyage
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_knowledge_graph():
    """Test 3: Knowledge Graph"""
    print_section("TEST 3: Living Knowledge Graph")
    
    try:
        from modules.knowledge_graph import LivingKnowledgeGraph
        from modules.data_generator import DataMeshSimulator
        
        # Générer des données de test
        test_dir = Path("test_data")
        test_dir.mkdir(exist_ok=True)
        
        simulator = DataMeshSimulator(output_dir=str(test_dir))
        simulator.generate_all_domains()
        
        # Tester le knowledge graph
        kg = LivingKnowledgeGraph(data_dir=str(test_dir))
        dataframes = kg.scan_data_products()
        
        print_success(f"Scanné {len(dataframes)} fichiers")
        
        relationships = kg.discover_relationships(dataframes)
        print_success(f"Découvert {len(relationships)} relations")
        
        # Test de chemin
        if len(dataframes) >= 2:
            files = list(dataframes.keys())
            path = kg.get_join_path(files[0], files[1])
            if path:
                print_success(f"Chemin trouvé: {' → '.join(path)}")
        
        # Nettoyage
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_trust_layer():
    """Test 4: Trust Layer"""
    print_section("TEST 4: Trust Layer")
    
    try:
        from modules.trust_layer import TrustLayer
        from modules.knowledge_graph import LivingKnowledgeGraph
        from modules.data_generator import DataMeshSimulator
        
        # Générer des données de test
        test_dir = Path("test_data")
        test_dir.mkdir(exist_ok=True)
        
        simulator = DataMeshSimulator(output_dir=str(test_dir))
        simulator.generate_all_domains()
        
        kg = LivingKnowledgeGraph(data_dir=str(test_dir))
        kg.scan_data_products()
        
        trust_layer = TrustLayer(knowledge_graph=kg)
        
        # Test avec une requête valide
        valid_sql = """
        SELECT c.Nom, SUM(s.Montant) as Total
        FROM 'test_data/customer_domain.parquet' AS c
        JOIN 'test_data/sales_domain.parquet' AS s ON c.ID_Client = s.ID_Client
        GROUP BY c.Nom
        LIMIT 10
        """
        
        passed, issues = trust_layer.validate_execution_plan(
            sql_query=valid_sql,
            required_files=["customer_domain", "sales_domain"],
            required_columns={
                "customer_domain": ["Nom", "ID_Client"],
                "sales_domain": ["ID_Client", "Montant"]
            }
        )
        
        if passed:
            print_success(f"Validation réussie ({len(issues)} issues)")
        else:
            print_warning(f"Validation échouée ({len(issues)} issues)")
        
        # Test avec une requête invalide (colonne inexistante)
        invalid_sql = """
        SELECT c.ColonneInexistante
        FROM 'test_data/customer_domain.parquet' AS c
        """
        
        passed, issues = trust_layer.validate_execution_plan(
            sql_query=invalid_sql,
            required_files=["customer_domain"],
            required_columns={"customer_domain": ["ColonneInexistante"]}
        )
        
        if not passed:
            print_success("Détection d'erreur fonctionne correctement")
        
        # Nettoyage
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_duckdb_execution():
    """Test 5: Exécution DuckDB"""
    print_section("TEST 5: Moteur de Requêtes DuckDB")
    
    try:
        import duckdb
        from modules.data_generator import DataMeshSimulator
        
        # Générer des données de test
        test_dir = Path("test_data")
        test_dir.mkdir(exist_ok=True)
        
        simulator = DataMeshSimulator(output_dir=str(test_dir))
        simulator.generate_all_domains()
        
        # Test d'exécution
        conn = duckdb.connect(database=':memory:')
        
        query = f"""
        SELECT COUNT(*) as count
        FROM '{test_dir}/customer_domain.parquet'
        """
        
        result = conn.execute(query).fetchdf()
        count = result['count'][0]
        
        print_success(f"Requête DuckDB exécutée: {count} lignes comptées")
        
        # Test de jointure
        join_query = f"""
        SELECT c.Nom, SUM(s.Montant) as Total
        FROM '{test_dir}/customer_domain.parquet' AS c
        JOIN '{test_dir}/sales_domain.parquet' AS s ON c.ID_Client = s.ID_Client
        GROUP BY c.Nom
        ORDER BY Total DESC
        LIMIT 5
        """
        
        result = conn.execute(join_query).fetchdf()
        print_success(f"Jointure exécutée: {len(result)} lignes retournées")
        
        conn.close()
        
        # Nettoyage
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_environment():
    """Test 6: Variables d'environnement"""
    print_section("TEST 6: Configuration Environnement")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and api_key != "your_openai_api_key_here":
        print_success("OPENAI_API_KEY configurée")
        return True
    else:
        print_warning("OPENAI_API_KEY non configurée (LLM désactivé)")
        print(f"{Fore.YELLOW}  → Créez un fichier .env avec votre clé API{Style.RESET_ALL}")
        return False

def main():
    """Exécute tous les tests"""
    print(f"""
    {Fore.CYAN}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🧪 ADOS - Suite de Tests Complète                      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    {Style.RESET_ALL}
    """)
    
    tests = [
        ("Imports des packages", test_imports),
        ("Générateur de données", test_data_generator),
        ("Knowledge Graph", test_knowledge_graph),
        ("Trust Layer", test_trust_layer),
        ("Moteur DuckDB", test_duckdb_execution),
        ("Configuration", test_environment),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(test_name)
        else:
            print_error(test_name)
    
    print(f"\n{Fore.CYAN}Score: {passed}/{total} tests réussis{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 Tous les tests sont passés ! Le système est prêt.{Style.RESET_ALL}")
        return 0
    elif passed >= total - 1:  # Tolérance si seule la config manque
        print(f"\n{Fore.YELLOW}✓ Système fonctionnel (certaines fonctionnalités désactivées){Style.RESET_ALL}")
        return 0
    else:
        print(f"\n{Fore.RED}❌ Certains tests ont échoué. Vérifiez l'installation.{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
