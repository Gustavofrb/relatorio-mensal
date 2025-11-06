# src/data_transformer.py

import logging
from typing import Dict

import pandas as pd

from utils import get_days_in_month

class DataTransformer:
    def process(self, raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Recebe os dataframes brutos:
          - bookings
          - properties
          - fees
          - feedback
          - costs
        E devolve um dataframe consolidado por imóvel + mês.
        """
        bookings = raw_data["bookings"].copy()
        properties = raw_data["properties"].copy()
        fees = raw_data["fees"].copy()
        feedback = raw_data["feedback"].copy()
        costs = raw_data["costs"].copy()
        month = raw_data["month"]

        logging.info("Iniciando transformação dos dados...")

        # ------------------------------
        # 1) Agregação de reservas por imóvel
        # ------------------------------
        # Colunas reais da API:
        # bookings: property_id, booking_count, occupancy_days, gross_revenue
        group_cols = ["property_id"]

        # Os dados já vêm agregados da API, então apenas renomeamos
        agg_bookings = bookings.rename(columns={
            "booking_count": "reservations_count",
            "occupancy_days": "occupied_days"
        })

        days_in_month = get_days_in_month(month)
        agg_bookings["occupancy_rate"] = (
            agg_bookings["occupied_days"] / days_in_month
        )

        # ------------------------------
        # 2) Merge com detalhes do imóvel
        # ------------------------------
        # Colunas reais: property_id, condominium, city, state, region, status
        merged = agg_bookings.merge(
            properties,
            on="property_id",
            how="left",
            suffixes=("", "_prop")
        )

        # ------------------------------
        # 3) Merge com taxas por cidade
        # ------------------------------
        # fees: city, state, region, fee_percentage, month, year
        # Filtramos por mês/ano correspondente
        year, month_num = map(int, month.split("-"))
        fees_filtered = fees[
            (fees["year"] == year) & (fees["month"] == month_num)
        ].copy()
        
        merged = merged.merge(
            fees_filtered[["city", "fee_percentage"]],
            on="city",
            how="left"
        )

        merged["platform_fee_amount"] = (
            merged["gross_revenue"]
            * (merged["fee_percentage"].fillna(0) / 100)
        )

        # ------------------------------
        # 4) Custos extras
        # ------------------------------
        # costs: id_imovel, descricao_custo, custo_reais, data_custo
        costs = costs.rename(columns={"id_imovel": "property_id", "custo_reais": "extra_cost_value"})
        costs_grouped = costs.groupby("property_id").agg(
            extra_cost_total=("extra_cost_value", "sum")
        ).reset_index()

        merged = merged.merge(
            costs_grouped,
            on="property_id",
            how="left"
        )
        merged["extra_cost_total"] = merged["extra_cost_total"].fillna(0.0)

        # ------------------------------
        # 5) Feedback / Qualidade
        # ------------------------------
        # feedback: id_imovel, nota_media, principais_reclamacoes, comentarios_qualitativos
        feedback = feedback.rename(columns={
            "id_imovel": "property_id",
            "nota_media": "rating",
            "principais_reclamacoes": "complaint_category"
        })
        
        feedback_grouped = (
            feedback
            .groupby("property_id")
            .agg(
                avg_rating=("rating", "mean"),
                complaints_list=("complaint_category", lambda x: ", ".join(sorted(set(str(v) for v in x.dropna() if str(v) != 'nan')))),
            )
            .reset_index()
        )

        merged = merged.merge(
            feedback_grouped,
            on="property_id",
            how="left"
        )

        # ------------------------------
        # 6) KPIs Financeiros
        # ------------------------------
        merged["net_revenue"] = (
            merged["gross_revenue"]
            - merged["platform_fee_amount"]
            - merged["extra_cost_total"]
        )

        # Aqui você poderia definir "margem" como net_revenue / gross_revenue ou similar.
        merged["margin_value"] = merged["net_revenue"]
        merged["margin_percent"] = (
            merged["net_revenue"] / merged["gross_revenue"].replace(0, pd.NA)
        ) * 100

        # ------------------------------
        # 7) Adiciona coluna mês e condominium como owner_name
        # ------------------------------
        merged["month"] = month
        merged["owner_name"] = merged["condominium"]  # usando condominium como proxy para owner

        logging.info(f"Transformação concluída: {merged.shape[0]} linhas no dataset final.")
        return merged
