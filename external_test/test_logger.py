from simple_otel_logger.logger import ConsoleLogger

logger = ConsoleLogger(service_name="auth-service")


def create_user(user_id: int):
    logger.info("Creating user", {"user_id": user_id})

    try:
        # simulate work
        result = {"status": "created"}
        logger.info("User created successfully", result)
        return result

    except Exception as e:
        logger.error("User creation failed", {"error": str(e)})
        raise
