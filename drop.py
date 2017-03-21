import json
import time
import zmq


class Drop(object):
    """Implements a generic component of pub-sub system.
    A drop can subscribe to given list of topics and send
    event to the proxy using the send_event function."""

    def __init__(self, host="127.0.0.1", subport=8000, pubport=8001, subscriptions=[]):
        super(Drop, self).__init__()

        # zmq context
        self.ctx = zmq.Context()

        # socket to receive data
        self.subsock = self.ctx.socket(zmq.SUB)
        self.subsock.connect("tcp://{}:{}".format(host, pubport))
        for item in subscriptions:
            self.subsock.setsockopt(zmq.SUBSCRIBE, str.encode(item))

        # socket to send data on
        self.pubsock = self.ctx.socket(zmq.PUB)
        self.pubsock.connect("tcp://{}:{}".format(host, subport))

        # sleep for a sec, so that we have received subscriptions, if any.
        # This is not necessary but we prefer that subscribers receive
        # all the messages. It is not required for the correctness of the
        # system. See below link for more information -
        # http://zguide.zeromq.org/page:all#Missing-Message-Problem-Solver
        time.sleep(1)

    def receive_loop(self, process_message):
        while True:
            try:
                [byte_topic, byte_message] = self.subsock.recv_multipart()
                send_topic = byte_topic.decode()
                message = json.loads(byte_message.decode())
                process_message(self, send_topic, message)
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break
                else:
                    raise
            except KeyboardInterrupt:
                break

    def send_event(self, topic, message):
        data = json.dumps(message)
        self.pubsock.send_multipart([str.encode(topic), str.encode(data)])

    def cleanup(self):
        self.subsock.close()
        self.pubsock.close()
        self.ctx.term()
