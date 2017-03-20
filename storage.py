#!/usr/bin/env python3

import json
import os
import zmq
import zconfig
import zutils


def main():
    """Implements L5 component of the system which
       stores all the data into files on disk."""

    # init logger
    logger = zutils.getLogger(__file__)

    # socket to receive data
    ctx = zmq.Context()
    subsock = ctx.socket(zmq.SUB)
    subsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.PUB_PORT))
    subsock.setsockopt(zmq.SUBSCRIBE, str.encode(zconfig.TOPIC_AGGR))

    # stores all the file pointers data
    data = {}

    # receive loop
    logger.info("Started storage service")
    while True:
        try:
            [topic, message] = subsock.recv_multipart()
            topic = topic.decode()
            message = json.loads(message.decode())
            process_message(data, topic, message)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break
            else:
                raise
        except KeyboardInterrupt:
            logger.info("Recevied interrupt to stop storage service")
            break

    # clean up
    logger.info("Stopped storage service")
    subsock.close()
    ctx.term()
    for _, fd in data.items():
        fd.close()


def process_message(data, topic, message,):
    [_, app] = topic.split()

    if not app in data:
        if not os.path.exists(zconfig.OUT_FOLDER):
            os.makedirs(zconfig.OUT_FOLDER)
        filename = "{}/{}_{}.txt".format(zconfig.OUT_FOLDER,
                                         zconfig.OUT_FILE, app)
        data[app] = open(filename, "w+")

    data[app].write("{}\n".format(message["total_requests"]))
    data[app].flush()

if __name__ == "__main__":
    main()
