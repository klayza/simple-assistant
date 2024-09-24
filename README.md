## *simple-assistant*
A personal assistant that can text you and run commands. For example you can have it text you whenever its your friend's birthday, or see if any of your friends posted anything recently.

## Install
1. Clone repo

`git clone https://github.com/klayza/simple-assistant`

2. Install dependencies

`pip3 install -r requirements.txt`

3. Create bot

Go create a bot here: [https://t.me/BotFather](https://t.me/BotFather) and run the command `/newbot` and it will have you give it a name.

4. Set bot token in .env

Now copy the token that BotFather gave to you and put it in the .env
Make sure to rename .env.example -> .env

5. Start it with `python main.py`


## Features
- Tools - run commands
- Scheduling - make things happen on a regular schedule
- AI - run commands via natural language


## Coming Soon
- Data driven tools
- Public tool repository?
- Note tool
- Easier scheduling


## Included Tools
- Spotify - find spotify playlists
- Quotes - get inspirational quotes



## Inspiration
[Fabric](https://github.com/danielmiessler/fabric) had the right idea for organizing tools but it was hard to setup and integrate it into my life. This app will be very easy to use and fun to program new capabilities.