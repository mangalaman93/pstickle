#!/usr/bin/env python3

import zconfig
import zmq
import zutils


def main():
    # log settings
    logger = zutils.getLogger(__name__)

    # zmq context
    ctx = zmq.Context()

    # proxy socket for subscribers to connect
    pubsock = ctx.socket(zmq.XPUB)
    pubsock.bind("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.PROXY_PUB_PORT))

    # proxy socket for publishers to connect
    subsock = ctx.socket(zmq.XSUB)
    subsock.bind("tcp://{}:{}".format(zconfig.IP_ADDR, zconfig.PROXY_SUB_PORT))

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
