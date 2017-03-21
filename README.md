# pstickle
Publish Subscribe System using ZMQ

# How to Run
```
$ ./main.py
```

# System Architecture
## System Components
`pstickle` consists of 5 components (drops) as shown in the following figure:
![Components](https://raw.githubusercontent.com/mangalaman93/pstickle/master/images/arch.jpg)

## Flow of messages
Messages are passed around using an intermediary `proxy`. It implements
ZMQ `XPUB` and `XSUB` sockets which can be connected from publishers and
subscribers. First, all subscribers send their respective subscriptions
to the proxy. Proxy then, relays all the subscriptions to all the
publishers. Publishers filter messages based on the received subscription
and forwards them to correct subscribers through the proxy. Here, proxy
allows us to dynamically add and remove publishers and subsribers to/form
the system.

Following figure shows the flow of messages in the system:
![Components](https://raw.githubusercontent.com/mangalaman93/pstickle/master/images/flow.jpg)

## Limitations
* `main.py` only runs on localhost
* Doesn't stop cleanly on `ctrl+c`
* Subscribers do not receive messages until the subscription has been completely processed by the publishers which can result in loss of messages
