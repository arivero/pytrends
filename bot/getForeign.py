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

langcodes="af,ach,ak,am,ar,az,ban,be,bem,bg,bh,bn,br,bs,ca,ceb,chr,ckb,\
co,crs,cs,cy,da,de,ee,el,en,eo,es,es-419,et,eu,fa,fi,\
fo,fr,fy,ga,gaa,gd,gl,gn,gu,ha,haw,hi,hr,ht,hu,hy,ia,\
id,ig,is,it,iw,ja,jw,ka,kg,kk,km,kn,ko,kri,ku,ky,la,\
lg,ln,lo,loz,lt,lua,lv,mfe,mg,mi,mk,ml,mn,mo,mr,ms,mt,my,\
ne,nl,nn,no,nso,ny,nyn,oc,om,or,pa,pcm,pl,ps,pt-BR,\
pt-PT,qu,rm,rn,ro,ru,rw,sd,sh,si,sk,sl,sn,sm,so,sq,sr,\
sr-Latn,sr-ME,st,su,sv,sw,ta,te,tg,th,ti,tk,tl,tlh,tn,to,tr,tt,\
tum,tw,ug,uk,ur,uz,vi,wo,xh,xx-bork,xx-elmer,xx-hacker,\
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

async def fetch(cnl):
  #si ponemos el conector en el main se cierra :-( 
  async with aiohttp.TCPConnector(force_close=True,limit_per_host=1) as c:
    async with aiohttp.ClientSession(connector=c) as s:
      async with s.get('https://www.google.com/complete/search?client=qsb-android-asbl&q=&gl='+cnl) as response:
        print(cnl)
        return await response.json()


async def sampleLanguages():
      n=0
      for lang in ['','en','es']+sample(langcodes,4):
        l= '&hl='+lang if len(lang)>0 else ''
        for cn in ['UK','US']+sample(countrycodes,12):
            #task=asyncio.ensure_future(fetch(cn+l)) #es lo mismo que create_task en 3.8
            task=fetch(cn+l)
            yield task,lang,cn,n
            n+=1

import time
async def save(jpromise,h,g):
    j=await jpromise
    for e in j[1]:
         name=e[0][3:-4]
         zc=e[3]['zc']
         raw=str(e)
         History.create(busqueda=name,hl=h,gl=g,zc=zc, raw=raw)

async def main():
    tasks=[]
    async for jp,hl,gl,n in sampleLanguages():
          task=asyncio.ensure_future(save(jp,hl,gl))
          tasks.append(task)
          await asyncio.sleep(0.00001)
    await asyncio.wait(tasks,return_when=asyncio.ALL_COMPLETED)
    #await asyncio.gather(*tasks)
    #await asyncio.sleep(5)

loop.run_until_complete(main())
