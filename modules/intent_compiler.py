"""
ADOS - Intent Compiler Module
Agent LangGraph qui compile une intention en langage naturel en plan d'exécution
"""

import os
from typing import Dict, List, TypedDict, Annotated, Optional
import logging
import duckdb
import pandas as pd
from pathlib import Path

# LangChain & LangGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from modules.knowledge_graph import LivingKnowledgeGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# === Modèles Pydantic pour structurer les sorties ===

class DataDiscovery(BaseModel):
    """Résultat de la phase de découverte"""
    required_files: List[str] = Field(description="Fichiers nécessaires pour la requête")
    required_columns: Dict[str, List[str]] = Field(description="Colonnes par fichier")
    reasoning: str = Field(description="Raisonnement de la découverte")


class JoinPlan(BaseModel):
    """Plan de jointure SQL"""
    sql_query: str = Field(description="Requête SQL DuckDB complète")
    join_path: List[str] = Field(description="Chemin de jointure entre fichiers")
    explanation: str = Field(description="Explication du plan de jointure")


class ExecutionResult(BaseModel):
    """Résultat de l'exécution"""
    success: bool
    data: Optional[str] = None  # JSON ou description
    error: Optional[str] = None
    rows_count: int = 0


# === État du Graphe LangGraph ===

class GraphState(TypedDict):
    """État partagé entre les nœuds du graphe"""
    user_intent: str
    knowledge_graph: LivingKnowledgeGraph
    data_dir: str
    
    # Découverte
    discovery: Optional[DataDiscovery]
    
    # Planification
    join_plan: Optional[JoinPlan]
    
    # Exécution
    execution_result: Optional[ExecutionResult]
    
    # Validation (Trust Layer)
    validation_passed: bool
    validation_errors: List[str]
    
    # Contexte
    messages: List[str]


class IntentCompiler:
    """
    Compilateur d'intention utilisant LangGraph pour orchestrer
    les agents de découverte, planification et exécution
    """
    
    def __init__(self, knowledge_graph: LivingKnowledgeGraph, data_dir: str = "data",
                 model_name: str = "gpt-4-turbo-preview", temperature: float = 0.1):
        """
        Args:
            knowledge_graph: Instance du graphe de connaissances
            data_dir: Répertoire des données
            model_name: Modèle OpenAI à utiliser
            temperature: Température du LLM
        """
        self.kg = knowledge_graph
        self.data_dir = Path(data_dir)
        
        # Configuration LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY non définie. Créez un fichier .env")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        # Construction du graphe LangGraph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("IntentCompiler initialisé avec modèle %s", model_name)
    
    def _build_workflow(self) -> StateGraph:
        """Construit le workflow LangGraph"""
        workflow = StateGraph(GraphState)
        
        # Ajout des nœuds
        workflow.add_node("discovery", self._discovery_node)
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("execution", self._execution_node)
        
        # Définition des arêtes
        workflow.set_entry_point("discovery")
        workflow.add_edge("discovery", "planning")
        workflow.add_edge("planning", "execution")
        workflow.add_edge("execution", END)
        
        return workflow
    
    def _discovery_node(self, state: GraphState) -> GraphState:
        """
        Nœud 1: Découverte des fichiers et colonnes nécessaires
        """
        logger.info("🔍 Phase DISCOVERY: Analyse de l'intention")
        
        user_intent = state["user_intent"]
        kg_summary = state["knowledge_graph"].get_metadata_summary()
        
        # Prompt pour la découverte
        discovery_prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en analyse de données. 
Analyse l'intention utilisateur et identifie quels fichiers et colonnes sont nécessaires.

Contexte des données disponibles:
{kg_summary}

Réponds uniquement avec un objet JSON structuré selon ce format:
{{
    "required_files": ["file1", "file2"],
    "required_columns": {{"file1": ["col1", "col2"], "file2": ["col3"]}},
    "reasoning": "Explication de la logique"
}}
"""),
            ("user", "{user_intent}")
        ])
        
        # Appel LLM
        chain = discovery_prompt | self.llm
        response = chain.invoke({
            "user_intent": user_intent,
            "kg_summary": str(kg_summary)
        })
        
        # Parse la réponse
        try:
            import json
            discovery_data = json.loads(response.content)
            discovery = DataDiscovery(**discovery_data)
            
            state["discovery"] = discovery
            state["messages"].append(f"✓ Découverte: {len(discovery.required_files)} fichiers identifiés")
            logger.info("  Fichiers: %s", ", ".join(discovery.required_files))
            
        except Exception as e:
            logger.error("Erreur parsing discovery: %s", e)
            state["messages"].append(f"✗ Erreur discovery: {e}")
            state["validation_passed"] = False
        
        return state
    
    def _planning_node(self, state: GraphState) -> GraphState:
        """
        Nœud 2: Planification de la requête SQL
        """
        logger.info("🗺️  Phase PLANNING: Génération du plan SQL")
        
        discovery = state["discovery"]
        if not discovery:
            state["messages"].append("✗ Impossible de planifier sans découverte")
            return state
        
        user_intent = state["user_intent"]
        kg = state["knowledge_graph"]
        
        # Trouver le chemin de jointure
        files = discovery.required_files
        join_path_info = []
        
        if len(files) > 1:
            # Chercher le chemin entre le premier et dernier fichier
            path = kg.get_join_path(files[0], files[-1])
            if path:
                join_columns = kg.get_join_columns_for_path(path)
                join_path_info = join_columns
        
        # Prompt pour générer SQL
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert SQL DuckDB. 
Génère une requête SQL complète pour répondre à l'intention utilisateur.

Fichiers requis: {files}
Colonnes disponibles: {columns}
Relations de jointure: {join_info}

Règles:
- Utilise la syntaxe DuckDB
- Les fichiers Parquet sont dans le dossier 'data/'
- Syntaxe: SELECT ... FROM 'data/fichier.parquet' AS alias
- Joins basés sur les relations fournies
- Limite à 100 lignes par défaut

Réponds uniquement avec un objet JSON:
{{
    "sql_query": "SELECT ...",
    "join_path": ["file1", "file2"],
    "explanation": "Description du plan"
}}
"""),
            ("user", "{user_intent}")
        ])
        
        # Appel LLM
        chain = planning_prompt | self.llm
        response = chain.invoke({
            "user_intent": user_intent,
            "files": discovery.required_files,
            "columns": discovery.required_columns,
            "join_info": str(join_path_info)
        })
        
        # Parse la réponse
        try:
            import json
            plan_data = json.loads(response.content)
            join_plan = JoinPlan(**plan_data)
            
            state["join_plan"] = join_plan
            state["messages"].append("✓ Plan SQL généré")
            logger.info("  SQL: %s", join_plan.sql_query[:100] + "...")
            
        except Exception as e:
            logger.error("Erreur parsing plan: %s", e)
            state["messages"].append(f"✗ Erreur planning: {e}")
            state["validation_passed"] = False
        
        return state
    
    def _execution_node(self, state: GraphState) -> GraphState:
        """
        Nœud 3: Exécution de la requête avec DuckDB
        """
        logger.info("⚡ Phase EXECUTION: Exécution via DuckDB")
        
        join_plan = state["join_plan"]
        if not join_plan:
            state["messages"].append("✗ Impossible d'exécuter sans plan")
            return state
        
        try:
            # Connexion DuckDB
            conn = duckdb.connect(database=':memory:')
            
            # Exécution de la requête
            result_df = conn.execute(join_plan.sql_query).fetchdf()
            conn.close()
            
            # Conversion en JSON pour stockage
            result_json = result_df.to_json(orient='records', indent=2)
            
            execution_result = ExecutionResult(
                success=True,
                data=result_json,
                rows_count=len(result_df)
            )
            
            state["execution_result"] = execution_result
            state["messages"].append(f"✓ Exécution réussie: {len(result_df)} lignes retournées")
            logger.info("  Résultat: %d lignes", len(result_df))
            
        except Exception as e:
            logger.error("Erreur exécution: %s", e)
            execution_result = ExecutionResult(
                success=False,
                error=str(e)
            )
            state["execution_result"] = execution_result
            state["messages"].append(f"✗ Erreur exécution: {e}")
            state["validation_passed"] = False
        
        return state
    
    def compile_intent(self, user_intent: str) -> Dict:
        """
        Point d'entrée principal: compile une intention en résultat
        
        Args:
            user_intent: Intention en langage naturel
            
        Returns:
            Dictionnaire avec le résultat complet
        """
        logger.info("=== Compilation de l'intention ===")
        logger.info("Intent: %s", user_intent)
        
        # État initial
        initial_state: GraphState = {
            "user_intent": user_intent,
            "knowledge_graph": self.kg,
            "data_dir": str(self.data_dir),
            "discovery": None,
            "join_plan": None,
            "execution_result": None,
            "validation_passed": True,
            "validation_errors": [],
            "messages": []
        }
        
        # Exécution du workflow
        final_state = self.app.invoke(initial_state)
        
        # Formatage du résultat
        result = {
            "intent": user_intent,
            "discovery": final_state.get("discovery"),
            "plan": final_state.get("join_plan"),
            "execution": final_state.get("execution_result"),
            "messages": final_state.get("messages", []),
            "validation_passed": final_state.get("validation_passed", True)
        }
        
        logger.info("=== Compilation terminée ===")
        return result


if __name__ == "__main__":
    # Test du module
    from modules.knowledge_graph import LivingKnowledgeGraph
    
    kg = LivingKnowledgeGraph()
    kg.scan_data_products()
    
    compiler = IntentCompiler(knowledge_graph=kg)
    
    test_intent = "Montre-moi les 10 meilleurs clients par montant total"
    result = compiler.compile_intent(test_intent)
    
    print("\n📊 Résultat de la compilation:")
    for msg in result["messages"]:
        print(f"  {msg}")
