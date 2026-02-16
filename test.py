from simple_otel_logger import ConsoleLogger, LoggerOptions

logger = ConsoleLogger(LoggerOptions("test-service"))

logger.info("Hello from python logger")
logger.error("invalid_data")