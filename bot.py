# coding = utf-8
'''Main bot file'''
import os
import sys
import logging

from dotenv import load_dotenv

import discord
from discord.ext import tasks, commands

from bot_ext import timeupdater
from bot_ext import dankmemer
from bot_ext import valo
from bot_ext import userpolice
from bot_ext import ytsmx

logging.basicConfig(level=logging.INFO)
load_dotenv()

class MyClient(commands.Bot):
    '''discord class redefinition'''

    async def on_ready(self):
        '''executed when connected to discord'''
        logging.info(f"{self.user} has connected to Discord!")

        if len(self.guilds) == 0:
            logging.error("Alone and drunk.")
            sys.exit()

        logging.info(f"{self.guilds[0].name}: {self.guilds[0].id}; owner: {self.guilds[0].owner}")

if __name__ == '__main__':
    client = MyClient(command_prefix='/', intents=discord.Intents.all())

    client.add_cog(timeupdater.TimeUpdater(client))
    client.add_cog(dankmemer.DankMemer(client))
    client.add_cog(valo.Valo(client))
    client.add_cog(userpolice.UserPolice(client))
    client.add_cog(ytsmx.YTS(client))

    client.run(os.getenv("DISCORD_TOKEN"))
