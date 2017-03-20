#!/usr/bin/env python3

import itertools
import json
import random
import time
import zconfig
import zmq
import zutils


def main():
    logger = zutils.getLogger(__name__)

    ctx = zmq.Context()
    pubsock = ctx.socket(zmq.PUB)
    pubsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR,
                                         zconfig.PROXY_SUB_PORT))

    # Node & Application IDs beginning with 0
    nodes = list(range(zconfig.NUM_NODES))
    apps = list(range(zconfig.NUM_APPS))
    nodes_apps = list(itertools.product(nodes, apps))

    # sleep for a sec, so that we have received subscriptions, if any.
    # This is not necessary but we prefer that subscribers receive
    # all the messages. It is not required for the correctness of the
    # system. See below link for more information -
    # http://zguide.zeromq.org/page:all#Missing-Message-Problem-Solver
    time.sleep(1)

    try:
        logger.info("Starting load generator")
        for curtime in range(zconfig.BEGIN_TIME, zconfig.END_TIME):
            random.shuffle(nodes_apps)
            for (node, app) in nodes_apps:
                send_event(pubsock, curtime, app, node)

            if curtime % 60 * 5 == 0:
                logger.debug("current time: {}".format(curtime))
    except KeyboardInterrupt:
        logger.info("Recevied interrupt to stop load generator")

    # clean up
    logger.info("Stopped load generator")
    pubsock.close()
    ctx.term()


def send_event(pubsock, curtime, app, node):
    # type-application-node, topics are filtered using prefix matching
    topic = "{}-{}-{}".format(zconfig.GEN_TOPIC, app, node)
    message = json.dumps({"time": curtime,
                          "node": node,
                          "app": app,
                          "requests": random.randrange(1000)
                          })
    pubsock.send_multipart([str.encode(topic), str.encode(message)])

if __name__ == "__main__":
    main()
