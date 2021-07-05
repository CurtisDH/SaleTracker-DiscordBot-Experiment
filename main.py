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
import youtube_dl
from youtube_search import YoutubeSearch
import asyncio

config_name = "data.txt"
pingList_name = "pingList.txt"
hoursRemaining_name = "hoursRemaining.txt"
QueuedSongs_Name = "Queue.txt"
prefix = "!"
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
QueuedSongsPath = os.path.join(application_path, QueuedSongs_Name)
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

    @client.event
    async def on_raw_reaction_add(payload):
        await PrintWithTime("OnReactionAddEvent")
        if payload.user_id == client.user:
            return

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
            #########Play#########
            if ProcessedResponse == str.lower(prefix + "Play"):
                SearchTerm = str.lower(message.content).split(f"{prefix}play", 1)[1]
                await PrintWithTime(f"{prefix}{SearchTerm}")
                if not SearchTerm:
                    await message.channel.send("No search term was provided")
                    await PrintWithTime("No search term was provided.. Returning")
                    return
                await SendRelevantPlayBackInformation(client,message,SearchTerm)

                # await PlaySong(client, url, message)
                # await message.channel.send("\n" + response)
            #########Stop#########
            if ProcessedResponse == str.lower(prefix + "Stop"):
                await PrintWithTime(f"Message:{ProcessedResponse} attempting to stop music")
                response = "Stopping Music"
                try:
                    voice_clients = client.voice_clients[0]
                    voice_clients.stop()
                    await voice_clients.disconnect()
                except:
                    response = "Error: Stop Request Failed. Am I connected to a voice channel?"
                    await PrintWithTime("Stop Request failed. Is voice_clients null?")
                await message.channel.send("\n" + response)
            #########Pause#########
            if ProcessedResponse == str.lower(prefix + "Pause"):
                response = "Pausing Music"
                try:
                    voice_clients = client.voice_clients[0]
                    voice_clients.pause()
                except:
                    response = "Error: Pause Request Failed. Am I connected to a voice channel?"
                    await PrintWithTime("Pause Request failed. Is voice_clients null?")
                await message.channel.send("\n" + response)
                #########Resume#########
            if ProcessedResponse == str.lower(prefix + "Resume"):
                await PrintWithTime(f"{prefix}Resume")
                response = "Resuming"
                try:
                    voice_clients = client.voice_clients[0]
                    voice_clients.resume()
                except:
                    response = "Error: Resume Request Failed. Am I connected to a voice channel?"
                    await PrintWithTime("Resume failed. Is voice_clients null?")
                await message.channel.send("\n" + response)
                #####Volume#######
            if ProcessedResponse == str.lower(prefix + "Volume"):
                await PrintWithTime(f"{prefix}Volume")
                await SetVolumeConfig(message=message)
                await SetVolumeOnClient(client, message)
                #####ClearQueue#######
            if ProcessedResponse == str.lower(prefix + "ClearQueue"):
                await PrintWithTime(f"{prefix}ClearQueue")
                await ClearQueue()
            ######URBAN DICTIONARY - Whatis#######
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
                    break
                if (str.lower(term) == "kyle"):
                    response = discord.Embed(title="Definition of " + term,
                                             description="kyle, the only man to hold an ultimate for the ENTIRE match",
                                             color=0xff0000
                                             )
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
                await PruneMessages(number, message)
                ###NOTIFYME###
            if str.lower(message.content) == str.lower(prefix + "NotifyMe"):
                await PrintWithTime("notifyme")
                url = "https://www.whenisthenextsteamsale.com"
                WebsiteInfo = await ScrapeWebsite(url, client)
                if WebsiteInfo is not None:
                    TimeInHours = int(float(WebsiteInfo.TimeInHours))
                    TimeInSeconds = (TimeInHours * 60) * 60
                    asyncio.get_event_loop().create_task(
                        SendReactMessageAndUpdateDataConfig(TimeInSeconds, message.channel))
                asyncio.get_event_loop().create_task(
                    UpdateTimerLoop(18000, url="https://www.whenisthenextsteamsale.com",
                                    client=client))  # Starts update loop

    client.run(token_string)


async def PruneMessages(number, message):
    msgs = []
    number = int(number)
    async for x in message.channel.history(limit=number):
        msgs.append(x)
    await message.channel.purge(limit=number)


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
    if not splitResponse[0]:  # At the 100 hourish mark the website changes how the time is displayed so it breaks
        await PrintWithTime(f"If Not SplitResponse '{splitResponse[0]}'")
        splitResponse = mainResponse.split(":")  # instead of checking the sub response we now have to check the main
        # await PrintWithTime(splitResponse[0])
        if not splitResponse[0]:  # once the sale starts no data is provided
            await PrintWithTime("Sale has started or site has gone down")
            await client.change_presence(status=discord.Status.idle, activity=discord.Game(
                name="SteamSale has started"))
            browser.close()
            return None
        await PrintWithTime(splitResponse[0])
        days = float(splitResponse[0]) / 24
        TimeInHours += float(splitResponse[0])
        TimeInHours += float(splitResponse[1]) / 60
        print(TimeInHours)
    else:
        TimeInHours += (float(splitResponse[0]))
        TimeInHours += float(splitResponse[1]) / 60
        TimeInHours += ((float(splitResponse[2]) / 60) / 60)
        days = float(mainResponse.split("days")[0])
        print(f"Days:{days}")

    if days != 0 and subResponse.split(":")[0]:
        await PrintWithTime("days != 0 & subResponse is not none")
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


async def AppendSpecificFileLine(filePath, LineToChange, contentToWrite):  ## TODO convert all .txt files into JSON
    with open(filePath, 'r') as fileR:
        data = fileR.read()
        fileR.close()
        with open(filePath, 'w') as file:
            response = ""
            data = data.split("\n")
            for i in range(LineToChange):
                if str(i) is not str(LineToChange):
                    response += data[i] + "\n"
                    await PrintWithTime(response)
                try:
                    if str(int(i + 1)) == str(LineToChange):  # + 1 because index starts at 0
                        response += contentToWrite
                except:
                    print('except')
                    response += contentToWrite
            # response += contentToWrite
            file.write(response)
            file.close()


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


async def GetChannelFromID(client):
    id = await ReadLineFromFile(configPath, 2)
    id = int(id)
    Channel = client.get_channel(id)
    return Channel


async def UpdateTimerLoop(FrequencyInSeconds, url, client):
    global HoursRemaining
    global Channel
    # await PlaySong(client,url)
    while True:
        await ScrapeWebsite(url=url, client=client)
        # channelID = await ReadLineFromFile(configPath, 2)
        # channelID = int(channelID)
        # Channel = client.get_channel(channelID)
        Channel = await GetChannelFromID(client)
        # await Channel.send("UpdateTimerLoop")
        HoursRemaining = await ReadLineFromFile(hoursRemainingPath, 0)
        HoursRemaining = int(float(HoursRemaining))
        await PrintWithTime(f"UpdateTimer: Hours Remaining: {HoursRemaining}")
        if HoursRemaining >= 24:
            FrequencyInSeconds = 24 * 3600
        if HoursRemaining - int(FrequencyInSeconds / 3600) <= 0:
            break
        await PrintWithTime(f"Next update in:{int(FrequencyInSeconds / 3600)} hours")
        await asyncio.sleep(FrequencyInSeconds)
    await PrintWithTime("While Loop Broken, Attempting to Set timer")
    await SetTimer((HoursRemaining * 60) * 60, Channel)


async def PlaySong(client, url: str, message):  # TODO Implement Spotify streaming
    song_exists = os.path.exists("song.mp3")

    if song_exists:
        await asyncio.sleep(3)
        os.remove("song.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': "song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    video_url = url
    # await ConnectToVoiceChannelFromMessage(client, message)
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except:
        print("exceptstatement")
        os.system(f"""youtube-dl -o "song.%(ext)s" --extract-audio -x --audio-format mp3 {video_url}""")
    print(client.voice_clients)
    client.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3")))
    await SetVolumeOnClient(client, message)


async def AddSongToQueue(url,response,message):
    await message.channel.send(embed=response)
    if not os.path.exists(QueuedSongsPath):
        with open(QueuedSongsPath, 'w') as f:
            f.write(f"{url}\n")
        f.close()
    else:
        with open(QueuedSongsPath, 'a') as f:
            f.write(f"{url}\n")
            f.close


async def RemoveSongFromQueue(url):
    with open(QueuedSongsPath, 'r') as readFile:
        data = readFile.read()
        data = data.split("\n")
        readFile.close()
        response = ""
        for i in data:
            print(i)
            if str(url) == str(i):
                print("Remove i?")
            else:
                response += f"{i}\n"
        print(response)
    with open(QueuedSongsPath, 'w') as file:
        file.write(response)


async def ConnectToVoiceChannelFromUserMessage(client, message):
    vc = await FindVoiceChannelFromUserMessage(client, message)
    if vc is not None:
        try:
            if client.voice_clients[0]:
                client.voice_clients[0].stop()
                await client.voice_clients[0].disconnect()
                # channel = await GetChannelFromID(message)
        except:
            await PrintWithTime("Cannot Disconnect this Client is it already disconnected?")

        await PrintWithTime(f"Attempting to connect to Voice Channel:{vc}")
        await vc.connect()
        await PrintWithTime(f"Connected to:{vc}")


async def SetVolumeConfig(message):
    try:
        floatResponse = message.content.split(" ", 1)[1]
        floatResponse = (float(int(floatResponse)) / 100)
        await AppendSpecificFileLine(configPath, 3, f"{floatResponse}")

    except:
        await PrintWithTime("Error changing Volume:: term = int(message.content.split(" ",1)[1])")
        await message.channel.send(
            f"Error: No Numerical value was entered Invalid response'{message.content.split(' ', 1)[1]}'")
        return
    await message.channel.send("Setting Volume...")
    await asyncio.sleep(1)
    await PruneMessages(2,
                        message)  # Should delete bot response & user message -> This is easily glitched tho.. #TODO BETTER METHOD


async def SetVolumeOnClient(client, message):
    try:
        volume = await ReadLineFromFile(configPath, 3)
        volume = float(volume)
        await PrintWithTime(f"Setting volume to:{volume}")
        voice_clients = client.voice_clients[0]
        voice_clients.source.volume = volume
        await PrintWithTime(f"Successfully set volume to:{volume}")
    except:
        response = "Error: Volume Change Request Failed. Am I connected to a voice channel?"
        await PrintWithTime("Volume change failed failed. Is voice_clients null?")
        await message.channel.send("\n" + response)


async def FindVoiceChannelFromUserMessage(client, message):
    channelID = await GetChannelFromID(client)
    VoiceState = message.author.voice
    try:
        print(VoiceState)
        print(VoiceState.channel)
        print(VoiceState.channel.id)
    except:
        await channelID.send("You must be connected to a voice channel")
        return None
    # print(VoiceState.id)
    # print(VoiceState.VoiceChannel_id)
    return VoiceState.channel


async def CheckIfMusicIsPlaying(client, duration, message, url):
    print(f"Duration:{duration}")
    minutes = duration.split(":", 2)[0]
    seconds = duration.split(":", 2)[1]
    await PrintWithTime(f"Waiting {minutes} Minutes {seconds} Seconds")
    minutes = float(int(minutes) * 60)
    seconds = float(int(seconds))
    totalTimeInSeconds = minutes + seconds
    client.voice_clients[0].stop()
    await asyncio.sleep(totalTimeInSeconds + 10)
    await PrintWithTime(f"Wait ended Attempting to remove song from Queue")
    await RemoveSongFromQueue(url)
    await PrintWithTime(f"Removed:{url} from queue.")
    await PrintWithTime(f"Retrieving next song..")
    NextSongURL = await GetURLFromQueue()
    if NextSongURL is not None:
        NextSongSearchTerm = NextSongURL.split("https://www.youtube.com/watch?v=")[1]
        await SendRelevantPlayBackInformation(client,message,NextSongSearchTerm)
    else:
        await message.channel.send("Queue Finished")
        client.voice_clients[0].stop()
        await client.voice_clients[0].disconnect()
        await ClearQueue()

async def SendRelevantPlayBackInformation(client, message, SearchTerm):
    print(SearchTerm)
    results = YoutubeSearch(SearchTerm, max_results=1).to_json()
    results = json.loads(results)
    videoID = results['videos'][0]['id']
    url = "https://www.youtube.com/watch?v={}"
    url = url.format(videoID)
    VidInfo = results["videos"][0]

    try:
        if client.voice_clients[0].is_playing():
            response = discord.Embed(title=f"Added: {VidInfo['title']} to queue",
                                     description=f"Duration: {VidInfo['duration']}\n"
                                                 f"https://www.youtube.com{VidInfo['url_suffix']}\n",
                                     color=0xff9900
                                     )
            await AddSongToQueue(url,response,message)
            return
    except:
        await PrintWithTime("Play: Except")
    response = discord.Embed(title="Playing: " + VidInfo['title'],
                             description=f"Duration: {VidInfo['duration']}\n"
                                         f"Views: {VidInfo['views']}\n"
                                         f"Publish Date: {VidInfo['publish_time']}\n"
                                         f"https://www.youtube.com{VidInfo['url_suffix']}\n"
                                         f"Channel: {VidInfo['channel']}",
                             color=0x00ff00
                             )
    await message.channel.send(embed=response)
    await PrintWithTime("Attempting to connect to VoiceChannel")
    await ConnectToVoiceChannelFromUserMessage(client, message)
    await PrintWithTime("Connected")
    asyncio.get_event_loop().create_task(PlaySong(client, url, message))
    asyncio.get_event_loop().create_task(
        CheckIfMusicIsPlaying(client, str(VidInfo['duration']), message, url))


async def ClearQueue():
    with open(QueuedSongsPath,'w') as f:
        f.write("\n")
        f.close()


async def GetURLFromQueue(increment=0):
    URL = await ReadLineFromFile(QueuedSongsPath, increment)
    print("NextSong"+str(URL))
    lineCount = 0
    with open(QueuedSongsPath,'r') as file:
        content = file.read()
        content = content.split("\n")
        for i in content:
            if i:
                lineCount += 1
        if increment > lineCount:
            return None

    if not URL:
        return await GetURLFromQueue(increment = increment+1)
    return URL


if __name__ == '__main__':
    Initialise(configPath)
