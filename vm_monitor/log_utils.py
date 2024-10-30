import logging.config
import os

def create_log_directory(log_dir):
    """
    Creates the log directory if it does not exist.

    Args:
       log_dir (str): The directory where logs should be saved.
    """
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Created logs directory at {log_dir}")
    except OSError as e:
        print(f"Error creating log directory: {e}")
        raise

def configure_logging():
    """
    Configures the logging system based on logging.conf configuration.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'logging.conf')
    create_log_directory(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    logging.config.fileConfig(config_path, disable_existing_loggers=False)
    return logging.getLogger()

def log_warning(message: str) -> None:
    """
    Logs a warning message using the configured root logger.

    Args:
       message (str): The message to log as a warning.
    """
    logger = configure_logging() 
    logger.warning(message)

def log_error(message: str) -> None:
    """
    Logs an error message using the configured root logger.

    Args:
       message (str): The message to log as an error.
    """
    logger = configure_logging()
    logger.error(message)

def log_info(message: str) -> None:
    """
    Logs an informational message using the configured root logger.

    Args:
       message (str): The message to log as information.
    """
    logger = configure_logging()
    logger.info(message)
