# SaleTracker-DiscordBot-Experiment

**Usage**
create a txt file named data at the path of main.py
Line 1 should contain your bot token 
line 2 server name that you're connecting the bot to (this can be left blank without errors (in my limited testing))

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
