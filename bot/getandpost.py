#//pues esto estaba dudando entre twython y tweepy. Asi que voy a intentar peony :-)
import asyncio
from tokens import *
# NOTE: the package name is peony and not peony-twitter
from peony import PeonyClient

loop = asyncio.get_event_loop()

# create the client using your api keys
client = PeonyClient(consumer_key=consumer_key,
                     consumer_secret=consumer_secret,
                     access_token=token,
                     access_token_secret=token_secret)

# this is a coroutine
req = client.api.statuses.update.post(status="I'm using Peony!!")

# run the coroutine
loop.run_until_complete(req)
