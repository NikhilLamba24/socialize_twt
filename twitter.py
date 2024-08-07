import asyncio
import nest_asyncio
from twikit import Client
client = Client('en-US')
client.load_cookies('cookies.json')

async def tweeteeer(text):
    print("inside")
    await client.create_tweet(text=text)
    print("outside")
    #return 