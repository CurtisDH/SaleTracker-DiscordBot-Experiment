import os
import time
import timeit

import discord
import sys
import requests
import json

###################################
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
###################################

import asyncio

############Threading##############
import logging
import threading
import time

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
    #client.activity = discord.Activity(type=discord.ActivityType.watching,name="SteamSale is " + "test" + " Days away")
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

    @client.event
    async def on_raw_reaction_add(payload):
        print("OnReactionAddEvent")
        if payload.user_id == client.user:
            return
        print(payload.emoji)
        print(payload.message_id)
        if str(payload.message_id) == '852561831910178836':
            await client.get_channel(payload.channel_id).send(f"Thanks for reacting <@{payload.user_id}>")
        if str(payload.emoji) == "👍":
            await client.get_channel(payload.channel_id).send("test")

    # when a message is sent in the server
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        ProcessedResponse = str.lower(message.content.split(" ", 1)[0])
        if message.content.startswith(prefix):
            if ProcessedResponse == str.lower(prefix + "Test"):
                response = "Test Received"
                print(response)
                # x = threading.Thread(target=replyTimer,args=(3,message.channel))
                # x.start()
                # print("starting thread")
                asyncio.get_event_loop().create_task(DelayedReply(3, message.channel))
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
                browser = webdriver.Firefox(options=options, executable_path=geckoDriver)
                browser.get(url)
                soup = bs(browser.page_source, "html.parser")
                subtimer = soup.find_all("p", {"id": "subTimer"})
                maintimer = soup.find_all("p", {"id": "mainTimer"})
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


            #STILL WIP -- NEED TO IMPLEMENT USER PINGING
            if str.lower(message.content) == str.lower(prefix + "NotifyMe"):
                await message.channel.send("SettingTimer...")
                url = "https://www.whenisthenextsteamsale.com"
                options = Options()
                options.add_argument("--headless")
                browser = webdriver.Firefox(options=options, executable_path=geckoDriver)
                browser.get(url)

                soup = bs(browser.page_source, "html.parser")
                subtimer = soup.find_all("p", {"id": "subTimer"})
                maintimer = soup.find_all("p", {"id": "mainTimer"})
                for item in subtimer:
                    print(item.text)
                    subResponse = item.text
                for item in maintimer:
                    print(item.text)
                    mainResponse = item.text

                TimeInHours = float(0)
                # doing this by hand cause its getting late and im getting lazy
                print(subResponse.split(":"))  # [0] [1] [2] should always have a value in them.
                splitResponse = subResponse.split(":")
                TimeInHours += ((float(splitResponse[0])))
                TimeInHours += float(splitResponse[1]) / 60
                TimeInHours += ((float(splitResponse[2]) / 60) / 60)

                days = float(mainResponse.split("days")[0])
                if (days is not 0):
                    TimeInHours += days*24
                print(TimeInHours)
                TimeInSeconds = (TimeInHours * 60) * 60
                print (TimeInSeconds)
                await client.change_presence(status=discord.Status.idle, activity=discord.Game(name="SteamSale in " + str(int(TimeInHours / 24)) + " Days"))
                asyncio.get_event_loop().create_task(DelayedReply(TimeInSeconds,message.channel))
    client.run(token_string)


async def DelayedReply(timer, channeltoMessage):
    await(channeltoMessage.send("Setting timer successfully set for: "+str(int((timer/60)/60))+" hours"))
    await asyncio.sleep(timer)
    # print(client.get_channel(852493411268165682))
    # await client.get_channel(852493411268165682).send("Test")
    await channeltoMessage.send("Test")


if __name__ == '__main__':
    Initialise(configPath)
