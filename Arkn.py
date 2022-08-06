# This example requires the 'message_content' intent.
#Create a file called config.py and add a variable token as for this to work. token variable is filled with the discord bot token.

from discord.ext import commands #Used to find the skins
import discord
import requests #Used for synchronous
from bs4 import BeautifulSoup
import aiohttp
import asyncio
#import config #File with the bot token innit
import os
import aiofiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from op_skin_file import *
import random
from updat import *
client = commands.Bot(command_prefix='!')
intents = discord.Intents.default()
#client = discord.Client(intents=intents)

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

async def operators(message, prof):
    with open('op.txt', 'r') as f:
        lines = f.readlines()
        num_op = len(lines) - 4
        op_list = []
        if prof == "All":
            num = random.randint(0, num_op)
            oper = lines[num].split("\t")
        else:
            for line in lines:
                if prof in line:
                    op_list.append(line)
            num = random.randint(0, len(op_list))
            oper = op_list[num].split("\t")
        await message.channel.send(oper[0] + "\n" + oper[1] + "\n" + oper[2])
    
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

#@client.event #This is for message events
#async def on_message(message):
#
#    if message.author == client.user:
#        return
#
#    if message.content.startswith('hello'):
#        await message.channel.send(message.content)
#    
#    await client.process_commands(message)


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
    await message.channel.send(file=discord.File("Arknights_Data.txt"))

@client.command()
async def op_skin(message, *, arg):
    skin_list_url = "https://gamepress.gg/arknights/gallery/arknights-skin-art-gallery"
    arg = arg.upper()
    await client.loop.create_task(skin_op(skin_list_url, arg, message))

@client.command()
async def all_random_op(message):
    await client.loop.create_task(operators(message, "All"))

@client.command()
async def random_op(message, *, arg):
    prof = arg.capitalize()
    prof_list = ["Medic", "Vanguard", "Sniper", "Caster", "Guard", "Supporter", "Specialist", "Defender"]
    if prof in prof_list:
        await client.loop.create_task(operators(message, prof))
    else:
        await message.channel.send("Class does not exist")

token = os.environ['token']
client.run(token)

sched = AsyncIOScheduler()

# Schedule job_function to be called every two seconds
sched.add_job(upd_list, 'interval', minutes=1)
sched.start()

#client.run(config.token)
