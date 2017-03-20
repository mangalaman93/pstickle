#!/usr/bin/env python3

import json
import zmq
import zconfig
import zutils


def main():
    logger = zutils.getLogger(__name__)

    ctx = zmq.Context()
    subsock = ctx.socket(zmq.SUB)
    subsock.connect("tcp://{}:{}".format(zconfig.IP_ADDR,
                                         zconfig.PROXY_PUB_PORT))
    subsock.setsockopt(zmq.SUBSCRIBE, b"raw")

    logger.info("Started cum60 service")
    while True:
        try:
            [topic, message] = subsock.recv_multipart()
            topic = topic.decode()
            message = json.loads(message.decode())
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break
            else:
                raise
        except KeyboardInterrupt:
            logger.info("Recevied interrupt to stop cum60 service")
            break

if __name__ == "__main__":
    main()
