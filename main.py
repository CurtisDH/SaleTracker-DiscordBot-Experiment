import os

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
from datetime import datetime

import asyncio

config_name = "data.txt"
pingList_name = "pingList.txt"
hoursRemaining_name = "hoursRemaining.txt"
prefix = "!"
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

configPath = os.path.join(application_path, config_name)
pingListPath = os.path.join(application_path, pingList_name)
geckoDriver = os.path.join(application_path, "geckodriver.exe")  # Windows
hoursRemainingPath = os.path.join(application_path, hoursRemaining_name)
if str(platform.system()) == "Linux":
    geckoDriver = os.path.join(application_path,
                               "geckodriver")  # Linux says it was checking path for geckodriver -- added here regardless

if not os.path.exists(configPath):
    with open(configPath, 'w') as f:
        f.write("NO CONTENT")
        print("NO CONTENT FOUND, GENERATED AUTOMATICALLY PATH:" + configPath)
        print("USE THE FOLLOWING ORDER IN THE DATA.txt DOCUMENT")
        print("DISCORD BOT TOKEN:")
        print("MESSAGE ID:")
        print("CHANNEL ID:")
    f.close()


class WebPageInformation:
    def __init__(self, Source, Time):
        self.WebpageSource = Source
        self.TimeInHours = Time

async def PrintWithTime(message):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"{current_time} {message}")

def Initialise(fileName):
    print("Starting...")
    global MessageID
    global token_string
    try:
        MessageID = NonAsyncReadLineFromFile(configPath, 1)
    except:
        print("Line 2 (INDEX 1) does not exist")
    try:
        token_string = NonAsyncReadLineFromFile(configPath, 0)
    except:
        print("Line 1 (INDEX 0) does not exist")
    client = discord.Client()

    # client.activity = discord.Activity(type=discord.ActivityType.watching,name="SteamSale is " + "test" + " Days away")
    @client.event
    async def on_ready():
        await PrintWithTime("OnReadyEvent")
        for guild in client.guilds:
            await PrintWithTime(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
        asyncio.get_event_loop().create_task(
            UpdateTimerLoop(18000, url="https://www.whenisthenextsteamsale.com", client=client))

    @client.event
    async def on_raw_reaction_add(payload):
        await PrintWithTime("OnReactionAddEvent")
        if payload.user_id == client.user:
            return
        # TODO load messageID from the txt file

        ### MessageID Retrieval ###
        with open(configPath) as retrieval:
            mID = retrieval.read()
            mID = mID.split("\n")
            MessageID = mID[1]
            retrieval.close()
        ###########################

        if str(payload.message_id) == str(MessageID):
            global IdExists
            IdExists = False
            if os.path.exists(pingListPath):
                with open(pingListPath, 'a') as f:
                    with open(pingListPath) as filecontents:
                        Content = str(filecontents.read())
                        Content = Content.split("\n")
                        filecontents.close()
                        for userid in Content:
                            if str(userid) == str(payload.user_id):
                                IdExists = True
                                break
                        if not IdExists:
                            f.write("\n" + str(payload.user_id))
                f.close()
            await PrintWithTime(str(payload.member))
            await payload.member.send(f"You will be pinged when the Sale begins! <@{payload.user_id}>")
            if not os.path.exists(pingListPath):
                with open(pingListPath, 'w') as f:
                    f.write(str(payload.user_id))
                f.close()
            with open(pingListPath) as g:
                content = str(g.read())
                g.close()
                content = content.split("\n")
                await PrintWithTime(content)
        # if str(payload.emoji) == "👍":
        #     await client.get_channel(payload.channel_id).send("test")




    # when a message is sent in the server
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        ProcessedResponse = str.lower(message.content.split(" ", 1)[0])
        if message.content.startswith(prefix):
            ###Test###
            if ProcessedResponse == str.lower(prefix + "Test"):
                response = "Test Received"
                await PrintWithTime(response)
                # x = threading.Thread(target=replyTimer,args=(3,message.channel))
                # x.start()
                # print("starting thread")
                # asyncio.get_event_loop().create_task(SendReactMessageAndUpdateDataConfig(3, message.channel))
                await message.channel.send("\n" + response)

            if ProcessedResponse == str.lower(prefix + "Whatis"):
                term = ""
                try:
                    term = message.content.split(" ", 1)[1]
                except:
                    await PrintWithTime("Split failed (probably contains empty) or no results were found")
                    await message.channel.send("No results found for search term:'" + term + "'")
                response = "No results found for search term: '" + term + "'"
                await PrintWithTime(term)
                url = 'https://api.urbandictionary.com/v0/define?term={}'
                r = requests.get(url.format(term))
                args = message.content
                await PrintWithTime(args)
                testing = json.dumps(r.json())
                testing = json.loads(testing)
                for thing in testing['list']:
                    await PrintWithTime(thing["definition"])
                    response = discord.Embed(title="Definition of " + term,
                                             description=thing["definition"],
                                             color=0x00ff00
                                             )
                    # response = thing["definition"]
                    break
                await message.channel.send(embed=response)
                ###STEAMSALE###
            if ProcessedResponse == str.lower(prefix + "SteamSale"):
                await PrintWithTime("Searching...")
                await message.channel.send("Searching...")
                url = "https://www.whenisthenextsteamsale.com"
                WebsiteContent = await ScrapeWebsite(url, client)
                TimeInHours = int(float(WebsiteContent.TimeInHours))
                TimeInDays = int(TimeInHours / 24)
                TimeInHours = int(TimeInHours - (TimeInDays * 24))
                response = discord.Embed(title="Next Steam sale",
                                         description=f"{TimeInDays} days {TimeInHours} hours",
                                         color=0x00ff00
                                         )
                await PrintWithTime(f"sending response: {TimeInDays}  days {TimeInHours} hours")
                await message.channel.send(embed=response)
                ###PRUNE###
            if ProcessedResponse == str.lower(prefix + "prune"):
                number = " "
                try:
                    number = message.content.split(" ", 1)[1]
                except:
                    await PrintWithTime("Invalid number provided")
                    await message.channel.send(ProcessedResponse + ":Invalid Number Provided")
                msgs = []
                number = int(number)
                async for x in message.channel.history(limit=number):
                    msgs.append(x)
                await message.channel.purge(limit=number)
                ###NOTIFYME###
            if str.lower(message.content) == str.lower(prefix + "NotifyMe"):
                await PrintWithTime("notifyme")
                url = "https://www.whenisthenextsteamsale.com"
                WebsiteInfo = await ScrapeWebsite(url, client)
                TimeInHours = int(float(WebsiteInfo.TimeInHours))
                TimeInSeconds = (TimeInHours * 60) * 60
                asyncio.get_event_loop().create_task(
                    SendReactMessageAndUpdateDataConfig(TimeInSeconds, message.channel))

    client.run(token_string)


async def ScrapeWebsite(url, client):
    await PrintWithTime("Updating Status...")
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options, executable_path=geckoDriver)
    browser.get(url)

    soup = bs(browser.page_source, "html.parser")
    subtimer = soup.find_all("p", {"id": "subTimer"})
    maintimer = soup.find_all("p", {"id": "mainTimer"})
    for item in subtimer:
        subResponse = item.text
    for item in maintimer:
        mainResponse = item.text

    TimeInHours = float(0)
    # doing this by hand cause its getting late and im getting lazy
    # print(subResponse.split(":"))  # [0] [1] [2] should always have a value in them.
    splitResponse = subResponse.split(":")
    TimeInHours += ((float(splitResponse[0])))
    TimeInHours += float(splitResponse[1]) / 60
    TimeInHours += ((float(splitResponse[2]) / 60) / 60)

    days = float(mainResponse.split("days")[0])
    if days is not 0:
        TimeInHours += days * 24
    await PrintWithTime(f"Updating Client Status {str(int(float(TimeInHours / 24)))}")
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(
        name="SteamSale in " + str(int(float(TimeInHours / 24))) + " Days"))
    relevantInformation = WebPageInformation(Source=str(browser.page_source), Time=str(int(TimeInHours)))
    browser.close()
    await WriteToFile(hoursRemainingPath, (str(TimeInHours)))
    await PrintWithTime(await ReadLineFromFile(hoursRemainingPath, 0))
    return relevantInformation


async def ReadLineFromFile(filePath, desiredLineNumber):
    with open(filePath, 'r') as file:
        data = file.read()
        file.close()
        data = data.split("\n")
        return data[desiredLineNumber]


def NonAsyncReadLineFromFile(filePath, desiredLineNumber):
    with open(filePath, 'r') as file:
        data = file.read()
        file.close()
        data = data.split("\n")
        return data[desiredLineNumber]


async def WriteToFile(filePath, contentToWrite):
    with open(filePath, 'w') as file:
        file.write(contentToWrite)
        file.close()


async def AppendSpecificFileLine(filePath, LineToChange, contentToWrite):
    with open(filePath, 'w') as file:
        data = file.read()
        file.close()
        response = ""
        data = data.split("\n")
        for i in range(LineToChange):
            if str(i) is not str(LineToChange):
                response += data[i] + "\n"
                await PrintWithTime(response)


async def SendReactMessageAndUpdateDataConfig(timer, channeltoMessage):
    # await(channeltoMessage.send("Setting timer successfully set for: " + str(int((timer / 60) / 60)) + " hours"))
    await channeltoMessage.send(content="If you'd like to get notified when the sale begins, react to this message")
    async for msg in channeltoMessage.history(limit=1):
        await PrintWithTime("New Message ID:" + str(msg.id) + "Sent by:" + str(msg.author))
    with open(configPath, 'r') as file:
        data = file.read()
        file.close()
        with open(configPath, 'w') as writeOver:
            response = data.split("\n", 1)[0] + "\n" + str(msg.id) + "\n" + str(channeltoMessage.id)
            writeOver.write(response)
            writeOver.close()


async def SetTimer(timer, channeltoMessage):
    await PrintWithTime("ALERT: Timer has been Set! " + str(timer / 3600) + " Hours remaining!")
    await asyncio.sleep(timer)
    response = "The SteamSale Has begun! "
    ###Retrieve Data from PingList###

    with open(pingListPath) as pingList:
        content = pingList.read()
        content = content.split("\n")
        pingList.close()
        for userID in content:
            await PrintWithTime(userID)
            response += f"<@{userID}>"

    #################################

    await channeltoMessage.send(response)


async def UpdateTimerLoop(FrequencyInSeconds, url, client):
    global HoursRemaining
    global Channel
    while True:
        await ScrapeWebsite(url=url, client=client)
        channelID = await ReadLineFromFile(configPath, 2)
        channelID = int(channelID)
        Channel = client.get_channel(channelID)
        # await Channel.send("UpdateTimerLoop")
        HoursRemaining = await ReadLineFromFile(hoursRemainingPath, 0)
        HoursRemaining = int(float(HoursRemaining))
        await PrintWithTime(f"UpdateTimer: Hours Remaining: {HoursRemaining}")
        # HoursRemaining = 3 # DON'T FORGET TO COMMENT OR REMOVE THIS LINE
        if HoursRemaining - int(FrequencyInSeconds / 3600) <= 0:
            break
        await PrintWithTime(f"Next update in:{int(FrequencyInSeconds / 3600)} hours")
        await asyncio.sleep(FrequencyInSeconds)
    await PrintWithTime("While Loop Broken, Attempting to Set timer")
    await SetTimer((HoursRemaining * 60) * 60, Channel)


if __name__ == '__main__':
    Initialise(configPath)
