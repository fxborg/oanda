import zmq
import requests
from requests.exceptions import ConnectionError
import sys
import time
from datetime import datetime
from pprint import pprint
from oandastream import OandaStream,ZMQ_OPTION
from settings import ACCOUNT_ID,ACCESS_TOKEN,STREAM_DOMAIN
if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: %s [events|prices|client]" % (sys.argv[0])
    sys.exit(1)

  mode = sys.argv[1]

  if mode == 'events':
    #stream account events
    oda = OandaStream(mode, STREAM_DOMAIN, ACCESS_TOKEN , 20)
    params = {'accountIds' : ACCOUNT_ID}

  elif mode == 'prices':
    #stream tick data for the below instruments
    #instruments = ['EUR_USD', 'AUD_USD']
    instruments = ['USD_JPY']
    oda = OandaStream(mode, STREAM_DOMAIN, ACCESS_TOKEN,  10)
    params = {'accountId' : ACCOUNT_ID,
                                'instruments' : ','.join(instruments) }


  elif mode == 'clocks':
    oda = OandaStream(mode, STREAM_DOMAIN, ACCESS_TOKEN,  10)
    params = {}

  else:
    print "usage: %s [events|prices|clocks]" % (sys.argv[0])
    sys.exit(1)


  try:
    oda.stream(params)

  except KeyboardInterrupt:
    print " Done..."
  except Exception as e:
    print e.message
  finally:
    if oda.zmq_sock: oda.zmq_sock.close() 


