import logging
import sys

# Support both new and legacy pythonjsonlogger import paths
try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    from pythonjsonlogger.jsonlogger import JsonFormatter

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s'
    )
    log_handler.setFormatter(formatter)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(log_handler)
    return logger

logger = setup_logging()