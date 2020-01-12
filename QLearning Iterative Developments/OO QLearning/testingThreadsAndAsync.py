import time
import asyncio

async def doSomeWork(x):
    print("Wait " + str(x))
    await time.sleep(x)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(doSomeWork(x))
