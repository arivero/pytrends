#//pues esto estaba dudando entre twython y tweepy. Asi que voy a intentar peony :-)
import asyncio
import aiodns
import aiohttp
import sqlite3
from peewee import *
import datetime
from tokens import *
# NOTE: the package name is peony and not peony-twitter
from peony import PeonyClient

db = SqliteDatabase('tendencias.db')
loop = asyncio.get_event_loop()

class Trend(Model):
  class Meta:
    database = db
  busqueda=TextField()
  zc=IntegerField()
  found=DateTimeField(default=datetime.datetime.now)
  hl=CharField(null=True)
  gl=CharField(null=True)
  raw=TextField()


db.connect()
#Trend.drop_table()
#db.create_tables([Trend])

client = PeonyClient(consumer_key=consumer_key,
                     consumer_secret=consumer_secret,
                     access_token=token,
                     access_token_secret=token_secret)

async def tell(trend,score):
  mensaje="Se esta buscando '"+trend+"', con una score zc="+str(score)
  print(mensaje)
  return client.api.statuses.update.post(status=mensaje)

#asynchronous generator
async def sample():
  async with aiohttp.TCPConnector(force_close=True,limit_per_host=1,use_dns_cache=False) as c: #podriamos dar otro resolver
    async with aiohttp.ClientSession(connector=c) as session:
      for lang in ['','&hl=en','&hl=es']:
        async with session.get('https://www.google.com/complete/search?client=qsb-android-asbl&q=&gl=ES'+lang) as response:
          json = await response.json()
          yield json
          print(json)

#native coroutine (main one)
async def main():
    async for j in sample():
      a=[]
      for e in j[1]:
          name=e[0][3:-4]
          zc=e[3]['zc']
          raw=str(e)
          dbTrend, created =Trend.get_or_create(busqueda=name, defaults= {'zc':zc, 'raw':raw})
          if created:
            #esto es lo raro de los async... aqui el primero solo nos da un request pending
            res = await tell(name,zc)
            #... y tenemos que ejecutar una espera del segundo para estar seguro de que se ejecuta
            a.append(res)
          else:
            if dbTrend.zc != zc:
              print(dbTrend.busqueda," ya estaba en la BD, con zc=", dbTrend.zc)
      if len(a) > 0:
          await asyncio.gather(*a)


loop.run_until_complete(main())
