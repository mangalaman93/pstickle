import logging
import zconfig


def getLogger(module):
    """returns a logger with default configurations"""

    logging.basicConfig(format='%(name)s :: %(levelname)s :: %(message)s',
                        level=zconfig.LOG_LEVEL)
    return logging.getLogger(module)
