import zmq
import sys
import time
from datetime import datetime
from pprint import pprint
import json
from candles import Candles, Candle
from oandastream import OandaStream,ZMQ_OPTION

if __name__ == '__main__':
  try:
    #subscribe to the events and prices feed
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect(ZMQ_OPTION['events']['addr'])
    sock.setsockopt(zmq.SUBSCRIBE, ZMQ_OPTION['events']['kw'])
    sock.connect(ZMQ_OPTION['prices']['addr'])
    sock.setsockopt(zmq.SUBSCRIBE, ZMQ_OPTION['prices']['kw'])
    sock.connect(ZMQ_OPTION['clocks']['addr'])
    sock.setsockopt(zmq.SUBSCRIBE, ZMQ_OPTION['clocks']['kw'])
    candles=Candles(3)
    # recv
    while True:
      s = sock.recv_string()
      event = s[:3]
      msg = s[4:]
      if event=='TCK' : print event+",", 
      if event == ZMQ_OPTION['clocks']['kw']:
        o=json.loads(msg)
        candles.update(o)
      elif event == ZMQ_OPTION['prices']['kw']:
        o=json.loads(msg)
        if o.has_key('tick'): candles.update(o['tick'])

  except KeyboardInterrupt:
    print " Done..."
  except Exception as e:
    print e.message
  finally:
    if sock: 
      sock.setsockopt( zmq.LINGER, 0 )  #           to avoid hanging infinitely
      sock.close()                      # .close()  for all sockets & devices

