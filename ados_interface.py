"""
ADOS - Interface Chainlit
Interface web conversationnelle pour le Data Operating System
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import json

import chainlit as cl
from chainlit import Message, AskUserMessage

# Import des modules ADOS
from modules.data_generator import DataMeshSimulator
from modules.knowledge_graph import LivingKnowledgeGraph
from modules.intent_compiler import IntentCompiler
from modules.trust_layer import TrustLayer

# Chargement des variables d'environnement
load_dotenv()

# Variables globales
ados_system = None


@cl.on_chat_start
async def start():
    """Initialisation de la session Chainlit"""
    global ados_system
    
    await cl.Message(
        content="""
# 🚀 AI-Native Data Operating System (ADOS)

Bienvenue dans votre assistant de données autonome !

**Qu'est-ce que je peux faire ?**
- 📊 Analyser vos données avec du langage naturel
- 🔍 Découvrir automatiquement les relations entre vos données
- ⚡ Générer et exécuter des requêtes SQL intelligentes
- 🛡️ Valider la cohérence de vos analyses

**Initialisation en cours...**
        """
    ).send()
    
    # Initialiser le système
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Vérifier si les données existent
    required_files = [
        "customer_domain.parquet",
        "logistics_domain.parquet", 
        "sales_domain.parquet"
    ]
    
    data_exists = all((data_dir / f).exists() for f in required_files)
    
    # Génération de données si nécessaire
    if not data_exists:
        await cl.Message(content="📦 Génération des Data Products synthétiques...").send()
        
        data_generator = DataMeshSimulator(output_dir=str(data_dir))
        domains = data_generator.generate_all_domains()
        
        # Afficher un résumé
        summary_lines = ["✅ Data Products générés:\n"]
        for name, df in domains.items():
            summary_lines.append(f"- **{name}**: {len(df)} lignes, {len(df.columns)} colonnes")
        
        await cl.Message(content="\n".join(summary_lines)).send()
    
    # Construction du Knowledge Graph
    await cl.Message(content="🧠 Construction du Living Knowledge Graph...").send()
    
    kg = LivingKnowledgeGraph(data_dir=str(data_dir))
    dataframes = kg.scan_data_products()
    relationships = kg.discover_relationships(dataframes)
    
    # Afficher le graphe
    graph_viz = kg.visualize_graph()
    await cl.Message(content=f"```\n{graph_viz}\n```").send()
    
    # Initialisation de la Trust Layer
    trust_layer = TrustLayer(knowledge_graph=kg)
    
    # Initialisation du Compilateur
    try:
        intent_compiler = IntentCompiler(
            knowledge_graph=kg,
            data_dir=str(data_dir)
        )
        compiler_ready = True
    except ValueError as e:
        await cl.Message(
            content=f"⚠️ Impossible d'initialiser le compilateur LLM: {e}\n\n"
                   "Veuillez configurer `OPENAI_API_KEY` dans votre fichier `.env`"
        ).send()
        intent_compiler = None
        compiler_ready = False
    
    # Stocker dans la session
    cl.user_session.set("knowledge_graph", kg)
    cl.user_session.set("trust_layer", trust_layer)
    cl.user_session.set("intent_compiler", intent_compiler)
    cl.user_session.set("compiler_ready", compiler_ready)
    cl.user_session.set("dataframes", dataframes)
    
    # Message de bienvenue final
    if compiler_ready:
        await cl.Message(
            content="""
✅ **Système initialisé avec succès !**

**Exemples de requêtes :**
- "Montre-moi les 10 meilleurs clients par montant total"
- "Analyse l'impact des stocks bas sur mes clients VIP"
- "Quels produits ont un délai de livraison > 10 jours ?"
- "Liste les clients d'Île-de-France avec leurs transactions"

Posez votre question ci-dessous 👇
            """
        ).send()
    else:
        await cl.Message(
            content="⚠️ Mode dégradé: Exploration manuelle disponible uniquement"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Traitement des messages utilisateur"""
    
    user_intent = message.content.strip()
    
    # Récupération du contexte
    compiler_ready = cl.user_session.get("compiler_ready")
    intent_compiler = cl.user_session.get("intent_compiler")
    trust_layer = cl.user_session.get("trust_layer")
    kg = cl.user_session.get("knowledge_graph")
    
    # Vérifier si le compilateur est prêt
    if not compiler_ready:
        await cl.Message(
            content="❌ Le compilateur LLM n'est pas disponible. "
                   "Veuillez configurer votre clé OpenAI dans `.env`"
        ).send()
        return
    
    # Message de traitement
    processing_msg = cl.Message(content="🔄 Traitement de votre requête...")
    await processing_msg.send()
    
    try:
        # Compilation de l'intention
        result = intent_compiler.compile_intent(user_intent)
        
        # Afficher les étapes
        steps_lines = ["### 📋 Étapes de traitement\n"]
        for msg in result.get("messages", []):
            steps_lines.append(f"- {msg}")
        
        await cl.Message(content="\n".join(steps_lines)).send()
        
        # Afficher la découverte
        if result.get("discovery"):
            discovery = result["discovery"]
            discovery_text = f"""
### 🔍 Découverte

**Fichiers identifiés:** {', '.join(discovery.required_files)}

**Colonnes requises:**
{chr(10).join([f"- **{file}**: {', '.join(cols)}" for file, cols in discovery.required_columns.items()])}

**Raisonnement:** {discovery.reasoning}
            """
            await cl.Message(content=discovery_text).send()
        
        # Afficher le plan SQL
        if result.get("plan"):
            plan = result["plan"]
            plan_text = f"""
### 📝 Plan d'Exécution

**Requête SQL générée:**
```sql
{plan.sql_query}
```

**Explication:** {plan.explanation}
            """
            await cl.Message(content=plan_text).send()
            
            # Validation Trust Layer
            if result.get("discovery"):
                validation_passed, issues = trust_layer.validate_execution_plan(
                    sql_query=plan.sql_query,
                    required_files=discovery.required_files,
                    required_columns=discovery.required_columns
                )
                
                # Rapport d'audit
                if issues:
                    audit_lines = ["### 🛡️ Trust Layer - Validation\n"]
                    
                    critical = [i for i in issues if i.severity.value == "critical"]
                    warnings = [i for i in issues if i.severity.value == "warning"]
                    
                    if critical:
                        audit_lines.append("**🚨 Erreurs critiques:**")
                        for issue in critical:
                            audit_lines.append(f"- [{issue.rule}] {issue.message}")
                            if issue.suggestion:
                                audit_lines.append(f"  💡 {issue.suggestion}")
                    
                    if warnings:
                        audit_lines.append("\n**⚠️ Avertissements:**")
                        for issue in warnings:
                            audit_lines.append(f"- [{issue.rule}] {issue.message}")
                    
                    if not critical:
                        audit_lines.append("\n✅ **Validation réussie**")
                    
                    await cl.Message(content="\n".join(audit_lines)).send()
        
        # Afficher les résultats
        if result.get("execution"):
            exec_result = result["execution"]
            
            if exec_result.success:
                result_text = f"### ✅ Résultats ({exec_result.rows_count} lignes)\n\n"
                
                # Convertir en DataFrame pour affichage
                if exec_result.data:
                    try:
                        df = pd.read_json(exec_result.data)
                        
                        # Limiter l'affichage à 20 lignes
                        display_df = df.head(20)
                        
                        result_text += "**Aperçu des données:**\n\n"
                        result_text += display_df.to_markdown(index=False)
                        
                        if len(df) > 20:
                            result_text += f"\n\n*...et {len(df) - 20} lignes supplémentaires*"
                        
                        # Envoyer le résultat
                        await cl.Message(content=result_text).send()
                        
                        # Bouton pour télécharger les données complètes
                        elements = [
                            cl.Text(
                                name="Données complètes (JSON)",
                                content=exec_result.data,
                                display="inline"
                            )
                        ]
                        
                        await cl.Message(
                            content="📥 **Téléchargement disponible:**",
                            elements=elements
                        ).send()
                        
                    except Exception as e:
                        await cl.Message(
                            content=f"⚠️ Impossible d'afficher les résultats: {e}"
                        ).send()
            else:
                await cl.Message(
                    content=f"❌ **Erreur d'exécution:**\n```\n{exec_result.error}\n```"
                ).send()
    
    except Exception as e:
        await cl.Message(
            content=f"❌ **Erreur inattendue:**\n```\n{str(e)}\n```"
        ).send()
    
    finally:
        # Supprimer le message de traitement
        await processing_msg.remove()


@cl.on_settings_update
async def setup_agent(settings):
    """Mise à jour des paramètres"""
    pass


if __name__ == "__main__":
    # Lancer l'interface Chainlit
    # Commande: chainlit run ados_interface.py
    pass
