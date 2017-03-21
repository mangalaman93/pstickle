#!/usr/bin/env python3

import drop
import itertools
import logging
import os
import proxy
import random
import threading

# topics
TOPIC_GENERATOR = "0"
TOPIC_ACCUMULATOR = "1"
TOPIC_AGGREGATOR = "2"

# simulation parameters
NUM_NODES = 1000
NUM_APPS = 5
BEGIN_TIME = 1
END_TIME = 901

# other
ACCU_SIZE = 60
OUT_FOLDER = "out"
OUT_FILE = "sum"


def getLogger(module):
    """returns a logger with default configurations"""
    logging.basicConfig(format='%(name)s :: %(levelname)s :: %(message)s',
                        level=logging.DEBUG)
    return logging.getLogger(module[:5])


###############################################################################
###############################   Proxy (Hub)   ###############################
###############################################################################
def run_proxy():
    logger = getLogger("proxy")

    hub = proxy.Proxy()
    logger.info("Starting proxy service")
    hub.start()

    logger.info("Stopping proxy service")
    hub.cleanup()


###############################################################################
#############################   Load Generator    #############################
###############################################################################
def run_load_generator():
    logger = getLogger("generator")

    apps = list(range(NUM_APPS))
    nodes = list(range(NUM_NODES))
    apps_nodes = list(itertools.product(apps, nodes))

    logger.info("Starting load generator")
    load_generator = drop.Drop()
    for curtime in range(BEGIN_TIME, END_TIME):
        random.shuffle(apps_nodes)
        for (app, node) in apps_nodes:
            send_topic = "{}".format(TOPIC_GENERATOR)
            message = {"time": curtime,
                       "app": app,
                       "node": node,
                       "requests": random.randrange(1000)}
            load_generator.send_event(send_topic, message)

        if curtime % 60 * 5 == 0:
            logger.debug("current time: {}".format(curtime))

    logger.info("Stopping load generator")
    load_generator.cleanup()


###############################################################################
###############################   Accumulator   ###############################
###############################################################################
acc_data = {}

def ac_process_message(drop, topic, message):
    curtime = message["time"]
    app = message["app"]
    node = message["node"]

    if not node in acc_data:
        acc_data[node] = {}
    if not app in acc_data[node]:
        acc_data[node][app] = []
    acc_data[node][app].append(message)

    if curtime % ACCU_SIZE == 0:
        send_topic = "{}".format(TOPIC_ACCUMULATOR)
        drop.send_event(send_topic, {"app": app,
                                     "node": node,
                                     "data": acc_data[node][app]})
        acc_data[node][app] = []

def run_accumulator():
    logger = getLogger("accumulator")

    accumulator = drop.Drop(subscriptions=[TOPIC_GENERATOR])
    logger.info("Starting accumulator service")
    accumulator.receive_loop(ac_process_message)

    logger.info("Stopping accumulator service")
    accumulator.cleanup()


###############################################################################
###############################   Aggregator    ###############################
###############################################################################
agg_data = {}

def ag_process_message(drop, topic, message):
    app = message["app"]
    node = message["node"]

    if not app in agg_data:
        agg_data[app] = {}

    # check if we have received the data for a node yet.
    # if data already exists, we should first flush the
    # existing all the data and then store more data
    if node in agg_data[app]:
        aggr = 0
        for _, item in agg_data[app].items():
            aggr += item

        drop.send_event(TOPIC_AGGREGATOR, {"app": app, "aggr": aggr})
        agg_data[app] = {}

    aggr = 0
    for item in message["data"]:
        aggr += item["requests"]
    agg_data[app][node] = aggr

def run_aggregator():
    logger = getLogger("aggregator")

    aggregator = drop.Drop(subscriptions=[TOPIC_ACCUMULATOR])
    logger.info("Starting aggregator service")
    aggregator.receive_loop(ag_process_message)\

    aggregator.info("Stopping aggregator service")
    aggregator.cleanup()


###############################################################################
#################################  Storage    #################################
###############################################################################
files = {}

def s_process_message(drop, topic, message):
    app = message["app"]

    if not app in files:
        if not os.path.exists(OUT_FOLDER):
            os.makedirs(OUT_FOLDER)

        filename = "{}/{}_{}.txt".format(OUT_FOLDER, OUT_FILE, app)
        files[app] = open(filename, "w+")

    files[app].write("{}\n".format(message["aggr"]))
    files[app].flush()


def run_storage():
    logger = getLogger("storage")

    storage = drop.Drop(subscriptions=[TOPIC_AGGREGATOR])
    logger.info("Starting storage service")
    storage.receive_loop(s_process_message)

    logger.info("Stopping storage service")
    storage.cleanup()
    for _, fd in files.items():
        fd.close()


## Run all the components (drops)
tproxy = threading.Thread(target=run_proxy)
tproxy.start()
tstorage = threading.Thread(target=run_storage)
tstorage.start()
taggregator = threading.Thread(target=run_aggregator)
taggregator.start()
taccumulator = threading.Thread(target=run_accumulator)
taccumulator.start()
tgenerator = threading.Thread(target=run_load_generator)
tgenerator.start()

# wait for all threads to finish
try:
    tproxy.join()
    tstorage.join()
    taggregator.join()
    taccumulator.join()
    tgenerator.join()
except KeyboardInterrupt:
    pass
