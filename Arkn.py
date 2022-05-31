# This example requires the 'message_content' intent.

import discord
#import requests #Used for synchronous
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import config #File with the bot token innit


intents = discord.Intents.default()

client = discord.Client(intents=intents)

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
    f = open("Arknights_Data2.txt", 'w')
    f.seek(0)
    f.writelines("Arknights OP Event Data\n")
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
                f.writelines("\n" + str(num + 1) + ". " + line.text)
        
        if dud == 1:
            continue
        
        try:
            #Gets the value of OP received from event
            event_div = soup.find_all('div', class_="event-total-summary")[0]
            new_player_content = event_div.find('td', class_="event-totals-text")
            #Check whether it is only for new players or not
            if "New Players" in new_player_content.text:
                new_p = 1
                f.writelines("\nNew Players only")
            #Gets the value of OP
            Object_quantity_w_tag = event_div.find("a")
            Object_href = Object_quantity_w_tag.get('href')
            if "originite-prime" in Object_href:
                OP_quantity_w_tag = event_div.find('div', class_="item-qty")
                OP_quantity = int(OP_quantity_w_tag.text)
                f.writelines("\nOriginal Prime from this event: " + str(OP_quantity) + "\n")
                OP_tq_new = OP_tq_new + OP_quantity
                if new_p != 1:
                    OP_tq_old = OP_tq_old + OP_quantity
            else:
                f.writelines("\nEvent does not contain OP\n")
        except:
            f.writelines("\nEvent does not contain OP\n")
        
    f.writelines("\nTotal OP Obtained (New Player): " + str(OP_tq_new))
    f.writelines("\nTotal OP Obtained (Old Player): " + str(OP_tq_old))
    f.close()
                
async def start(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        list_url = parse(data)
        data2 = await get_all(session, list_url)
        parse2(data2)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

    #if message.content.startswith('$OP'): # Synchornous stuff, probably should not use. But it works
    #    f = open("Arknights_Data.txt", 'w')
    #    f.seek(0)
    #    f.writelines("Arknights OP Event Data\n")
    #    base_url = "https://gamepress.gg"
    #    source_url = "https://gamepress.gg/arknights/other/cn-event-and-campaign-list"
    #    list_url = []
    #    OP_tq_new = 0
    #    OP_tq_old = 0
    #    #
    #    r = requests.get(source_url)
    #    event_list_pg = BeautifulSoup(r.text, "html.parser")
    #    s = event_list_pg.find_all("tr")
    #    for line in s:
    #        if "Not Yet Global" in line.text:
    #            a = line.find("a")
    #            event_url = a.get('href')
    #            full_url = base_url + event_url
    #            list_url.append(full_url)
    #    list_url = list_url[:-2]
    #    for num, a in enumerate(list_url):
    #        r = requests.get(a)
    #        soup = BeautifulSoup(r.text, "html.parser")
    #        new_p = 0
    #        OP_quantity = 0
    #        epi = 0
    #        s = soup.find('div', id= 'page-title')
    #        for line in s:
    #            if "Episode" in line.text:
    #                epi = 1
    #            elif "Page" in line.text or "CN" in line.text:
    #                f.writelines("\n" + str(num + 1) + ". " + line.text)
    #        #Ignore episodes
    #        if epi == 1:
    #            continue
    #        try:
    #            #Gets the value of OP received from event
    #            event_div = soup.find_all('div', class_="event-total-summary")[0]
    #            new_player_content = event_div.find('td', class_="event-totals-text")
    #            #Check whether it is only for new players or not
    #            if "New Players" in new_player_content.text:
    #                new_p = 1
    #                #await message.channel.send("\nNew Players only")
    #                f.writelines("\nNew Players only")
#
    #            #Gets the value of OP
    #            Object_quantity_w_tag = event_div.find("a")
    #            Object_href = Object_quantity_w_tag.get('href')
    #            if "originite-prime" in Object_href:
    #                OP_quantity_w_tag = event_div.find('div', class_="item-qty")
    #                OP_quantity = int(OP_quantity_w_tag.text)
    #                f.writelines("\nOriginal Prime from this event: " + str(OP_quantity) + "\n")
    #                OP_tq_new = OP_tq_new + OP_quantity
    #                if new_p != 1:
    #                    OP_tq_old = OP_tq_old + OP_quantity
    #            else:
    #                #await message.channel.send("\nEvent does not contain OP\n")
    #                f.writelines("\nEvent does not contain OP\n")
    #        except:
    #            f.writelines("\nEvent does not contain OP\n")
    #            #await message.channel.send("\nEvent does not contain OP\n")
    #    #await message.channel.send("\nTotal OP Obtained (New Player): " + str(OP_tq_new))
    #    #await message.channel.send("\nTotal OP Obtained (Old Player): " + str(OP_tq_old))
    #    f.writelines("\nTotal OP Obtained (New Player): " + str(OP_tq_new))
    #    f.writelines("\nTotal OP Obtained (Old Player): " + str(OP_tq_old))
    #    f.close()
    #    await message.channel.send(file=discord.File("Arknights_Data.txt"))
    
    if message.content.startswith('$OP'): #Asynchornous version of getting the Originium Prime. Means can do other stuff while doing this function
        urls = [
        "https://gamepress.gg/arknights/other/cn-event-and-campaign-list",
        ]
        await client.loop.create_task(start(urls))
        print("It doing stuff")
        await message.channel.send(file=discord.File("Arknights_Data.txt"))
        print("Text is sent")
        
client.run(config.token)