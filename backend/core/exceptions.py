class HDIBaseException(Exception):
    """Exception de base pour le projet Haiti Data Intelligence."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}

class SourceConnectionError(HDIBaseException):
    """Erreur lors de la connexion à une source externe (API WB, FMI)."""
    pass

class DataValidationError(HDIBaseException):
    """Erreur lors de la validation qualitative des données."""
    pass

class AIServiceError(HDIBaseException):
    """Erreur critique du service LLM ou Vector Store."""
    pass

class InsufficientDataError(HDIBaseException):
    """Levée quand les données sont insuffisantes pour une analyse fiable."""
    pass

class PromptInjectionError(HDIBaseException):
    """Détectée lors de la validation des entrées utilisateur."""
    pass
