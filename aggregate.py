#!/usr/bin/env python3

import json
import time
import zmq
import zconfig
import zutils


def main():
    """Implements L3 component of the system which essentially
       computes and forwards average of the received data points."""

    # init logger
    logger = zutils.getLogger(__name__)

    # socket to receive data
    ctx = zmq.Context()
    subsock = ctx.socket(zmq.SUB)
    subsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.PUB_PORT))
    subsock.setsockopt(zmq.SUBSCRIBE, str.encode(zconfig.TOPIC_ACCU))

    # socket to send data on
    pubsock = ctx.socket(zmq.PUB)
    pubsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.SUB_PORT))
    time.sleep(1)

    # stores all the aggregated data
    data = {}

    # receive loop
    logger.info("Started aggregate service")
    while True:
        try:
            [topic, message] = subsock.recv_multipart()
            topic = topic.decode()
            message = json.loads(message.decode())
            process_message(data, topic, message, pubsock)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break
            else:
                raise
        except KeyboardInterrupt:
            logger.info("Recevied interrupt to stop aggregate service")
            break

    # clean up
    logger.info("Stopped aggregate service")
    subsock.close()
    pubsock.close()
    ctx.term()


def process_message(data, topic, message, pubsock):
    [_, app, node] = topic.split()

    if not app in data:
        data[app] = {}

    # check if we have received the data for a node yet.
    # if data already exists, we should first flush the
    # existing all the data and then store more data
    if node in data[app]:
        aggr = 0
        for _, item in data[app].items():
            aggr += item
        data[app] = {}
        send_event(pubsock, aggr, app)

    aggr = 0
    for item in message:
        aggr += item["requests"]
    data[app][node] = aggr


def send_event(pubsock, total_requests, app):
    # type-application-node, topics are filtered using prefix matching
    topic = "{} {}".format(zconfig.TOPIC_AGGR, app)
    message = json.dumps({"total_requests": total_requests})
    pubsock.send_multipart([str.encode(topic), str.encode(message)])

if __name__ == "__main__":
    main()
