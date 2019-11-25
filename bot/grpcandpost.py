#//pues esto estaba dudando entre twython y tweepy. Asi que voy a intentar peony :-)
import asyncio
import aiodns
import aiohttp
import sqlite3
import urllib.parse
from peewee import *
import datetime
from random import sample
from tokens import *
# NOTE: the package name is peony and not peony-twitter
from peony import PeonyClient

db = SqliteDatabase('tendencias.db')
loop = asyncio.get_event_loop()

class HistoryDailyTrends(Model):
  class Meta:
    database = db
  found=DateTimeField(default=datetime.datetime.now,index=True)
  busqueda=TextField()
  hl=CharField(null=True)
  gl=CharField(null=True)
  n=IntegerField()


db.connect()
#HistoryDailyTrends.create_table()
#History.create_table()
#Trend.drop_table()
#db.create_tables([Trend])

client = PeonyClient(consumer_key=consumer_key,
                     consumer_secret=consumer_secret,
                     access_token=token,
                     access_token_secret=token_secret)

async def tell(trend,score):
  mensaje="La consulta '"+trend+"', ha sobrepasado las "+str(score)+" busquedas"
  print(mensaje)
  mensaje+="\n https://trends.google.com/trends/explore?q="+ urllib.parse.quote_plus(trend)+ "&date=now%201-d&geo=ES"
  return client.api.statuses.update.post(status=mensaje)

import requests
from hyper.contrib import HTTP20Adapter
import ejemplo_pb2
def tendencias():
  s = requests.Session()
  s.mount('https://', HTTP20Adapter())
  headers2= {'content-type': 'application/grpc',
          'te': 'trailers', 
          'x-geo': 'w CAIQNiICZXM=',
          'accept-language': 'es-ES', 
          'x-android-cert': '24BB24C05E47E0AEFA68A58A766179D9B613A600', 
          'x-android-package': 'com.google.android.apps.searchlite', 
          'x-goog-api-key': 'AIzaSyA4eMzY-Y4QANwGwi_y1lQKyYOPIYOK528', 
          'pragma': 'no-cache', 'cache-control': 'no-cache'}
  data= b'\x00\x00\x00\x00\n\n\x02ES\x12\x02es\x18\x14'
  req=requests.Request('POST',
          'https://searchlite-pa.googleapis.com/google.internal.search.searchlite.v0.SearchliteService/GetTrendingSearchQueries',
          headers=headers2,data=data)
  prep=s.prepare_request(req)
  del prep.headers['User-Agent']
  del prep.headers['Connection']
  del prep.headers['Accept']
  del prep.headers['Accept-Encoding']
  '''Content-Length': '15'}'''
  resp=s.send(prep)
  v=ejemplo_pb2.Vista()
  v.ParseFromString(resp.content[5:])
  for t in v.c[0].tendencia:
    yield (datetime.datetime.now(),t.score,t.name)

hdt=HistoryDailyTrends
async def main():
      for (date, score, name) in tendencias():
          try:
              created=False
              dbTrend=HistoryDailyTrends.get(hdt.busqueda==name,hdt.n==score, hdt.found > ( datetime.datetime.now() - datetime.timedelta(days=1)) )
          except DoesNotExist:
              created=True
              dbTrend=HistoryDailyTrends.create(busqueda=name,n=score)
          if created and score > 19999:
            res = await tell(name,score)
            await res  #no queremos paralelizar

loop.run_until_complete(main())
