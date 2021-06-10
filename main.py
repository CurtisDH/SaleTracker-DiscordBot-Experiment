import os
import discord
import sys
import requests
import json

###################################
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
###################################

config_name = "data.txt"
prefix = "!"
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

configPath = os.path.join(application_path, config_name)
geckoDriver = os.path.join(application_path, "geckodriver.exe")

if not os.path.exists(configPath):
    with open(configPath, 'w') as f:
        f.write("NO CONTENT")
        print("NO CONTENT FOUND, GENERATED AUTOMATICALLY PATH:" + configPath)
        print("USE THE FOLLOWING ORDER IN THE DATA.txt DOCUMENT")
        print("DISCORD BOT TOKEN:")
        print("SERVER NAME:")
    f.close()


def Initialise(fileName):
    print("Starting...")
    with open(fileName) as f:
        data = str(f.read())
        f.close()
        token_char_array = []
        secondary_char_array = []
        bToggle = False
        for i in data:
            if (bToggle):
                if str(i) == "\n":
                    bToggle = not bToggle
                    continue
                secondary_char_array.append(i)
                continue
            if str(i) == "\n":
                bToggle = not bToggle
                continue
            token_char_array.append(i)

        # for d in token_char_array:
        #     print (d)
        # print ("Visual Display of separate char arrays")
        # for e in secondary_token_char_array:
        #     print(e)

    client = discord.Client()

    @client.event
    async def on_ready():
        print("OnReadyEvent")
        servernamestr = ''.join(secondary_char_array)
        for guild in client.guilds:
            if guild.name == servernamestr:
                break
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

    token_string = ''.join(token_char_array)

    # when a message is sent in the server
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        ProcessedResponse = str.lower(message.content.split(" ", 1)[0])

        if message.content.startswith(prefix):
            if ProcessedResponse == str.lower(prefix + "Test"):
                response = "Test Received"
                await message.channel.send("\n" + response)

            if ProcessedResponse == str.lower(prefix + "Whatis"):
                term = ""
                try:
                    term = message.content.split(" ", 1)[1]
                except:
                    print("Split failed (probably contains empty) or no results were found")
                    await message.channel.send("No results found for search term:'" + term + "'")
                response = "No results found for search term: '" + term + "'"
                print(term)
                url = 'https://api.urbandictionary.com/v0/define?term={}'
                r = requests.get(url.format(term))
                args = message.content
                print(args)
                testing = json.dumps(r.json())
                testing = json.loads(testing)
                for thing in testing['list']:
                    print(thing["definition"])
                    response = discord.Embed(title="Definition of " + term,
                                             description=thing["definition"],
                                             color=0x00ff00
                                             )
                    # response = thing["definition"]
                    break
                await message.channel.send(embed=response)

            if str.lower(message.content) == str.lower(prefix + "SteamSale"):
                await message.channel.send("Searching...")
                url = "https://www.whenisthenextsteamsale.com"
                options = Options()
                options.add_argument("--headless")
                browser = webdriver.Firefox(options=options,executable_path=geckoDriver)
                browser.get(url)

                soup = bs(browser.page_source,"html.parser")
                subtimer = soup.find_all("p",{"id":"subTimer"})
                maintimer = soup.find_all("p",{"id":"mainTimer"})
                for item in subtimer:
                    print(item.text)
                    subResponse = item.text
                for item in maintimer:
                    print(item.text)
                    mainResponse = item.text

                response = discord.Embed(title="Next Steam sale",
                                         description=mainResponse + " days " + subResponse + " hours",
                                         color=0x00ff00
                                         )
                print("sending response:" + mainResponse + " days " + subResponse + " hours")
                await message.channel.send(embed=response)

    client.run(token_string)


if __name__ == '__main__':
    Initialise(configPath)
