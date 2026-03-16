import json
from datetime import datetime
from backend.core.logging_config import logger

class AuditTrail:
    """Consigne les événements métier critiques pour le monitoring."""

    @staticmethod
    def log_ingestion_attempt(source: str, dataset: str, status: str, details: dict):
        """Logue une tentative d'ingestion de données."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "INGESTION_ATTEMPT",
            "source": source,
            "dataset": dataset,
            "status": status,
            "details": details
        }
        logger.info(f"AUDIT_INGESTION: {json.dumps(entry)}")

    @staticmethod
    def log_data_quality_issue(indicator: str, reason: str, value: any, details: dict):
        """Logue un problème de qualité détecté lors de la validation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "DATA_QUALITY_ISSUE",
            "indicator": indicator,
            "reason": reason,
            "value": value,
            "details": details
        }
        logger.warning(f"AUDIT_QUALITY: {json.dumps(entry)}")

    @staticmethod
    def log_ai_usage(user_query: str, intent: str, response_time_ms: float):
        """Logue l'usage de l'IA pour analyse d'usage et performance."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "AI_USAGE",
            "query": user_query,
            "intent": intent,
            "latency": response_time_ms
        }
        logger.info(f"AUDIT_USAGE: {json.dumps(entry)}")

# Instance globale
audit_trail = AuditTrail()
