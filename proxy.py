#!/usr/bin/env python3

import zconfig
import zmq
import zutils


def main():
    # init logger
    logger = zutils.getLogger(__file__)

    # zmq context
    ctx = zmq.Context()

    # proxy socket for subscribers to connect
    pubsock = ctx.socket(zmq.XPUB)
    pubsock.bind("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.PUB_PORT))

    # proxy socket for publishers to connect
    subsock = ctx.socket(zmq.XSUB)
    subsock.bind("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.SUB_PORT))

    # proxy loop
    try:
        logger.info("Starting proxy service")
        logger.info("Hit Ctrl-C (or send SIGKILL) to stop the service!")
        zmq.proxy(pubsock, subsock)
    except KeyboardInterrupt:
        logger.info("Recevied interrupt to stop proxy service")

    # clean up
    logger.info("Stopped proxy service")
    pubsock.close()
    subsock.close()
    ctx.term()

if __name__ == "__main__":
    main()
