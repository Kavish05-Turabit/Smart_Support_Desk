import redis.asyncio as aior
import asyncio

redis = aior.from_url(
    "redis://localhost:32769",
    decode_responses = True
)
async def gett():
    h = await redis.get(1)
    return h

print(asyncio.run(gett()))