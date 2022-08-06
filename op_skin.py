from discord.ext import commands #Used to find the skins
import discord
from bs4 import BeautifulSoup
import aiohttp
import aiofiles
import fetch

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