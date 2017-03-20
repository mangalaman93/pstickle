import logging

# log level
LOG_LEVEL = logging.DEBUG

# topics
GEN_TOPIC = "raw"

# zmq ports
# TODO: Assuming all services run on the same host
IP_ADDR = "127.0.0.1"
PROXY_SUB_PORT = 8000
PROXY_PUB_PORT = 8001

# simulation parameters
NUM_NODES = 1000
NUM_APPS = 5
BEGIN_TIME = 0
END_TIME = 900
