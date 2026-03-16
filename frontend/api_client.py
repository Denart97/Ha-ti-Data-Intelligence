import requests
from typing import Dict, Any, List, Optional
import streamlit as st

class APIClient:
    """Client pour interagir avec le backend FastAPI."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def post_chat(self, query: str) -> Dict[str, Any]:
        """Envoie une question à l'assistant IA."""
        try:
            response = requests.post(f"{self.base_url}/ai/ask", json={"query": query})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erreur lors de la communication avec l'IA : {e}")
            return {}

    def get_indicator_trend(self, indicator_code: str, country_iso: str) -> Dict[str, Any]:
        """Récupère les tendances pour un indicateur."""
        try:
            params = {"indicator_code": indicator_code, "country_iso": country_iso}
            response = requests.get(f"{self.base_url}/data/indicator-trend", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            return {}

    def compare_countries(self, indicator: str, countries: List[str]) -> Dict[str, Any]:
        """Compare plusieurs pays pour un indicateur."""
        try:
            payload = {"indicators": [indicator], "countries": countries}
            response = requests.post(f"{self.base_url}/data/compare", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erreur lors de la comparaison : {e}")
            return {}
