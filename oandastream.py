#!/usr/bin/env python

###
# streaming events or prices from OANDA with ZeroMQ - Pete Werner, 2016
# more info: http://petewerner.blogspot.com/2016/01/streaming-oanda-with-python-and-zeromq.html
###

import zmq
import requests
from requests.exceptions import ConnectionError
import sys
import time
from datetime import datetime
from pprint import pprint
import json
from candles import Candles, Candle
ZMQ_OPTION={
  'prices':{'kw':'TCK', 'addr':'tcp://127.0.0.1:8007'},
  'events':{'kw':'EVT', 'addr':'tcp://127.0.0.1:8008'},
  'clocks':{'kw':'CLK', 'addr':'tcp://127.0.0.1:8009'},
}


#oanda settings

#our local zeromq endpoints

class OandaStream(object):

  def __init__(self, name, domain, token,  timeout):
    self.name = name
    self.access_token = token
    self.streaming_domain = domain
    self.zmq_addr = ZMQ_OPTION[name]['addr']
    self.zmq_filter = ZMQ_OPTION[name]['kw']
    self.timeout = timeout
    self.zmq_sock = None
    self.oda_conn = None

  def stream(self, params):
    """start the stream, and handle re-connection"""
    self.zmq_sock = zmq.Context().socket(zmq.PUB)
    print "ZMQ: opening %s" % (self.zmq_addr)
    self.zmq_sock.bind(self.zmq_addr)

    if self.name=='clocks':
       while True:
         dt=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
         msg = "%s:{\"time\":\"%s\"}" % (self.zmq_filter, dt)
         self.zmq_sock.send_string(msg)
         time.sleep(1.0)
    else:
      while True:
        #initially not connected to oanda
        connected = False
        ntries = 0
        while not connected:
          #try to connect to the oanda stream
          url = 'https://%s/v1/%s' % (self.streaming_domain, self.name)
          headers = {'Authorization': 'Bearer %s' % self.access_token} 
          print url
          res = requests.get(url, headers=headers, params=params, stream=True, timeout=self.timeout)
          if res.status_code==200:
            self.oda_conn=res
            connected = True
          else:
            #couldnt connect, wait and try again
            ntries += 1
            print "connection to oanda failed, %s, try %d" % (res.content, ntries)
            wait_time = min(60, ntries * 2)
            print "waiting %ds before reconnection" % (wait_time)
            time.sleep(wait_time)
        
        try:
          #now connected to oanda, stream events
          for line in self.oda_conn.iter_lines(1):
            if not line:continue
            #heartbeat, print to stdout but dont pass via zmq
            if line[0:12].find('heartbeat') != -1:continue
            #oanda disconnected us for some reason
            if line[0:20].find('disconnect') != -1:  raise ConnectionError(line)
            #join our filter string and data from oanda
            msg = "%s:%s" % (self.zmq_filter, line)
            #print "sending: %s" % (msg)
            self.zmq_sock.send_string(msg)
    

        except ConnectionError as e:
          print "caught exception: %s" % (e.message)


