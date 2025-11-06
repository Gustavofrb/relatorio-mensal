# src/data_collector.py

import io
import logging
from typing import Dict

import pandas as pd
import requests

from config import API_BASE_URL, API_TOKEN

class DataCollector:
    def __init__(self) -> None:
        self.base_url = API_BASE_URL.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json"
        })

    def _get(self, path: str, **params) -> dict:
        url = f"{self.base_url}{path}"
        logging.info(f"GET {url} params={params}")
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _get_csv(self, path: str, **params) -> pd.DataFrame:
        url = f"{self.base_url}{path}"
        logging.info(f"GET CSV {url} params={params}")
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return pd.read_csv(io.StringIO(resp.text))

    def fetch_bookings_operational(self, month: str) -> pd.DataFrame:
        """
        Busca dados operacionais de reservas por imóvel.
        Idealmente filtra pelo mês. Se a API não tiver filtro de mês,
        você filtra depois por data.
        """
        response = self._get("/bookings-operational", month=month)
        df = pd.DataFrame(response.get("data", []))
        logging.info(f"bookings-operational: {df.shape[0]} linhas")
        return df

    def fetch_property_details(self) -> pd.DataFrame:
        response = self._get("/property-details")
        df = pd.DataFrame(response.get("data", []))
        logging.info(f"property-details: {df.shape[0]} linhas")
        return df

    def fetch_platform_fees(self) -> pd.DataFrame:
        """
        Busca taxas por cidade. Se tiver paginação, você pode iterar até acabar.
        Aqui deixo simples em uma única chamada.
        """
        response = self._get("/platform-fees")
        df = pd.DataFrame(response.get("data", []))
        logging.info(f"platform-fees: {df.shape[0]} linhas")
        return df

    def fetch_guest_feedback(self, month: str) -> pd.DataFrame:
        """
        Feedbacks dos hóspedes (CSV).
        """
        df = self._get_csv("/download/guest-feedback", month=month)
        logging.info(f"guest-feedback: {df.shape[0]} linhas")
        return df

    def fetch_extra_costs(self, month: str) -> pd.DataFrame:
        """
        Custos extras por imóvel (CSV).
        """
        df = self._get_csv("/download/extra-costs", month=month)
        logging.info(f"extra-costs: {df.shape[0]} linhas")
        return df

    def collect_all(self, month: str) -> Dict[str, pd.DataFrame]:
        """
        Coleta todas as fontes de dados necessárias para o fechamento do mês.
        """
        logging.info(f"Iniciando coleta de dados para o mês {month}")
        bookings = self.fetch_bookings_operational(month)
        properties = self.fetch_property_details()
        fees = self.fetch_platform_fees()
        feedback = self.fetch_guest_feedback(month)
        costs = self.fetch_extra_costs(month)

        return {
            "bookings": bookings,
            "properties": properties,
            "fees": fees,
            "feedback": feedback,
            "costs": costs,
            "month": month
        }
