#!/usr/bin/env python3

import json
import zmq
import zconfig
import zutils


def main():
    """Implements L2 component of the system which essentially
       accumulates set of data and forwards it to L3."""

    # init logger
    logger = zutils.getLogger(__name__)

    # socket to receive data
    ctx = zmq.Context()
    subsock = ctx.socket(zmq.SUB)
    subsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR,
                                         zconfig.PROXY_PUB_PORT))
    subsock.setsockopt(zmq.SUBSCRIBE, str.encode(zconfig.GEN_TOPIC))

    # socket to send data on
    pubsock = ctx.socket(zmq.PUB)
    pubsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR,
                                         zconfig.PROXY_SUB_PORT))

    # stores all the accumulated data
    data = {}

    logger.info("Started accu service")
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
            logger.info("Recevied interrupt to stop accu service")
            break

    # clean up
    logger.info("Stopped accu service")
    subsock.close()
    ctx.term()


def process_message(data, topic, message, pubsock):
    curtime = message["time"]
    node = message["node"]
    app = message["app"]

    if not node in data:
        data[node] = {}
    if not app in data[node]:
        data[node][app] = []
    data[node][app].append(message)

    if curtime % zconfig.ACCU_SIZE == 0:
        send_event(pubsock, data[node][app], app, node)
        data[node][app] = []  # reinitialize


def send_event(pubsock, data, app, node):
    # type-application-node, topics are filtered using prefix matching
    topic = "{}-{}-{}".format(zconfig.ACCU_TOPIC, app, node)
    message = json.dumps({"node": node,
                          "app": app,
                          "data": data
                          })
    pubsock.send_multipart([str.encode(topic), str.encode(message)])

if __name__ == "__main__":
    main()
