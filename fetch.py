import aiohttp
async def fetch(site):
    async with aiohttp.ClientSession() as session, \
            session.get(site) as response:
        return await response.text()