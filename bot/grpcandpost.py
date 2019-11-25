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

class Trend(Model):
  class Meta:
    database = db
  busqueda=TextField(unique=True,primary_key=True)
  zc=IntegerField()
  found=DateTimeField(default=datetime.datetime.now)

class History(Model):
  class Meta:
    database = db
  found=DateTimeField(default=datetime.datetime.now)
  busqueda=TextField()
  hl=CharField(null=True)
  gl=CharField(null=True)
  zc=IntegerField()
  raw=TextField()


db.connect()
#History.create_table()
#Trend.drop_table()
#db.create_tables([Trend])

client = PeonyClient(consumer_key=consumer_key,
                     consumer_secret=consumer_secret,
                     access_token=token,
                     access_token_secret=token_secret)

async def tell(trend,score):
  mensaje="Se esta buscando '"+trend+"', con una score zc="+str(score)
  print(mensaje)
  mensaje+="\n https://trends.google.com/trends/explore?q="+ urllib.parse.quote_plus(trend)+ "&date=now%201-d&geo=ES#RELATED_QUERIES_0"

  return client.api.statuses.update.post(status=mensaje)


import requests
from hyper.contrib import HTTP20Adapter
s = requests.Session()
s.mount('https://', HTTP20Adapter())
headers2= {'content-type': 'application/grpc', 'te': 'trailers', 'x-geo': 'w CAIQNiICZXM=', 'accept-language': 'es-ES', 'x-android-cert': '24BB24C05E47E0AEFA68A58A766179D9B613A600', 'x-android-package': 'com.google.android.apps.searchlite', 'x-goog-api-key': 'AIzaSyA4eMzY-Y4QANwGwi_y1lQKyYOPIYOK528', 'pragma': 'no-cache', 'cache-control': 'no-cache'}
data= b'\x00\x00\x00\x00\n\n\x02ES\x12\x02es\x18\x14'
req=requests.Request('POST','https://searchlite-pa.googleapis.com/google.internal.search.searchlite.v0.SearchliteService/GetTrendingSearchQueries',headers=headers2,data=data)
prep=s.prepare_request(req)
del prep.headers['User-Agent']
del prep.headers['Connection']
del prep.headers['Accept']
del prep.headers['Accept-Encoding']
'''Content-Length': '15'}'''
resp=s.send(prep)
print(resp)
print(resp.content)
import ejemplo_pb2
v=ejemplo_pb2.Vista()
v.ParseFromString(resp.content[5:])
print(v.c[0].tendencia[0].ok)
for t in v.c[0].tendencia:
    print (datetime.datetime.now(),t.score,t.name)
print("================================")
#native coroutine (main one)
async def main():
    #Trend.delete().where(Trend.found < datetime.datetime.now()-datetime.timedelta(days=1) 
    #      ).execute()
      for e in j[1]:
          name=e[0][3:-4]
          zc=e[3]['zc']
          raw=str(e)
          dbTrend, created =Trend.get_or_create(busqueda=name, defaults= {'zc':zc})
          if created:
            res = await tell(name,zc)
            a.append(res)
            History.create(busqueda=name,hl=hl,gl='ES',zc=zc, raw=raw)
          else:
            if dbTrend.zc != zc:
              dbTrend.zc=zc
              dbTrend.save()
              History.create(busqueda=name,hl=hl,gl='ES',zc=zc, raw=raw)
