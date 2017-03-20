import logging

# log level
LOG_LEVEL = logging.DEBUG

# topics
TOPIC_GEN = "src"
TOPIC_ACCU = "accu"

# other
ACCU_SIZE = 60

# zmq ports
# TODO: Assuming all services run on the same host
IP_ADDR = "127.0.0.1"
SUB_PORT = 8000
PUB_PORT = 8001

# simulation parameters
NUM_NODES = 1000
NUM_APPS = 5
BEGIN_TIME = 0
END_TIME = 900
