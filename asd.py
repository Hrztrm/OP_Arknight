#Testing purposes

from re import A
import aiohttp
import asyncio
from bs4 import BeautifulSoup


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
    
def parse(results):
    list_url = []
    base_url = "https://gamepress.gg"
    for html in results:
        event_list_pg = BeautifulSoup(html, "html.parser")
        s = event_list_pg.find_all("tr")
        for line in s:
            if "Not Yet Global" in line.text:
                a = line.find("a")
                event_url = a.get('href')
                full_url = base_url + event_url
                list_url.append(full_url)
    list_url = list_url[:-2]
    return (list_url)

def parse2(data2):
    OP_tq_new = 0
    OP_tq_old = 0
    for num, html in enumerate(data2):
        dud = 0

        new_p = 0
        soup = BeautifulSoup(html, "html.parser")
        s = soup.find('div', id= 'page-title')
        for line in s: #Skip the Episode's stuff
            if "Episode" in line.text:
                dud = 1
            elif "Page" in line.text or "CN" in line.text:
                print("\n" + str(num + 1) + ". " + line.text)
        
        if dud == 1:
            continue
        
        try:
            #Gets the value of OP received from event
            event_div = soup.find_all('div', class_="event-total-summary")[0]
            new_player_content = event_div.find('td', class_="event-totals-text")
            #Check whether it is only for new players or not
            if "New Players" in new_player_content.text:
                new_p = 1
                print("New Players only")
            #Gets the value of OP
            Object_quantity_w_tag = event_div.find("a")
            Object_href = Object_quantity_w_tag.get('href')
            if "originite-prime" in Object_href:
                OP_quantity_w_tag = event_div.find('div', class_="item-qty")
                OP_quantity = int(OP_quantity_w_tag.text)
                print("Original Prime from this event: " + str(OP_quantity) + "\n")
                OP_tq_new = OP_tq_new + OP_quantity
                if new_p != 1:
                    OP_tq_old = OP_tq_old + OP_quantity
            else:
                print("Event does not contain OP\n")
        except:
            print("Event does not contain OP\n")
        
    print("\nTotal OP Obtained (New Player): " + str(OP_tq_new))
    print("Total OP Obtained (Old Player): " + str(OP_tq_old))
                
async def start(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        list_url = parse(data)
        data2 = await get_all(session, list_url)
        parse2(data2)

urls = [
    "https://gamepress.gg/arknights/other/cn-event-and-campaign-list",
]
#base_url = "https://gamepress.gg"
#source_url = "https://gamepress.gg/arknights/other/cn-event-and-campaign-list"

#results = asyncio.run(main(urls))
loop = asyncio.get_event_loop()
loop.run_until_complete(start(urls))

