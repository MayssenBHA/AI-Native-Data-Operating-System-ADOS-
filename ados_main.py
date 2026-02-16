"""
ADOS - Script Principal Auto-Exécutable
Point d'entrée unique pour le prototype du Data Operating System
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ados.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import des modules ADOS
from modules.data_generator import DataMeshSimulator
from modules.knowledge_graph import LivingKnowledgeGraph
from modules.intent_compiler import IntentCompiler
from modules.trust_layer import TrustLayer


class ADOS:
    """
    AI-Native Data Operating System
    Orchestrateur principal du système
    """
    
    def __init__(self, data_dir: str = "data", auto_generate: bool = True):
        """
        Args:
            data_dir: Répertoire des données
            auto_generate: Générer automatiquement les données si absentes
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info("=== Initialisation du AI-Native Data Operating System ===")
        
        # Charger les variables d'environnement
        load_dotenv()
        
        # Étape 1: Génération de données
        if auto_generate or not self._data_exists():
            logger.info("📦 Génération des Data Products...")
            self.data_generator = DataMeshSimulator(output_dir=str(self.data_dir))
            self.domains = self.data_generator.generate_all_domains()
        else:
            logger.info("📦 Utilisation des Data Products existants")
            self.data_generator = None
            self.domains = {}
        
        # Étape 2: Construction du Knowledge Graph
        logger.info("🧠 Construction du Living Knowledge Graph...")
        self.knowledge_graph = LivingKnowledgeGraph(data_dir=str(self.data_dir))
        self.dataframes = self.knowledge_graph.scan_data_products()
        self.knowledge_graph.discover_relationships(self.dataframes)
        
        # Étape 3: Initialisation de la Trust Layer
        logger.info("🛡️  Initialisation de la Trust Layer...")
        self.trust_layer = TrustLayer(knowledge_graph=self.knowledge_graph)
        
        # Étape 4: Initialisation du Compilateur d'Intention
        logger.info("⚡ Initialisation du Compilateur d'Intention...")
        try:
            self.intent_compiler = IntentCompiler(
                knowledge_graph=self.knowledge_graph,
                data_dir=str(self.data_dir)
            )
            self.compiler_ready = True
        except ValueError as e:
            logger.error("Impossible d'initialiser le compilateur: %s", e)
            logger.warning("Mode dégradé: fonctionnalités LLM désactivées")
            self.intent_compiler = None
            self.compiler_ready = False
        
        logger.info("✓ ADOS initialisé avec succès\n")
    
    def _data_exists(self) -> bool:
        """Vérifie si les données existent déjà"""
        required_files = [
            "customer_domain.parquet",
            "logistics_domain.parquet",
            "sales_domain.parquet"
        ]
        return all((self.data_dir / f).exists() for f in required_files)
    
    def show_system_status(self):
        """Affiche le statut du système"""
        print("\n" + "="*60)
        print("🚀 AI-Native Data Operating System (ADOS) - Status")
        print("="*60)
        
        # Knowledge Graph
        print(self.knowledge_graph.visualize_graph())
        
        # Compilateur
        print(f"\n⚡ Compilateur d'Intention: {'✓ Actif' if self.compiler_ready else '✗ Inactif (clé API manquante)'}")
        
        # Trust Layer
        print(f"🛡️  Trust Layer: ✓ Active")
        
        print("="*60 + "\n")
    
    def process_intent(self, user_intent: str, validate: bool = True) -> dict:
        """
        Traite une intention utilisateur de bout en bout
        
        Args:
            user_intent: Intention en langage naturel
            validate: Activer la validation Trust Layer
            
        Returns:
            Résultat complet du traitement
        """
        if not self.compiler_ready:
            return {
                "error": "Compilateur non disponible. Configurez OPENAI_API_KEY dans .env",
                "intent": user_intent
            }
        
        logger.info("\n" + "="*60)
        logger.info("🎯 Traitement de l'intention: %s", user_intent)
        logger.info("="*60)
        
        # Compilation via LangGraph
        result = self.intent_compiler.compile_intent(user_intent)
        
        # Validation avec Trust Layer si activée
        if validate and result.get("plan"):
            plan = result["plan"]
            discovery = result.get("discovery")
            
            if plan and discovery:
                validation_passed, issues = self.trust_layer.validate_execution_plan(
                    sql_query=plan.sql_query,
                    required_files=discovery.required_files,
                    required_columns=discovery.required_columns
                )
                
                result["validation"] = {
                    "passed": validation_passed,
                    "issues": [
                        {
                            "severity": issue.severity.value,
                            "rule": issue.rule,
                            "message": issue.message,
                            "suggestion": issue.suggestion
                        }
                        for issue in issues
                    ]
                }
                
                # Afficher le rapport d'audit
                audit_report = self.trust_layer.generate_audit_report(issues)
                print("\n" + audit_report)
        
        return result
    
    def interactive_mode(self):
        """Mode interactif en ligne de commande"""
        print("\n" + "="*60)
        print("🤖 ADOS - Mode Interactif")
        print("="*60)
        print("Tapez vos requêtes en langage naturel.")
        print("Commandes spéciales:")
        print("  - 'status': Afficher le statut du système")
        print("  - 'examples': Voir des exemples de requêtes")
        print("  - 'quit' ou 'exit': Quitter")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("\n💬 Votre requête > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Au revoir!")
                    break
                
                if user_input.lower() == 'status':
                    self.show_system_status()
                    continue
                
                if user_input.lower() == 'examples':
                    self._show_examples()
                    continue
                
                # Traiter l'intention
                result = self.process_intent(user_input)
                
                # Afficher le résultat
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interruption - Au revoir!")
                break
            except Exception as e:
                logger.error("Erreur: %s", e)
                print(f"\n❌ Erreur: {e}")
    
    def _show_examples(self):
        """Affiche des exemples de requêtes"""
        examples = [
            "Montre-moi les 10 meilleurs clients par montant total",
            "Analyse l'impact des stocks bas sur mes clients VIP",
            "Quels sont les produits avec un délai de livraison supérieur à 10 jours ?",
            "Liste les clients d'Île-de-France avec leurs transactions",
            "Identifie les clients fidèles (score > 80) avec des achats récents"
        ]
        
        print("\n📚 Exemples de requêtes:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
    
    def _display_result(self, result: dict):
        """Affiche le résultat formaté"""
        print("\n" + "-"*60)
        
        # Afficher les messages
        if "messages" in result:
            print("📋 Étapes:")
            for msg in result["messages"]:
                print(f"  {msg}")
        
        # Afficher le plan SQL
        if "plan" in result and result["plan"]:
            print(f"\n📝 Requête SQL générée:")
            print(f"  {result['plan'].sql_query}")
        
        # Afficher le résultat de l'exécution
        if "execution" in result and result["execution"]:
            exec_result = result["execution"]
            
            if exec_result.success:
                print(f"\n✅ Exécution réussie: {exec_result.rows_count} lignes")
                
                # Afficher un aperçu des données
                if exec_result.data:
                    try:
                        import pandas as pd
                        df = pd.read_json(exec_result.data)
                        print("\n📊 Aperçu du résultat:")
                        print(df.head(10).to_string())
                    except Exception as e:
                        logger.warning("Impossible d'afficher l'aperçu: %s", e)
            else:
                print(f"\n❌ Erreur d'exécution: {exec_result.error}")
        
        # Afficher la validation
        if "validation" in result:
            validation = result["validation"]
            if validation["passed"]:
                print(f"\n✅ Validation réussie")
            else:
                print(f"\n⚠️  Validation: {len(validation['issues'])} problèmes détectés")
        
        print("-"*60)


def main():
    """Point d'entrée principal"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🚀 AI-Native Data Operating System (ADOS)              ║
    ║                                                           ║
    ║   Transformez vos intentions en insights                 ║
    ║   Architecture: LangGraph + DuckDB + NetworkX            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Initialiser ADOS
    ados = ADOS(auto_generate=True)
    
    # Afficher le statut
    ados.show_system_status()
    
    # Exemples de test automatiques
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        logger.info("Mode DEMO activé")
        
        demo_queries = [
            "Montre-moi les 10 meilleurs clients par montant total",
            "Quels produits ont un stock inférieur à 50 ?",
        ]
        
        for query in demo_queries:
            print(f"\n{'='*60}")
            print(f"🎯 Demo Query: {query}")
            print('='*60)
            result = ados.process_intent(query)
            ados._display_result(result)
            input("\nAppuyez sur Entrée pour continuer...")
    else:
        # Mode interactif
        ados.interactive_mode()


if __name__ == "__main__":
    main()
