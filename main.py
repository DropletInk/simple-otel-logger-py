from simple_otel_logger.structlog_config import configure_logging
from external_test.test_logger import create_user


def main():
    configure_logging()

    create_user(123)


if __name__ == "__main__":
    main()
