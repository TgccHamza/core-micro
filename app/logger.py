import logging

log_file = "uvicorn_logs.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),  # Save logs to a file
                        logging.StreamHandler()  # Also log to console
                    ])
logger = logging.getLogger(__name__)