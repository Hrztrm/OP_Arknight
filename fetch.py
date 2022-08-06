import aiohttp
import asyncio
async def fetch(site):
    async with aiohttp.ClientSession() as session, \
            session.get(site) as response:
        return await response.text()
    
async def get_page(session, url): #Gets the content of the page
    async with session.get(url) as r:
        return await r.text()
    
async def get_all(session, urls): #Put the contents of the page into a list
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results