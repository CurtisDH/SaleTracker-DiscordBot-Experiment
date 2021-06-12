# SaleTracker-DiscordBot-Experiment

**Usage**
create a txt file named data at the path of main.py
Line 1 should contain your bot token 
line 2 should contain the MessageID (this is to add the user to the PingList)
Line 3 Should contain the ChannelID of where the bot will send the message (Ensure the bot has permissions to send messages)
-- **WARNING** -- as of current version the bot may error if you do not fill out the following lines--
!notifyme -- command should automatically fill out Line 2 & 3 and generate the txt contents appropriately -- You may want to restart the bot after running this as the updateloop may already be one iteration behind
LINE 1 - BOT TOKEN 
LINE 2 - MESSAGEID
LINE 3 - CHANNELID
Add the bot to your discord server

**Commands**
!whatis term --urban dictionary lookup
!steamsale -- fetches when the next steam sale is
!test -- reponds *only used this to troubleshoot*
!prune (NUMBER) -- removes x amount of messages
!notifyme -- scrapes the steamsale website and creates an in app timer- also sends a message to the discord channel, which if reacted to creates a list of users to ping once the timer reaches 0


**Installed packages:** Not sure which ones are specifically needed to run the project successfully so I've listed them all

yarl
urllib3
typing-extensions
soupsieve
setuptools
selenium
requests
pip
multidict
idna
discord.py
chardet
certifi
beautifulsoup4
attrs
async-timeout
aiohttp
