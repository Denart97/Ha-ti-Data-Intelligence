import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: str = "etl_process.log"):
    """Configure un logger qui écrit dans la console et dans un fichier."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Formatage
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler Fichier
    log_path = Path("logs") / log_file
    log_path.parent.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger global par défaut
logger = setup_logger("HDI_ETL")
