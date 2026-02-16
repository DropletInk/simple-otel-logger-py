from simple_otel_logger import ConsoleLogger

logger = ConsoleLogger("test-service")

logger.info("Hello from external folder")
logger.error("Something broke")
