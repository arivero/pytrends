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

langcodes="af, ach, ak, am, ar, az, ban, be, bem, bg, bh, bn, br, bs,ca, ceb, chr, ckb,\
co, crs, cs, cy, da, de, ee, el, en, eo, es, es-419, et, eu, fa,fi,\
fo, fr, fy, ga, gaa, gd, gl, gn, gu, ha, haw, hi, hr, ht, hu, hy,ia,\
id, ig, is, it, iw, ja, jw, ka, kg, kk, km, kn, ko,kri,ku,ky,la,\
lg, ln, lo, loz, lt, lua, lv,mfe,mg,mi,mk,ml,mn,mo,mr,ms,mt,my,\
ne, nl, nn, no, nso, ny, nyn,oc, om, or, pa, pcm, pl, ps,pt-BR,\
pt-PT, qu, rm, rn, ro, ru, rw,sd, sh, si, sk, sl, sn, sm, so, sq, sr,\
sr-Latn, sr-ME, st, su, sv, sw,ta, te, tg, th, ti, tk, tl, tlh, tn, to, tr, tt,\
tum, tw, ug, uk, ur, uz, vi, wo,xh, xx-bork, xx-elmer, xx-hacker,\
xx-klingon,xx-pirate,yi,yo,zh-CN,zh-TW,zu".split(",")

countrycodes="AD,AE,AF,AG,AI,AL,AM,AO,AQ,AR,AS,AT,AU,AW,AZ,BA,BB,BD,BE,BF,BG,\
BH,BI,BJ,BM,BN,BO,BQ,BR,BS,BT,BV,BW,BY,BZ,CA,CC,CD,CF,CG,CH,CI,CK,CL,CM,CN,CO,CR,CV,CW,CX,\
CY,CZ,DE,DJ,DK,DM,DO,DZ,EC,EE,EG,EH,ER,ES,ET,FI,FJ,FK,FM,FO,FR,GA,GB,GD,GE,GF,GG,GH,GI,GL,\
GM,GN,GP,GQ,GR,GS,GT,GU,GW,GY,HK,HM,HN,HR,HT,HU,ID,IE,IL,IN,IO,IQ,IS,IT,JE,JM,JO,JP,KE,KG,KH,\
KI,KM,KN,KR,KW,KY,KZ,LA,LB,LC,LI,LK,LR,LS,LT,LU,LV,LY,MA,MC,MD,ME,MG,MH,MK,ML,MM,MN,MO,MP,MQ,\
MR,MS,MT,MU,MV,MW,MX,MY,MZ,NA,NC,NE,NF,NG,NI,NL,NO,NP,NR,NU,NZ,OM,PA,PE,PF,PG,PH,PK,PL,PM,PN,\
PR,PS,PT,PW,PY,QA,RE,RO,RS,RU,RW,SA,SB,SC,SE,SG,SH,SI,SJ,SK,SL,SM,SN,SO,SR,ST,SV,SX,SZ,\
TC,TD,TF,TG,TH,TJ,TK,TL,TM,TN,TO,TR,TT,TV,TW,TZ,UA,UG,UM,US,UY,UZ,VA,VC,VE,VG,VI,VN,VU,\
WF,WS,XK,YE,YT,ZA,ZM,ZW".split(",")


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
      for lang in ['','en','es','cat','eu','ca','gl']:
        l= '&hl='+lang if len(lang)>0 else ''
        async with session.get('https://www.google.com/complete/search?client=qsb-android-asbl&q=&gl=ES'+l) as response:
          json = await response.json()
          yield json,l
          print(json)

#native coroutine (main one)
async def main():
    async for j,hl in sample():
      a=[]
      for e in j[1]:
          name=e[0][3:-4]
          zc=e[3]['zc']
          raw=str(e)
          dbTrend, created =Trend.get_or_create(busqueda=name, defaults= {'hl':hl,'gl':'ES','zc':zc, 'raw':raw})
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
