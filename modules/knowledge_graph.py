"""
ADOS - Living Knowledge Graph Module
Découverte automatique des relations sémantiques entre Data Products
"""

import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import re
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ColumnMetadata:
    """Métadonnées d'une colonne"""
    file: str
    column: str
    dtype: str
    sample_values: List
    is_id: bool = False
    cardinality: int = 0


@dataclass
class Relationship:
    """Relation sémantique entre deux colonnes"""
    source_file: str
    source_column: str
    target_file: str
    target_column: str
    relationship_type: str  # "join_key", "foreign_key", "semantic_match"
    confidence: float


class LivingKnowledgeGraph:
    """
    Graphe de connaissances qui scanne automatiquement les Data Products
    et découvre les relations sémantiques entre colonnes
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: Répertoire contenant les fichiers Parquet
        """
        self.data_dir = Path(data_dir)
        self.graph = nx.DiGraph()
        self.metadata: Dict[str, Dict[str, ColumnMetadata]] = {}
        self.relationships: List[Relationship] = []
        
        logger.info("LivingKnowledgeGraph initialisé")
    
    def scan_data_products(self) -> Dict[str, pd.DataFrame]:
        """
        Scanne tous les fichiers Parquet et extrait les métadonnées
        
        Returns:
            Dictionnaire des DataFrames chargés
        """
        logger.info("Scan des Data Products dans %s", self.data_dir)
        
        dataframes = {}
        parquet_files = list(self.data_dir.glob("*.parquet"))
        
        if not parquet_files:
            logger.warning("Aucun fichier Parquet trouvé dans %s", self.data_dir)
            return dataframes
        
        for file_path in parquet_files:
            file_name = file_path.stem
            df = pd.read_parquet(file_path)
            dataframes[file_name] = df
            
            # Extraire métadonnées par colonne
            self.metadata[file_name] = {}
            
            for col in df.columns:
                is_id = self._is_id_column(col)
                sample_values = df[col].dropna().head(100).tolist()
                cardinality = df[col].nunique()
                
                self.metadata[file_name][col] = ColumnMetadata(
                    file=file_name,
                    column=col,
                    dtype=str(df[col].dtype),
                    sample_values=sample_values,
                    is_id=is_id,
                    cardinality=cardinality
                )
            
            # Ajouter le fichier comme nœud dans le graphe
            self.graph.add_node(
                file_name,
                type="data_product",
                columns=list(df.columns),
                shape=df.shape
            )
            
            logger.info("✓ Scanné: %s (%d lignes, %d colonnes)", 
                       file_name, len(df), len(df.columns))
        
        return dataframes
    
    def _is_id_column(self, column_name: str) -> bool:
        """Détecte si une colonne est un identifiant"""
        id_patterns = [
            r'.*[_]?id[_]?.*',
            r'.*[_]?key[_]?.*',
            r'.*identifier.*',
            r'pk_.*',
            r'fk_.*'
        ]
        return any(re.match(pattern, column_name.lower()) for pattern in id_patterns)
    
    def discover_relationships(self, dataframes: Dict[str, pd.DataFrame]) -> List[Relationship]:
        """
        Découvre automatiquement les relations entre colonnes
        
        Args:
            dataframes: Dictionnaire des DataFrames
            
        Returns:
            Liste des relations découvertes
        """
        logger.info("Découverte des relations sémantiques...")
        
        self.relationships = []
        files = list(dataframes.keys())
        
        # Compare chaque paire de fichiers
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                df1 = dataframes[file1]
                df2 = dataframes[file2]
                
                # Chercher les colonnes avec des noms similaires
                for col1 in df1.columns:
                    for col2 in df2.columns:
                        # Méthode 1: Correspondance exacte de nom
                        if col1 == col2:
                            rel = Relationship(
                                source_file=file1,
                                source_column=col1,
                                target_file=file2,
                                target_column=col2,
                                relationship_type="exact_name_match",
                                confidence=0.9
                            )
                            self.relationships.append(rel)
                            self._add_edge_to_graph(rel)
                            logger.info("  Relation trouvée: %s.%s ↔ %s.%s (exact match)", 
                                      file1, col1, file2, col2)
                        
                        # Méthode 2: Correspondance de pattern ID
                        elif self._is_potential_join_key(col1, col2):
                            # Vérifier si les valeurs se chevauchent
                            overlap = self._calculate_value_overlap(df1[col1], df2[col2])
                            
                            if overlap > 0.1:  # Au moins 10% de chevauchement
                                rel = Relationship(
                                    source_file=file1,
                                    source_column=col1,
                                    target_file=file2,
                                    target_column=col2,
                                    relationship_type="join_key",
                                    confidence=min(overlap, 0.95)
                                )
                                self.relationships.append(rel)
                                self._add_edge_to_graph(rel)
                                logger.info("  Relation trouvée: %s.%s ↔ %s.%s (join key, conf=%.2f)", 
                                          file1, col1, file2, col2, overlap)
        
        logger.info("✓ %d relations découvertes", len(self.relationships))
        return self.relationships
    
    def _is_potential_join_key(self, col1: str, col2: str) -> bool:
        """Vérifie si deux colonnes peuvent être des clés de jointure"""
        # Extraire les parties significatives
        parts1 = set(re.split(r'[_\s]+', col1.lower()))
        parts2 = set(re.split(r'[_\s]+', col2.lower()))
        
        # Intersection significative
        common = parts1 & parts2
        
        # Si partagent "id", "client", "produit", etc.
        significant_keywords = {'id', 'key', 'client', 'produit', 'product', 'customer', 'transaction'}
        return len(common & significant_keywords) > 0
    
    def _calculate_value_overlap(self, series1: pd.Series, series2: pd.Series) -> float:
        """Calcule le pourcentage de valeurs communes entre deux séries"""
        set1 = set(series1.dropna().unique())
        set2 = set(series2.dropna().unique())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _add_edge_to_graph(self, rel: Relationship):
        """Ajoute une arête au graphe NetworkX"""
        self.graph.add_edge(
            rel.source_file,
            rel.target_file,
            source_column=rel.source_column,
            target_column=rel.target_column,
            type=rel.relationship_type,
            confidence=rel.confidence
        )
    
    def get_join_path(self, file1: str, file2: str) -> Optional[List[str]]:
        """
        Trouve le chemin de jointure entre deux fichiers
        
        Returns:
            Liste des fichiers formant le chemin, ou None si pas de chemin
        """
        try:
            path = nx.shortest_path(self.graph.to_undirected(), file1, file2)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_join_columns_for_path(self, path: List[str]) -> List[Tuple[str, str, str, str]]:
        """
        Retourne les colonnes de jointure pour un chemin
        
        Returns:
            Liste de tuples (file1, col1, file2, col2)
        """
        join_columns = []
        
        for i in range(len(path) - 1):
            file1, file2 = path[i], path[i+1]
            
            # Chercher la relation
            for rel in self.relationships:
                if (rel.source_file == file1 and rel.target_file == file2) or \
                   (rel.source_file == file2 and rel.target_file == file1):
                    join_columns.append((
                        rel.source_file,
                        rel.source_column,
                        rel.target_file,
                        rel.target_column
                    ))
                    break
        
        return join_columns
    
    def visualize_graph(self) -> str:
        """
        Génère une représentation textuelle du graphe
        
        Returns:
            Représentation en texte du graphe
        """
        output = ["=== Living Knowledge Graph ===\n"]
        output.append(f"Nœuds (Data Products): {self.graph.number_of_nodes()}")
        output.append(f"Relations: {self.graph.number_of_edges()}\n")
        
        for node in self.graph.nodes(data=True):
            file_name, attrs = node
            output.append(f"\n📦 {file_name}")
            output.append(f"   Colonnes: {', '.join(attrs['columns'])}")
            output.append(f"   Shape: {attrs['shape']}")
        
        if self.relationships:
            output.append("\n\n🔗 Relations découvertes:")
            for rel in self.relationships:
                output.append(f"   {rel.source_file}.{rel.source_column} ↔ "
                            f"{rel.target_file}.{rel.target_column} "
                            f"({rel.relationship_type}, conf={rel.confidence:.2f})")
        
        return "\n".join(output)
    
    def get_metadata_summary(self) -> Dict:
        """Retourne un résumé des métadonnées"""
        summary = {
            "total_files": len(self.metadata),
            "total_relationships": len(self.relationships),
            "files": {}
        }
        
        for file_name, columns in self.metadata.items():
            summary["files"][file_name] = {
                "total_columns": len(columns),
                "id_columns": [col for col, meta in columns.items() if meta.is_id],
                "columns": list(columns.keys())
            }
        
        return summary


if __name__ == "__main__":
    # Test du module
    kg = LivingKnowledgeGraph()
    dataframes = kg.scan_data_products()
    
    if dataframes:
        relationships = kg.discover_relationships(dataframes)
        print(kg.visualize_graph())
        
        # Test de chemin
        files = list(dataframes.keys())
        if len(files) >= 2:
            path = kg.get_join_path(files[0], files[1])
            if path:
                print(f"\n🛤️  Chemin de jointure: {' → '.join(path)}")
                joins = kg.get_join_columns_for_path(path)
                for j in joins:
                    print(f"   JOIN ON {j[0]}.{j[1]} = {j[2]}.{j[3]}")
