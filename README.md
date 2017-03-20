# pstickle
Publish Subscribe System using ZMQ

# System Architecture
## System Components
`pstickle` consists of 5 components as shown in the following figure.

![Components](https://raw.githubusercontent.com/mangalaman93/pstickle/master/images/arch.jpg)

## Flow of messages
Messages are passed around using an intermediary `proxy`. It implements
ZMQ `XPUB` and `XSUB` sockets which can be connected from publishers and
subscribers. First, all subscribers send their respective subscriptions
to the proxy. Proxy then, relays all the subscriptions to all the
publishers. Publishers filter messages based on the received subscription
and forwards them to correct subscribers. Here, proxy allows us to
dynamically add and remove publishers and subsribers to/form the system.

![Components](https://raw.githubusercontent.com/mangalaman93/pstickle/master/images/flow.jpg)

## Limitations
* Assumes FIFO oredering of messages
* Assumes all the components run on localhost (easy to configure)

# How to Run
Run following commands on different terminals simultaneously:
```
[1] $ ./proxy.py
[2] $ ./accumulate.py
[3] $ ./aggregate.py
[4] $ ./loadgen.py
[5] $ ./storage.py
```
