from dotenv import load_dotenv
import os

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

JSON_LOGS = os.getenv("JSON_LOGS", "True").lower() == "true"

SERVICE_NAME = os.getenv("SERVICE_NAME", "app-service")
