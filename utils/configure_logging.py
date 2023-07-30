import os
import logging
from typing import Optional

def configure_logging(log_file: Optional[str] = None, log_level: int = logging.WARNING,
                      log_format: Optional[str] = None) -> None:
    """
    Configures logging with the given log_file, log_level, and log_format.
    If the directory for the log_file does not exist, it will be created.

    Parameters:
        log_file (str, optional): The file path to save the log messages.
                                  Default is None (no file logging).
        log_level (int, optional): The log level (e.g., logging.DEBUG, logging.INFO, etc.).
                                   Default is logging.WARNING.
        log_format (str, optional): The log message format. Default is None, which uses
                                    '[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s'.

    Returns:
        None
    """
    if log_file is not None and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    if log_format is None:
        log_format = '[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s'

    logging.basicConfig(filename=log_file, format=log_format, level=log_level)