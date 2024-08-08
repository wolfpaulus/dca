"""
Setting up a logger that still works when the app is containerized
The configuration file 'logconfig.yaml' is in YAML format and is loaded using the PyYAML library.
It specifies the loggers, handlers, and formatters. The loggers are named 'foo_logger' and 'bar_logger'.
Author: Wolf Paulus (wolf@paulus.com)
"""
from sys import stdout, stderr
import logging.config
import yaml  # PyYAML


try:
    with open('./src/logconfig.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logger = logging.getLogger("foo_logger")
except OSError as err:
    logger = logging.getLogger('bar_logger')
    logger.setLevel(logging.DEBUG)  # set logger level
    logFormatter = logging.Formatter(
        "%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s")
    # set streamhandler to stderr
    consoleHandler = logging.StreamHandler(stderr)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    logger.error(f"Using 'bar_logger', because of {err}")

if __name__ == "__main__":
    logger.debug('This is a debug message')
    logger.warning('This is a warning message')
    logger.error('This is a error message')
