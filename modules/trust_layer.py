"""
ADOS - Trust Layer Module
Judge Agent qui valide la cohérence et la sécurité du plan d'exécution
"""

import re
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from modules.knowledge_graph import LivingKnowledgeGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Niveaux de sévérité des erreurs de validation"""
    CRITICAL = "critical"  # Bloque l'exécution
    WARNING = "warning"    # Avertissement
    INFO = "info"          # Information


@dataclass
class ValidationIssue:
    """Issue détectée lors de la validation"""
    severity: ValidationSeverity
    rule: str
    message: str
    suggestion: Optional[str] = None


class TrustLayer:
    """
    Couche de confiance qui valide les plans d'exécution
    avant leur exécution effective
    """
    
    def __init__(self, knowledge_graph: LivingKnowledgeGraph, llm: Optional[ChatOpenAI] = None):
        """
        Args:
            knowledge_graph: Graphe de connaissances pour validation
            llm: LLM optionnel pour validation sémantique avancée
        """
        self.kg = knowledge_graph
        self.llm = llm
        
        logger.info("TrustLayer initialisée")
    
    def validate_execution_plan(self, 
                                sql_query: str,
                                required_files: List[str],
                                required_columns: Dict[str, List[str]]) -> Tuple[bool, List[ValidationIssue]]:
        """
        Valide un plan d'exécution selon plusieurs règles
        
        Args:
            sql_query: Requête SQL générée
            required_files: Fichiers requis
            required_columns: Colonnes requises par fichier
            
        Returns:
            (validation_passed, list_of_issues)
        """
        logger.info("🛡️  Validation du plan d'exécution...")
        
        issues: List[ValidationIssue] = []
        
        # Règle 1: Vérifier que les fichiers existent
        issues.extend(self._validate_file_existence(required_files))
        
        # Règle 2: Vérifier que les colonnes existent
        issues.extend(self._validate_column_existence(required_columns))
        
        # Règle 3: Valider la syntaxe SQL basique
        issues.extend(self._validate_sql_syntax(sql_query))
        
        # Règle 4: Vérifier la cohérence des types dans les jointures
        issues.extend(self._validate_join_type_compatibility(sql_query, required_files))
        
        # Règle 5: Détecter les opérations dangereuses
        issues.extend(self._validate_sql_safety(sql_query))
        
        # Règle 6: Validation sémantique avec LLM (optionnel)
        if self.llm:
            issues.extend(self._validate_semantic_coherence(sql_query, required_files))
        
        # Déterminer si la validation passe
        has_critical = any(issue.severity == ValidationSeverity.CRITICAL for issue in issues)
        validation_passed = not has_critical
        
        # Log des résultats
        for issue in issues:
            emoji = "🚨" if issue.severity == ValidationSeverity.CRITICAL else "⚠️" if issue.severity == ValidationSeverity.WARNING else "ℹ️"
            logger.info(f"  {emoji} [{issue.severity.value.upper()}] {issue.rule}: {issue.message}")
        
        if validation_passed:
            logger.info("✓ Validation réussie (%d warnings)", 
                       len([i for i in issues if i.severity == ValidationSeverity.WARNING]))
        else:
            logger.error("✗ Validation échouée (%d erreurs critiques)", 
                        len([i for i in issues if i.severity == ValidationSeverity.CRITICAL]))
        
        return validation_passed, issues
    
    def _validate_file_existence(self, required_files: List[str]) -> List[ValidationIssue]:
        """Vérifie que tous les fichiers existent dans le Knowledge Graph"""
        issues = []
        
        available_files = set(self.kg.metadata.keys())
        
        for file in required_files:
            if file not in available_files:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    rule="file_existence",
                    message=f"Fichier '{file}' introuvable",
                    suggestion=f"Fichiers disponibles: {', '.join(available_files)}"
                ))
        
        return issues
    
    def _validate_column_existence(self, required_columns: Dict[str, List[str]]) -> List[ValidationIssue]:
        """Vérifie que toutes les colonnes existent"""
        issues = []
        
        for file, columns in required_columns.items():
            if file not in self.kg.metadata:
                continue  # Déjà détecté par file_existence
            
            available_columns = set(self.kg.metadata[file].keys())
            
            for col in columns:
                if col not in available_columns:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        rule="column_existence",
                        message=f"Colonne '{col}' introuvable dans '{file}'",
                        suggestion=f"Colonnes disponibles: {', '.join(available_columns)}"
                    ))
        
        return issues
    
    def _validate_sql_syntax(self, sql_query: str) -> List[ValidationIssue]:
        """Validation basique de la syntaxe SQL"""
        issues = []
        
        # Vérifier la présence de SELECT
        if not re.search(r'\bSELECT\b', sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                rule="sql_syntax",
                message="Requête SQL invalide: SELECT manquant"
            ))
        
        # Vérifier la présence de FROM
        if not re.search(r'\bFROM\b', sql_query, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                rule="sql_syntax",
                message="Requête SQL invalide: FROM manquant"
            ))
        
        # Vérifier que les guillemets sont équilibrés
        single_quotes = sql_query.count("'")
        if single_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                rule="sql_syntax",
                message="Guillemets simples non appariés détectés"
            ))
        
        return issues
    
    def _validate_join_type_compatibility(self, sql_query: str, required_files: List[str]) -> List[ValidationIssue]:
        """Vérifie la compatibilité des types dans les jointures"""
        issues = []
        
        # Extraire les colonnes de jointure avec regex
        join_pattern = r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        matches = re.findall(join_pattern, sql_query, re.IGNORECASE)
        
        for match in matches:
            alias1, col1, alias2, col2 = match
            
            # Mapper les alias aux fichiers (simplifié)
            # Dans une implémentation complète, il faudrait parser l'alias mapping
            file1 = self._resolve_alias_to_file(alias1, required_files)
            file2 = self._resolve_alias_to_file(alias2, required_files)
            
            if file1 and file2:
                type1 = self._get_column_type(file1, col1)
                type2 = self._get_column_type(file2, col2)
                
                if type1 and type2 and not self._are_types_compatible(type1, type2):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        rule="type_compatibility",
                        message=f"Jointure incompatible: {file1}.{col1} ({type1}) avec {file2}.{col2} ({type2})",
                        suggestion="Convertir l'un des types avec CAST()"
                    ))
        
        return issues
    
    def _validate_sql_safety(self, sql_query: str) -> List[ValidationIssue]:
        """Détecte les opérations potentiellement dangereuses"""
        issues = []
        
        dangerous_keywords = [
            (r'\bDROP\b', "DROP détecté - opération destructrice"),
            (r'\bDELETE\b', "DELETE détecté - modification de données"),
            (r'\bUPDATE\b', "UPDATE détecté - modification de données"),
            (r'\bTRUNCATE\b', "TRUNCATE détecté - opération destructrice"),
            (r'\bINSERT\b', "INSERT détecté - modification de données"),
        ]
        
        for pattern, message in dangerous_keywords:
            if re.search(pattern, sql_query, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    rule="sql_safety",
                    message=message,
                    suggestion="Seules les requêtes en lecture seule (SELECT) sont autorisées"
                ))
        
        return issues
    
    def _validate_semantic_coherence(self, sql_query: str, required_files: List[str]) -> List[ValidationIssue]:
        """Validation sémantique avancée avec LLM"""
        issues = []
        
        if not self.llm:
            return issues
        
        try:
            # Prompt pour le Judge Agent
            judge_prompt = ChatPromptTemplate.from_messages([
                ("system", """Tu es un expert en validation de requêtes SQL.
Analyse la requête suivante et identifie les problèmes potentiels de logique métier.

Fichiers concernés: {files}

Vérifie:
1. La logique métier est cohérente
2. Les agrégations sont correctes
3. Les filtres ont du sens
4. Pas d'incohérences sémantiques

Réponds uniquement par "OK" ou liste les problèmes."""),
                ("user", "{sql_query}")
            ])
            
            chain = judge_prompt | self.llm
            response = chain.invoke({
                "sql_query": sql_query,
                "files": ", ".join(required_files)
            })
            
            response_text = response.content.strip()
            
            if response_text.upper() != "OK":
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    rule="semantic_coherence",
                    message=f"Judge Agent: {response_text}"
                ))
        
        except Exception as e:
            logger.warning("Validation sémantique impossible: %s", e)
        
        return issues
    
    def _resolve_alias_to_file(self, alias: str, files: List[str]) -> Optional[str]:
        """Résout un alias SQL vers un nom de fichier"""
        # Recherche partielle
        for file in files:
            if alias.lower() in file.lower() or file.lower() in alias.lower():
                return file
        return None
    
    def _get_column_type(self, file: str, column: str) -> Optional[str]:
        """Récupère le type d'une colonne"""
        if file in self.kg.metadata and column in self.kg.metadata[file]:
            return self.kg.metadata[file][column].dtype
        return None
    
    def _are_types_compatible(self, type1: str, type2: str) -> bool:
        """Vérifie la compatibilité de deux types"""
        # Normaliser les types
        type1 = type1.lower()
        type2 = type2.lower()
        
        # Types identiques
        if type1 == type2:
            return True
        
        # Groupes de types compatibles
        numeric_types = {'int64', 'int32', 'float64', 'float32', 'int', 'float'}
        string_types = {'object', 'string', 'str'}
        
        if type1 in numeric_types and type2 in numeric_types:
            return True
        
        if type1 in string_types and type2 in string_types:
            return True
        
        return False
    
    def generate_audit_report(self, issues: List[ValidationIssue]) -> str:
        """Génère un rapport d'audit formaté"""
        report = ["=== TRUST LAYER - AUDIT REPORT ===\n"]
        
        critical = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
        infos = [i for i in issues if i.severity == ValidationSeverity.INFO]
        
        report.append(f"🚨 Erreurs critiques: {len(critical)}")
        report.append(f"⚠️  Avertissements: {len(warnings)}")
        report.append(f"ℹ️  Informations: {len(infos)}\n")
        
        if critical:
            report.append("\n🚨 ERREURS CRITIQUES:")
            for issue in critical:
                report.append(f"   [{issue.rule}] {issue.message}")
                if issue.suggestion:
                    report.append(f"      Suggestion: {issue.suggestion}")
        
        if warnings:
            report.append("\n⚠️  AVERTISSEMENTS:")
            for issue in warnings:
                report.append(f"   [{issue.rule}] {issue.message}")
                if issue.suggestion:
                    report.append(f"      Suggestion: {issue.suggestion}")
        
        if infos:
            report.append("\nℹ️  INFORMATIONS:")
            for issue in infos:
                report.append(f"   [{issue.rule}] {issue.message}")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test du module
    from modules.knowledge_graph import LivingKnowledgeGraph
    
    kg = LivingKnowledgeGraph()
    kg.scan_data_products()
    
    trust_layer = TrustLayer(knowledge_graph=kg)
    
    # Test avec une requête SQL
    test_sql = """
    SELECT c.Nom, SUM(s.Montant) as Total
    FROM 'data/customer_domain.parquet' AS c
    JOIN 'data/sales_domain.parquet' AS s ON c.ID_Client = s.ID_Client
    GROUP BY c.Nom
    ORDER BY Total DESC
    LIMIT 10
    """
    
    passed, issues = trust_layer.validate_execution_plan(
        sql_query=test_sql,
        required_files=["customer_domain", "sales_domain"],
        required_columns={
            "customer_domain": ["Nom", "ID_Client"],
            "sales_domain": ["ID_Client", "Montant"]
        }
    )
    
    print("\n" + trust_layer.generate_audit_report(issues))
    print(f"\n{'✓ VALIDATION PASSED' if passed else '✗ VALIDATION FAILED'}")
