import bs4 as BeautifulSoup
from datetime import datetime
import aiohttp
from fetch import *
async def upd_list():
    async with aiohttp.ClientSession() as session:
        urls = [
                "https://gamepress.gg/arknights/other/cn-event-and-campaign-list",
            ]
        data = await get_all(session, urls)
        list_url = parse(data)
        data2 = await get_all(session, list_url)
        parse2(data2)
        print("Updated list OP")
    op_list_url = "https://gamepress.gg/arknights/tools/interactive-operator-list#tags=null##stats"
    data = await fetch(op_list_url)
    f = open("op.txt", 'w')
    f.seek(0)
    
    soup = BeautifulSoup(data, "html.parser")
    
    #Getting the attributes value use var["tagname"]
    operator_list = soup.find_all("tr", class_="operators-row")
    
    for b,a in enumerate(operator_list):
        try:
            f.writelines("Operator: " + a["data-name"] + "\t" + "Rarity: " + a["data-rarity"] + "*\t" + "Class: " + a["data-profession"] + "\n")
        except:
            print("none")
    f.writelines("\n\nTotal Operators: " + str(b + 1))
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f.writelines("\n\nLast Updated: " + dt_string)
    f.close()
    print("Updated list operators")
    
def parse(results): #Finding the events
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

def parse2(data2): #Finding the contents of events
    f = open("Arknights_Data.txt", 'w')
    f.seek(0)
    now = datetime.now()
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
        
    f.writelines("\nTotal Originum Prime for New Players: " + str(OP_tq_new))
    f.writelines("\nTotal Originum Prime for Old Players: " + str(OP_tq_old))
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f.writelines("\n\nLast Updated: " + dt_string)
    f.close()