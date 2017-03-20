import logging

# log level
LOG_LEVEL = logging.DEBUG

# topics
TOPIC_GEN = "src"
TOPIC_ACCU = "accu"
TOPIC_AGGR = "aggr"

# other
ACCU_SIZE = 60
OUT_FOLDER = "out"
OUT_FILE = "sum"
WAIT_DUR = 1

# zmq ports
# TODO: Assuming all services run on the same host
IP_ADDR = "127.0.0.1"
SUB_PORT = 8000
PUB_PORT = 8001

# simulation parameters
NUM_NODES = 1000
NUM_APPS = 5
BEGIN_TIME = 1
END_TIME = 901
