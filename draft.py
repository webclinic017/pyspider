import asyncio
from tqdm.asyncio import tqdm


async def funcname():
    with tqdm(range(1000)) as pbar:
        async for i in pbar:
            i=i+1


asyncio.run(funcname())
