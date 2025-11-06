# src/data_loader.py

import logging
import sqlite3
from typing import Optional

import pandas as pd

from config import SQLITE_DB_PATH
from utils import ensure_dir

class DataLoader:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or SQLITE_DB_PATH
        ensure_dir(self.db_path.rsplit("/", 1)[0])

    def _get_connection(self):
        """
        Create a connection with timeout to prevent locks.
        Using DELETE mode instead of WAL for better compatibility with WSL/Windows.
        """
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        # Configurações para evitar locks
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def init_schema(self) -> None:
        """
        Cria o schema básico, se ainda não existir.
        """
        logging.info("Inicializando schema do banco de dados (se necessário)...")
        with self._get_connection() as conn:
            cur = conn.cursor()

            # Tabelas simples (ajuste conforme necessidade)
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS properties (
                    property_id TEXT PRIMARY KEY,
                    condominium TEXT,
                    city TEXT,
                    state TEXT,
                    region TEXT,
                    status TEXT
                );

                CREATE TABLE IF NOT EXISTS monthly_summary (
                    property_id TEXT,
                    month TEXT,
                    reservations_count INTEGER,
                    gross_revenue REAL,
                    occupied_days INTEGER,
                    occupancy_rate REAL,
                    condominium TEXT,
                    city TEXT,
                    state TEXT,
                    region TEXT,
                    status TEXT,
                    fee_percentage REAL,
                    platform_fee_amount REAL,
                    extra_cost_total REAL,
                    net_revenue REAL,
                    margin_value REAL,
                    margin_percent REAL,
                    avg_rating REAL,
                    complaints_list TEXT,
                    owner_name TEXT,
                    PRIMARY KEY (property_id, month)
                );
                """
            )

            conn.commit()
        logging.info("Schema pronto.")

    def save_properties(self, df: pd.DataFrame) -> None:
        """
        Salva/atualiza tabela de propriedades (dimensão).
        """
        logging.info("Salvando tabela 'properties'...")
        cols = ["property_id", "condominium", "city", "state", "region", "status"]
        props = df[cols].drop_duplicates("property_id")

        with self._get_connection() as conn:
            props.to_sql("properties", conn, if_exists="append", index=False)
        logging.info("Tabela 'properties' atualizada.")

    def save_monthly_summary(self, df: pd.DataFrame) -> None:
        logging.info("Salvando tabela 'monthly_summary'...")
        with self._get_connection() as conn:
            df.to_sql("monthly_summary", conn, if_exists="append", index=False)
        logging.info("Tabela 'monthly_summary' atualizada.")

    def save_all(self, unified_df: pd.DataFrame) -> None:
        """
        Inicializa schema (se necessário) e grava dados usando uma única conexão.
        """
        logging.info("Salvando dados no banco de dados...")
        
        # Usar uma única conexão para todas as operações
        with self._get_connection() as conn:
            # 1. Criar schema
            logging.info("Inicializando schema do banco de dados (se necessário)...")
            cur = conn.cursor()
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS properties (
                    property_id TEXT PRIMARY KEY,
                    condominium TEXT,
                    city TEXT,
                    state TEXT,
                    region TEXT,
                    status TEXT
                );

                CREATE TABLE IF NOT EXISTS monthly_summary (
                    property_id TEXT,
                    month TEXT,
                    reservations_count INTEGER,
                    gross_revenue REAL,
                    occupied_days INTEGER,
                    occupancy_rate REAL,
                    condominium TEXT,
                    city TEXT,
                    state TEXT,
                    region TEXT,
                    status TEXT,
                    fee_percentage REAL,
                    platform_fee_amount REAL,
                    extra_cost_total REAL,
                    net_revenue REAL,
                    margin_value REAL,
                    margin_percent REAL,
                    avg_rating REAL,
                    complaints_list TEXT,
                    owner_name TEXT,
                    PRIMARY KEY (property_id, month)
                );
                """
            )
            conn.commit()
            logging.info("Schema pronto.")
            
            # 2. Salvar properties (INSERT OR REPLACE para evitar duplicatas)
            logging.info("Salvando tabela 'properties'...")
            cols = ["property_id", "condominium", "city", "state", "region", "status"]
            props = unified_df[cols].drop_duplicates("property_id")
            
            # Inserir ou atualizar cada propriedade
            for _, row in props.iterrows():
                cur.execute("""
                    INSERT OR REPLACE INTO properties 
                    (property_id, condominium, city, state, region, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, tuple(row))
            
            conn.commit()
            logging.info("Tabela 'properties' atualizada.")
            
            # 3. Salvar monthly_summary (INSERT OR REPLACE para evitar duplicatas)
            logging.info("Salvando tabela 'monthly_summary'...")
            
            # Deletar dados existentes para o mesmo mês antes de inserir
            month_ref = unified_df['month'].iloc[0] if 'month' in unified_df.columns and len(unified_df) > 0 else None
            if month_ref:
                cur.execute("DELETE FROM monthly_summary WHERE month = ?", (month_ref,))
                logging.info(f"Dados existentes do mês {month_ref} removidos.")
            
            unified_df.to_sql("monthly_summary", conn, if_exists="append", index=False)
            logging.info("Tabela 'monthly_summary' atualizada.")
        
        logging.info("Dados salvos com sucesso!")
