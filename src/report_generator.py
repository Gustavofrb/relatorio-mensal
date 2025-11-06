# src/report_generator.py

import logging
import os
from typing import Dict

import pandas as pd

from config import OUTPUT_DIR
from utils import ensure_dir

class ReportGenerator:
    def __init__(self) -> None:
        ensure_dir(OUTPUT_DIR)

    def _save_csv(self, df: pd.DataFrame, filename: str) -> str:
        path = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(path, index=False)
        logging.info(f"Relatório salvo em {path}")
        return path

    def generate_financial_report(self, df: pd.DataFrame) -> str:
        """
        Relatório Financeiro geral e por imóvel.
        """
        financial_cols = [
            "property_id", "owner_name", "city", "state", "region", "month",
            "reservations_count", "gross_revenue",
            "platform_fee_amount", "extra_cost_total",
            "net_revenue", "margin_value", "margin_percent"
        ]
        financial_df = df[financial_cols].sort_values(
            ["month", "city", "property_id"]
        )
        return self._save_csv(financial_df, "relatorio_financeiro.csv")

    def generate_quality_report(self, df: pd.DataFrame) -> str:
        """
        Relatório de Qualidade da Experiência.
        """
        quality_cols = [
            "property_id", "owner_name", "city", "state", "region", "month",
            "avg_rating", "complaints_list"
        ]
        quality_df = df[quality_cols].sort_values(
            ["month", "avg_rating"], ascending=[True, False]
        )
        return self._save_csv(quality_df, "relatorio_qualidade.csv")

    def generate_occupancy_report(self, df: pd.DataFrame) -> str:
        """
        Painel de Ocupação e Inventário.
        """
        occupancy_cols = [
            "property_id", "owner_name", "city", "state", "region", "month",
            "reservations_count", "occupied_days", "occupancy_rate"
        ]
        occupancy_df = df[occupancy_cols].sort_values(
            ["month", "occupancy_rate"], ascending=[True, False]
        )
        return self._save_csv(occupancy_df, "relatorio_ocupacao.csv")

    def generate(self, unified_df: pd.DataFrame) -> Dict[str, str]:
        """
        Gera todos os relatórios principais e retorna os caminhos.
        """
        logging.info("Gerando relatórios...")
        financial_path = self.generate_financial_report(unified_df)
        quality_path = self.generate_quality_report(unified_df)
        occupancy_path = self.generate_occupancy_report(unified_df)

        return {
            "financial": financial_path,
            "quality": quality_path,
            "occupancy": occupancy_path,
        }
