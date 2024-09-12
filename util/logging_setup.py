import logging
from .config_loader import ConfigLoader
from os.path import dirname, exists, join
from os import makedirs


def setup_logging():
    """Set up logging based on configuration."""
    # Load the logging configuration from config.json

    config_loader = ConfigLoader()
    config = config_loader.load_qgis_config()
    logging_config = config.get('logging', {})

    # Get the root logger
    logger = logging.getLogger()

    # Set to DEBUG to allow all levels, will filter later
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    if logger.hasHandlers():
        for handler in logger.handlers:
            handler.close()  # Close each handler
        logger.handlers.clear()

    if logging_config.get('enabled', False):
        # Set log file path from config, '.../log/app.log' if not provided
        log_file_path = logging_config.get('file_path') or join(
           dirname(dirname(__file__)), 'log', 'app.log')

        # Set log level from config, default to logging.INFO if not provided
        log_level_str = logging_config.get('level').upper() or 'INFO'
        log_level = getattr(logging, log_level_str, logging.INFO)

        # Ensure the directory for the log file exists
        log_dir = dirname(log_file_path)
        if log_dir and not exists(log_dir):
            makedirs(log_dir)

        log_format = (logging_config.get('format') or
                      '%(asctime)s - %(levelname)s - %(message)s')
        filemode = logging_config.get('filemode') or 'w'

        # Create file handler
        file_handler = logging.FileHandler(log_file_path, mode=filemode)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)

        logger.info("Logging is enabled.")
        print('Logging is enabled, logfile path: {}'
              .format(log_file_path.replace('\\', '/')))
    else:
        logger.addHandler(logging.NullHandler())
        print("Logging is disabled.")

    # Disable logging for requests and urllib3
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)
    return logger


# Create a logger instance
logger = setup_logging()
