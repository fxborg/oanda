# -*- coding: utf-8 -*-
from math import floor
import time
from datetime import datetime
from pprint import pprint 
class Candle():
  """ candle class """
  def __init__(self,p,t,v):
    self.o=p
    self.h=p
    self.l=p
    self.c=p
    self.t=t
    self.v=v
  
  def update(self,p):
    """ update candle """ 
    if not p: return
    self.c=p 
    if self.o is None: self.o=p
    if self.h is None or self.h < p: self.h=p
    if self.l is None or self.l > p: self.l=p
    self.v += 1

class Candles():
  """ Candles class """
  def __init__(self,tf):
    self.candles=[]
    self.bars = 0
    self.tf=tf
    self.last_time=0
    self.last_price=None

  def update(self,tick):
    """ update ticks """
    if not tick.has_key('time'):return
    t = self.normalize_time(tick['time'])
    p = None
    v = 0
    if tick.has_key('ask') and tick.has_key('bid'): 
      p = (tick['ask']+tick['bid']) * 0.5
      self.last_price = p
      v = 1

    if t > self.last_time :
      if len(self.candles) > 0:
         if not self.candles[-1].o : 
           self.candles[-1].update(self.last_price)
           self.candles[-1].v = 0

         cd=self.candles[-1]
         if cd.o :
           print "\n%s\t| %.3f\t| %.3f\t| %.3f\t| %.3f\t | %s" % (datetime.fromtimestamp(cd.t),cd.o,cd.h,cd.l,cd.c,cd.v)
          
      self.candles.append(Candle(p,t,v))
      self.last_time=t  
      
    else:
      self.candles[-1].update(p)

  def normalize_time(self, t):
    """ normalized time for timeframe"""
    dt = datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ') 
    a = int(time.mktime(dt.timetuple()))
    return floor(a / self.tf) * self.tf	
