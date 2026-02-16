"""
ADOS - Data Generator Module
Génère des Data Products synthétiques pour simuler un Data Mesh
"""

import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataMeshSimulator:
    """Génère des Data Products décentralisés avec des relations cohérentes"""
    
    def __init__(self, seed: int = 42, output_dir: str = "data"):
        """
        Args:
            seed: Seed pour la reproductibilité
            output_dir: Répertoire de sortie pour les fichiers Parquet
        """
        self.seed = seed
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialisation Faker avec seed
        self.fake = Faker('fr_FR')
        Faker.seed(seed)
        np.random.seed(seed)
        
        # Données partagées pour cohérence entre domaines
        self.num_customers = 1000
        self.num_products = 200
        self.num_transactions = 5000
        
        # IDs de référence
        self.customer_ids = [f"CUST_{i:05d}" for i in range(1, self.num_customers + 1)]
        self.product_ids = [f"PROD_{i:04d}" for i in range(1, self.num_products + 1)]
        
        logger.info("DataMeshSimulator initialisé avec seed=%d", seed)
    
    def generate_customer_domain(self) -> pd.DataFrame:
        """
        Génère le Data Product: customer_domain
        
        Returns:
            DataFrame avec colonnes: ID_Client, Nom, Score_Fidélité, Région
        """
        logger.info("Génération du domaine Customer...")
        
        regions = ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur", 
                   "Nouvelle-Aquitaine", "Occitanie", "Hauts-de-France", "Grand Est", "Normandie"]
        
        data = {
            "ID_Client": self.customer_ids,
            "Nom": [self.fake.name() for _ in range(self.num_customers)],
            "Score_Fidelite": np.random.randint(0, 101, self.num_customers),
            "Region": np.random.choice(regions, self.num_customers),
            "Email": [self.fake.email() for _ in range(self.num_customers)],
            "Date_Inscription": [self.fake.date_between(start_date='-3y', end_date='today') 
                                  for _ in range(self.num_customers)]
        }
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / "customer_domain.parquet"
        df.to_parquet(output_path, index=False)
        
        logger.info("✓ customer_domain.parquet créé (%d lignes)", len(df))
        return df
    
    def generate_logistics_domain(self) -> pd.DataFrame:
        """
        Génère le Data Product: logistics_domain
        
        Returns:
            DataFrame avec colonnes: ID_Produit, Stock, Entrepôt, Délai_Livraison
        """
        logger.info("Génération du domaine Logistics...")
        
        warehouses = ["Paris_Hub", "Lyon_Central", "Marseille_Sud", "Lille_Nord", "Bordeaux_Ouest"]
        
        data = {
            "ID_Produit": self.product_ids,
            "Stock": np.random.randint(0, 500, self.num_products),
            "Entrepot": np.random.choice(warehouses, self.num_products),
            "Delai_Livraison": np.random.randint(1, 15, self.num_products),  # Jours
            "Cout_Stockage": np.round(np.random.uniform(5, 50, self.num_products), 2),
            "Derniere_Mise_A_Jour": [self.fake.date_time_between(start_date='-30d', end_date='now') 
                                      for _ in range(self.num_products)]
        }
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / "logistics_domain.parquet"
        df.to_parquet(output_path, index=False)
        
        logger.info("✓ logistics_domain.parquet créé (%d lignes)", len(df))
        return df
    
    def generate_sales_domain(self) -> pd.DataFrame:
        """
        Génère le Data Product: sales_domain
        
        Returns:
            DataFrame avec colonnes: Transactions, ID_Client, ID_Produit, Montant
        """
        logger.info("Génération du domaine Sales...")
        
        data = {
            "ID_Transaction": [f"TXN_{i:08d}" for i in range(1, self.num_transactions + 1)],
            "ID_Client": np.random.choice(self.customer_ids, self.num_transactions),
            "ID_Produit": np.random.choice(self.product_ids, self.num_transactions),
            "Montant": np.round(np.random.uniform(10, 1000, self.num_transactions), 2),
            "Quantite": np.random.randint(1, 10, self.num_transactions),
            "Date_Transaction": [self.fake.date_time_between(start_date='-1y', end_date='now') 
                                 for _ in range(self.num_transactions)],
            "Statut": np.random.choice(["Confirmé", "En attente", "Annulé"], 
                                       self.num_transactions, 
                                       p=[0.85, 0.10, 0.05])
        }
        
        df = pd.DataFrame(data)
        output_path = self.output_dir / "sales_domain.parquet"
        df.to_parquet(output_path, index=False)
        
        logger.info("✓ sales_domain.parquet créé (%d lignes)", len(df))
        return df
    
    def generate_all_domains(self) -> Dict[str, pd.DataFrame]:
        """
        Génère tous les Data Products
        
        Returns:
            Dictionnaire avec les 3 DataFrames
        """
        logger.info("=== Génération de tous les Data Products ===")
        
        domains = {
            "customer": self.generate_customer_domain(),
            "logistics": self.generate_logistics_domain(),
            "sales": self.generate_sales_domain()
        }
        
        logger.info("=== Génération terminée ===")
        return domains
    
    def get_metadata(self) -> Dict:
        """Retourne les métadonnées des Data Products générés"""
        return {
            "num_customers": self.num_customers,
            "num_products": self.num_products,
            "num_transactions": self.num_transactions,
            "output_directory": str(self.output_dir),
            "files": [
                "customer_domain.parquet",
                "logistics_domain.parquet",
                "sales_domain.parquet"
            ]
        }


if __name__ == "__main__":
    # Test du module
    simulator = DataMeshSimulator()
    domains = simulator.generate_all_domains()
    
    print("\n📊 Résumé des données générées:")
    for name, df in domains.items():
        print(f"\n{name.upper()} Domain:")
        print(f"  Shape: {df.shape}")
        print(f"  Colonnes: {', '.join(df.columns)}")
        print(f"  Aperçu:\n{df.head(3)}")
