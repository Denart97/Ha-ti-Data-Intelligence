import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.logging_config import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """Intercepte les requêtes pour loguer le temps de réponse et les erreurs."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Injection du request_id dans le contexte pour suivi
        logger.info(f"REQ_START [{request_id}] {request.method} {request.url.path} from {request.client.host}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"REQ_END [{request_id}] status={response.status_code} "
                f"duration={process_time:.2f}ms"
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"REQ_FAIL [{request_id}] error={str(e)} "
                f"duration={process_time:.2f}ms", 
                exc_info=True
            )
            # Re-raise pour que FastAPI gère l'exception globalement
            raise e
