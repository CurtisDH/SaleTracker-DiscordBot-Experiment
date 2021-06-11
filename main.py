import os
import time
import timeit

import discord
import sys
import requests
import json

import platform

###################################
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
###################################

import asyncio

config_name = "data.txt"
pingList_name = "pingList.txt"
prefix = "!"
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

configPath = os.path.join(application_path, config_name)
pingListPath = os.path.join(application_path, pingList_name)
geckoDriver = os.path.join(application_path, "geckodriver.exe")  # Windows
if str(platform.system()) == "Linux":
    geckoDriver = os.path.join(application_path,
                               "geckodriver")  # Linux says it was checking path for geckodriver -- added here regardless

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
    global MessageID
    with open(fileName) as f:
        data = str(f.read())
        f.close()
        token_char_array = []
        MessageID_char_array = []
        bToggle = False
        for i in data:
            if (bToggle):
                if str(i) == "\n":
                    bToggle = not bToggle
                    continue
                MessageID_char_array.append(i)
                MessageID = "".join(MessageID_char_array)
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

    # client.activity = discord.Activity(type=discord.ActivityType.watching,name="SteamSale is " + "test" + " Days away")
    @client.event
    async def on_ready():
        print("OnReadyEvent")
        servernamestr = ''.join(MessageID_char_array)
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
        # TODO load messageID from the txt file

        ### MessageID Retrieval ###
        with open(configPath) as retrieval:
            mID = retrieval.read()
            mID = mID.split("\n")
            MessageID = mID[1]
        ###########################

        if str(payload.message_id) == str(MessageID):
            if os.path.exists(pingListPath):
                with open(pingListPath, 'a') as f:
                    with open(pingListPath) as filecontents:
                        Content = str(filecontents.read())
                        Content = Content.split(" ")
                        global IdExists
                        for userid in Content:
                            if str(userid) == str(payload.user_id):
                                IdExists = False
                                break
                            if not IdExists:
                                f.write("\n" + str(payload.user_id))
                IdExists = True
                f.close()
            print(str(payload.member))
            await payload.member.send(f"You will be pinged when the Sale begins! <@{payload.user_id}>")
            if not os.path.exists(pingListPath):
                with open(pingListPath, 'w') as f:
                    f.write(str(payload.user_id))
                f.close()
            with open(pingListPath) as g:
                content = str(g.read())
                g.close()
                content = content.split("\n")
                print(content)
        # if str(payload.emoji) == "👍":
        #     await client.get_channel(payload.channel_id).send("test")

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

            if ProcessedResponse == str.lower(prefix + "SteamSale"):
                print("Searching...")
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
                browser.close()
                response = discord.Embed(title="Next Steam sale",
                                         description=mainResponse + " days " + subResponse + " hours",
                                         color=0x00ff00
                                         )
                print("sending response:" + mainResponse + " days " + subResponse + " hours")

                await message.channel.send(embed=response)
            if ProcessedResponse == str.lower(prefix + "prune"):
                number = " "
                try:
                    number = message.content.split(" ", 1)[1]
                except:
                    print("Invalid number provided")
                    await message.channel.send(ProcessedResponse + ":Invalid Number Provided")
                msgs = []
                number = int(number)
                async for x in message.channel.history(limit=number):
                    msgs.append(x)
                # print(number)
                # for m in msgs:
                #     print(m.id)
                await message.channel.purge(limit=number)

            # STILL WIP -- NEED TO IMPLEMENT USER PINGING
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
                browser.close()
                TimeInHours = float(0)
                # doing this by hand cause its getting late and im getting lazy
                print(subResponse.split(":"))  # [0] [1] [2] should always have a value in them.
                splitResponse = subResponse.split(":")
                TimeInHours += ((float(splitResponse[0])))
                TimeInHours += float(splitResponse[1]) / 60
                TimeInHours += ((float(splitResponse[2]) / 60) / 60)

                days = float(mainResponse.split("days")[0])
                if (days is not 0):
                    TimeInHours += days * 24
                print(TimeInHours)
                TimeInSeconds = (TimeInHours * 60) * 60
                print(TimeInSeconds)
                await client.change_presence(status=discord.Status.idle, activity=discord.Game(
                    name="SteamSale in " + str(int(TimeInHours / 24)) + " Days"))
                asyncio.get_event_loop().create_task(DelayedReply(TimeInSeconds, message.channel))

    client.run(token_string)


async def DelayedReply(timer, channeltoMessage):
    await(channeltoMessage.send("Setting timer successfully set for: " + str(int((timer / 60) / 60)) + " hours"))
    await channeltoMessage.send(content="If you'd like to get notified when the sale begins, react to this message")
    async for msg in channeltoMessage.history(limit=1):
        print("New Message ID:" + str(msg.id) + "Sent by:" + str(msg.author))
    with open(configPath, 'r') as file:
        data = file.read()
        file.close()
        with open(configPath, 'w') as writeOver:
            response = data.split("\n", 1)[0] + "\n" + str(msg.id)
            writeOver.write(response)
            writeOver.close()

    await asyncio.sleep(timer)
    # print(client.get_channel(852493411268165682))
    # await client.get_channel(852493411268165682).send("Test")

    # TODO read the data from the PingList and ping all the userID's contained.
    await channeltoMessage.send("The Sale has begun!")


if __name__ == '__main__':
    Initialise(configPath)
