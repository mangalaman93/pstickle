import zmq


class Proxy(object):
    """Centralized proxy (Hub) for relaying pub-sub messages"""

    def __init__(self, host="127.0.0.1", subport=8000, pubport=8001):
        super(Proxy, self).__init__()

        # zmq context
        self.ctx = zmq.Context()

        # proxy socket for subscribers to connect
        self.pubsock = self.ctx.socket(zmq.XPUB)
        self.pubsock.bind("tcp://{}:{}".format(host, pubport))

        # proxy socket for publishers to connect
        self.subsock = self.ctx.socket(zmq.XSUB)
        self.subsock.bind("tcp://{}:{}".format(host, subport))

    def start(self):
        try:
            zmq.proxy(self.pubsock, self.subsock)
        except KeyboardInterrupt:
            pass

    def cleanup(self):
        self.pubsock.close()
        self.subsock.close()
        self.ctx.term()
