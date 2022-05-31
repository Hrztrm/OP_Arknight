# This example requires the 'message_content' intent.
#Create a file called config.py and add a variable token as for this to work. token variable is filled with the discord bot token.

from ast import excepthandler
from discord.ext import commands #Used to find the skins
import discord
import requests #Used for synchronous
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import config #File with the bot token innit
import aiofiles

client = commands.Bot(command_prefix='!')
intents = discord.Intents.default()
#client = discord.Client(intents=intents)


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
    f = open("Arknights_Data.txt", 'w')
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

async def skin_f(urls, message): #Is redundant, useful if only wants a single skin info, but going to put it at op_skin function. Can delete
    base_url = "https://gamepress.gg"
    infor = ""
    async with aiohttp.ClientSession() as session:
        data = await get_page(session, urls)
        soup = BeautifulSoup(data, "html.parser")
        
        #FInds the Name of skin
        s = soup.find('div', id= 'page-title')
        title = s.find('h1')
        print(title.text) #Send Discord msg
        infor = infor + "Skin Name: " + title.text

        #Find the operator name
        artist_div = soup.find('div', class_="skin-artist skin-info-box")
        model_design = artist_div.find_all('a')
        print("Model: " + model_design[0].text)
        infor = infor + "\nModel: " + model_design[0].text
        
        #Finds the series
        series_div = soup.find('div', class_="skin-series skin-info-box")
        try:
            series = series_div.find_all('a')
            print("Series: " + series[0].text)
            infor = infor + "\nSeries: " + series[0].text
        except:
            print("Series: None")
            infor = infor + "\nSeries: None"
            
        #Find the cost of skin
        cost = soup.find('span', class_="material-quantity")
        try:
            print("Originium Prime cost: " + cost.text[1:])
            infor = infor + "\nOriginium Prime cost: " + cost.text[1:]
        except:
            print("Originium Prime cost: Free\n")
            infor = infor + "\nOriginium Prime cost: Free" + "\n"

        #Find the image of skin
        img_div = soup.find('div', id= 'image-tab-1')
        img_w_tag = img_div.find('img')
        img_url = base_url + img_w_tag.attrs["src"]
        print(img_url)
        
        async with aiofiles.open('skin_search.jpg', 'wb') as f:
            resp = await session.request(method="GET", url=img_url)
            await f.write(await resp.read())
            #Do a send file here
            await message.channel.send(file=discord.File('skin_search.jpg'))
            await message.channel.send(infor) #Sends the whole information about the skin

async def skin_by_op(skin_list_url, filt, message):      
    base_url = "https://gamepress.gg"
    data = await fetch(skin_list_url)
    soup = BeautifulSoup(data, "html.parser")
    
    #Getting the whole skins list
    s = soup.find_all('div', class_ = 'views-field views-field-field-skin-image')
    print("Use the in brackets keyword for !skin command\n")
    await message.channel.send("Use the in brackets keyword for !skin command\n")
    
    for skin_entry in s:
        skin_op_name = skin_entry.find_all('a')
        op_name = skin_op_name[1].text
        infor = ""
        if filt in op_name.upper(): #Filter part
            event_url = skin_op_name[0].get('href')
            search_url = event_url.split('/')
            img_div = skin_op_name[2].find('img')
            img_url = base_url + img_div.attrs["src"]
            
            url = "https://gamepress.gg"
            end_url = url + event_url
            print(end_url)
            skin_page = await fetch(end_url)
            s = BeautifulSoup(skin_page, "html.parser")
            
            #Find the cost
            cost = s.find('span', class_="material-quantity")
            try:
                print("Originium Prime cost: " + cost.text[1:])
            except:
                print("Originium Prime cost: Free\n")
                
            #Finds the series
            series_div = s.find('div', class_="skin-series skin-info-box")
            try:
                series = series_div.find_all('a')
                print("Series: " + series[0].text)
            except:
                print("Series: None")
            
            #Skin img search function
            print(img_url)
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open('skin_search.jpg', 'wb') as f:
                    resp = await session.request(method="GET", url=img_url)
                    await f.write(await resp.read())
                    await message.channel.send(file=discord.File('skin_search.jpg'))
            
            print("message send succesfful")
            infor = infor + "Skin name: " + skin_op_name[0].text + " (" + search_url[-1] + ")\n"
            infor = infor + "Operator : " + skin_op_name[1].text + "\n"
            try:
                infor = infor + "Series: " + series[0].text + "\n"
            except:
                infor = infor + "Series: None"
            try:
                infor = infor + "Originium Prime cost: " + cost.text[1:] + "\n"
            except:
                infor = infor + "Originium Prime cost: Free" + "\n"
                
            await message.channel.send(infor)
            print("Skin name: " + skin_op_name[0].text + " (" + search_url[-1] + ")")
            print("Operator : " + skin_op_name[1].text + "\n")
            
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send(message.content)
    
    await client.process_commands(message)


@client.command()
async def skin(message, *,arg):
    if not arg.isdigit():
        url = "https://gamepress.gg/arknights/skin/"
    else:
        url = "https://gamepress.gg/arknights/node/"
    new_arg = arg.replace(" ", "-")
    end_url = url + new_arg
    print(end_url)
    try:
        await client.loop.create_task(skin_f(end_url, message))
    except:
        await message.channel.send("Skin not found")
    
@client.command()
async def OP(message):
    urls = [
        "https://gamepress.gg/arknights/other/cn-event-and-campaign-list",
        ]
    await client.loop.create_task(start(urls))
    print("It doing stuff")
    await message.channel.send(file=discord.File("Arknights_Data.txt"))
    print("Text is sent")

@client.command()
async def op_skin(message, *, arg):
    skin_list_url = "https://gamepress.gg/arknights/gallery/arknights-skin-art-gallery"
    arg = arg.upper()
    await client.loop.create_task(skin_by_op(skin_list_url, arg, message))

client.run(config.token)